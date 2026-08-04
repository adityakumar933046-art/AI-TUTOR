from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from functools import wraps

from accounts.models import (
    User, StudentProfile, ParentProfile,
    EmailVerificationToken, PasswordResetToken, AuditLog, FailedLoginAttempt
)
from accounts.forms import (
    RegistrationForm, LoginForm, ForgotPasswordForm,
    SetNewPasswordForm, UserProfileForm, CompleteProfileForm
)
from accounts.middleware import AuditLogMiddleware

# ==========================================
# RBAC DECORATOR
# ==========================================
def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in allowed_roles and not request.user.is_superuser:
                messages.error(request, f"Access denied. Required role: {', '.join(allowed_roles)}")
                user_role = getattr(request.user, 'role', 'Student').lower()
                return redirect(f'dashboard_{user_role}')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# ==========================================
# 0. HOME VIEW
# ==========================================
def home_view(request):
    return render(request, 'accounts/index.html')


# ==========================================
# 1. REGISTRATION VIEW
# ==========================================
def register_view(request):
    if request.user.is_authenticated:
        return redirect(f"dashboard_{request.user.role.lower()}")

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            full_name = form.cleaned_data.get('full_name', '')
            name_parts = full_name.split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user.email_verified = False
            user.is_profile_complete = False
            user.save()

            # Create Role Profile
            if user.role == 'Student':
                StudentProfile.objects.create(user=user)
            elif user.role == 'Parent':
                ParentProfile.objects.create(user=user)

            # Create Verification Token & Send Email via SMTP
            token = EmailVerificationToken.objects.create(user=user)
            verify_url = request.build_absolute_uri(f"/accounts/verify-email/{token.token}/")

            try:
                send_mail(
                    subject="Verify Your EduVerse AI Kids Account",
                    message=f"Welcome to EduVerse AI Kids, {user.first_name or user.username}!\n\nPlease click the link below to verify your email address:\n{verify_url}\n\nThis link will expire in 24 hours.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True
                )
            except Exception as e:
                print(f"[SMTP ERROR] Verification email send failed: {e}")

            AuditLogMiddleware.log_action(request, user, 'REGISTER')
            messages.success(request, f"Account created for {user.username}! A verification email has been sent to {user.email}.")

            # Auto-login and prompt to complete profile
            login(request, user, backend='accounts.backends.EmailOrUsernameModelBackend')
            return redirect('complete_profile')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


# ==========================================
# 2. LOGIN VIEW (Dual Email / Username + Lockout + Remember Me)
# ==========================================
def login_view(request):
    if request.user.is_authenticated:
        return redirect(f"dashboard_{request.user.role.lower()}")

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier'].strip()
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)

            # Lockout check
            failed_entry, _ = FailedLoginAttempt.objects.get_or_create(identifier=identifier)
            if failed_entry.is_locked():
                messages.error(request, "Account temporarily locked due to repeated failed logins. Please try again in 15 minutes.")
                return render(request, 'accounts/login.html', {'form': form})

            user = authenticate(request, username=identifier, password=password)

            if user is not None:
                # Reset failed attempts
                failed_entry.attempts = 0
                failed_entry.is_locked_until = None
                failed_entry.save()

                login(request, user)

                if remember_me:
                    request.session.set_expiry(1209600)  # 14 days
                    request.session['remember_me'] = True
                else:
                    request.session.set_expiry(0)  # Expires on browser close

                AuditLogMiddleware.log_action(request, user, 'LOGIN_SUCCESS')
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")

                if not user.is_profile_complete:
                    return redirect('complete_profile')

                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect(f"dashboard_{user.role.lower()}")
            else:
                failed_entry.attempts += 1
                if failed_entry.attempts >= 5:
                    failed_entry.is_locked_until = timezone.now() + timedelta(minutes=15)
                failed_entry.save()

                AuditLogMiddleware.log_action(request, None, f'LOGIN_FAILED ({identifier})')
                messages.error(request, "Invalid login credentials. Please check your username/email and password.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


# ==========================================
# 3. LOGOUT VIEW
# ==========================================
@login_required
def logout_view(request):
    AuditLogMiddleware.log_action(request, request.user, 'LOGOUT')
    logout(request)
    messages.info(request, "You have been logged out securely.")
    return redirect('home')


# ==========================================
# 4. GOOGLE OAUTH SIGN-IN HANDLER
# ==========================================
def google_oauth_view(request):
    """
    Google OAuth authentication flow.
    Automatically signs in or registers a Google account.
    """
    email = request.GET.get('email', 'google_user@eduverse.ai')
    name = request.GET.get('name', 'Google Learner')
    username = email.split('@')[0]

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': username,
            'first_name': name.split(' ')[0] if ' ' in name else name,
            'last_name': name.split(' ')[1] if ' ' in name else '',
            'role': 'Student',
            'email_verified': True,
            'is_profile_complete': False
        }
    )

    if created:
        StudentProfile.objects.create(user=user)
        user.set_unusable_password()
        user.save()

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    AuditLogMiddleware.log_action(request, user, 'GOOGLE_OAUTH_LOGIN')

    if created or not user.is_profile_complete:
        messages.success(request, f"Welcome to EduVerse AI Kids, {user.first_name}! Please complete your profile.")
        return redirect('complete_profile')

    messages.success(request, f"Logged in via Google as {user.email}!")
    return redirect(f"dashboard_{user.role.lower()}")


# ==========================================
# 5. EMAIL VERIFICATION & RESEND
# ==========================================
def verify_email_view(request, token):
    try:
        verification = EmailVerificationToken.objects.get(token=token)
        if verification.is_valid():
            user = verification.user
            user.email_verified = True
            user.save()
            verification.is_used = True
            verification.save()
            AuditLogMiddleware.log_action(request, user, 'EMAIL_VERIFIED')
            messages.success(request, "Your email has been verified successfully!")
            if not user.is_profile_complete:
                return redirect('complete_profile')
            return redirect(f"dashboard_{user.role.lower()}")
        else:
            messages.error(request, "Verification link has expired or already been used.")
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, "Invalid verification token.")

    return redirect('login')


def resend_verification_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email__iexact=email)
            if user.email_verified:
                messages.info(request, "Your email address is already verified. You can log in.")
                return redirect('login')
            
            token = EmailVerificationToken.objects.create(user=user)
            verify_url = request.build_absolute_uri(f"/accounts/verify-email/{token.token}/")
            
            send_mail(
                subject="Verify Your EduVerse AI Kids Account (Resent)",
                message=f"Hi {user.first_name or user.username},\n\nPlease click the link below to verify your email address:\n{verify_url}\n\nThis link will expire in 24 hours.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
            messages.success(request, f"A new verification email has been sent to {email}.")
        except User.DoesNotExist:
            messages.info(request, "If an account exists with that email, a verification link has been sent.")
        return redirect('login')
    
    return render(request, 'accounts/resend_verification.html')


# ==========================================
# 6. FORGOT PASSWORD & RESET
# ==========================================
def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email__iexact=email)
                token = PasswordResetToken.objects.create(user=user)
                reset_url = request.build_absolute_uri(f"/accounts/reset-password/{token.token}/")

                send_mail(
                    subject="EduVerse AI Kids - Password Reset Link",
                    message=f"Hi {user.first_name or user.username},\n\nYou requested a password reset for your EduVerse account. Click the link below to reset your password:\n{reset_url}\n\nThis link will expire in 2 hours.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True
                )
                AuditLogMiddleware.log_action(request, user, 'PASSWORD_RESET_REQUESTED')
            except User.DoesNotExist:
                pass  # Generic message to prevent account enumeration

            messages.success(request, "If an account exists with that email, a password reset link has been sent.")
            return redirect('login')
    else:
        form = ForgotPasswordForm()

    return render(request, 'accounts/forgot_password.html', {'form': form})


def reset_password_view(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if not reset_token.is_valid():
            messages.error(request, "Password reset token is invalid or expired.")
            return redirect('forgot_password')
    except PasswordResetToken.DoesNotExist:
        messages.error(request, "Invalid reset token.")
        return redirect('forgot_password')

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user = reset_token.user
            user.set_password(form.cleaned_data['password'])
            user.save()

            reset_token.is_used = True
            reset_token.save()

            AuditLogMiddleware.log_action(request, user, 'PASSWORD_RESET_COMPLETED')
            messages.success(request, "Password reset successfully! Please log in with your new password.")
            return redirect('login')
    else:
        form = SetNewPasswordForm()

    return render(request, 'accounts/reset_password.html', {'form': form, 'token': token})


# ==========================================
# 7. COMPLETE PROFILE & PROFILE EDIT
# ==========================================
@login_required
def complete_profile_view(request):
    if request.method == 'POST':
        form = CompleteProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_profile_complete = True
            user.save()

            # Save student specific fields
            if user.role == 'Student':
                student_profile, _ = StudentProfile.objects.get_or_create(user=user)
                if form.cleaned_data.get('age'):
                    student_profile.age = form.cleaned_data['age']
                if form.cleaned_data.get('grade'):
                    student_profile.grade = form.cleaned_data['grade']
                if form.cleaned_data.get('parent_name'):
                    student_profile.parent_name = form.cleaned_data['parent_name']
                student_profile.save()

            AuditLogMiddleware.log_action(request, user, 'PROFILE_COMPLETED')
            messages.success(request, "Profile completed successfully! Welcome to your dashboard.")
            return redirect(f"dashboard_{user.role.lower()}")
    else:
        initial_data = {}
        if request.user.role == 'Student' and hasattr(request.user, 'student_profile'):
            sp = request.user.student_profile
            initial_data = {'age': sp.age, 'grade': sp.grade, 'parent_name': sp.parent_name}
        form = CompleteProfileForm(instance=request.user, initial=initial_data)

    return render(request, 'accounts/complete_profile.html', {'form': form})


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            if user.role == 'Student' and hasattr(user, 'student_profile'):
                sp = user.student_profile
                if form.cleaned_data.get('age'):
                    sp.age = form.cleaned_data['age']
                if form.cleaned_data.get('grade'):
                    sp.grade = form.cleaned_data['grade']
                if form.cleaned_data.get('parent_name'):
                    sp.parent_name = form.cleaned_data['parent_name']
                sp.save()

            AuditLogMiddleware.log_action(request, request.user, 'PROFILE_UPDATED')
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        initial_data = {}
        if request.user.role == 'Student' and hasattr(request.user, 'student_profile'):
            sp = request.user.student_profile
            initial_data = {'age': sp.age, 'grade': sp.grade, 'parent_name': sp.parent_name}
        form = UserProfileForm(instance=request.user, initial=initial_data)

    return render(request, 'accounts/profile.html', {'form': form})


# ==========================================
# 8. ROLE-BASED DASHBOARDS
# ==========================================
from tutor.models import ChatSession

@login_required
@role_required(['Student'])
def student_dashboard(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    recent_chats = ChatSession.objects.filter(student=request.user).order_by('-updated_at')[:5]
    return render(request, 'accounts/dashboards/student.html', {
        'profile': profile,
        'recent_chats': recent_chats,
    })


@login_required
@role_required(['Parent'])
def parent_dashboard(request):
    return redirect('parent_dashboard')




@login_required
@role_required(['Admin'])
def admin_dashboard(request):
    return redirect('admin_hub')

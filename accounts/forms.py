import re
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class RegistrationForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': 'Full Name (e.g. Alex Johnson)',
            'id': 'reg-fullname'
        })
    )
    username = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': 'Username (e.g. alex_learner)',
            'id': 'reg-username'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': 'Email address (e.g. alex@example.com)',
            'id': 'reg-email'
        })
    )
    role = forms.ChoiceField(
        choices=[('Student', 'Student 🎓'), ('Parent', 'Parent 👨‍👩‍👧')],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select rounded-pill glass-input',
            'id': 'reg-role'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': '••••••••',
            'id': 'reg-password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': '••••••••',
            'id': 'reg-confirm-password'
        })
    )
    terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must accept the Terms of Service & Privacy Policy.'}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_.]+$', username):
            raise ValidationError('Username can only contain letters, numbers, underscores, and dots.')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('This username is already taken. Please choose another.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email address already exists.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not any(char.isupper() for char in password):
            raise ValidationError('Password must contain at least one uppercase letter (A-Z).')
        if not any(char.islower() for char in password):
            raise ValidationError('Password must contain at least one lowercase letter (a-z).')
        if not any(char.isdigit() for char in password):
            raise ValidationError('Password must contain at least one digit (0-9).')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/|\\]', password):
            raise ValidationError('Password must contain at least one special character (!@#$%^&* etc).')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

        return cleaned_data


class LoginForm(forms.Form):
    identifier = forms.CharField(
        label='Username or Email',
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': 'Username or Email address',
            'id': 'login-identifier',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': '••••••••',
            'id': 'login-password',
            'autocomplete': 'current-password'
        })
    )
    remember_me = forms.BooleanField(required=False)


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': 'Enter your registered email address',
            'id': 'forgot-email'
        })
    )


class SetNewPasswordForm(forms.Form):
    password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': '••••••••',
            'id': 'reset-password'
        })
    )
    confirm_password = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': '••••••••',
            'id': 'reset-confirm-password'
        })
    )

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not any(char.isdigit() for char in password):
            raise ValidationError('Password must contain at least one digit.')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data


class CompleteProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'type': 'date',
            'id': 'profile-dob'
        })
    )
    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select rounded-pill glass-input',
            'id': 'profile-gender'
        })
    )
    language = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': 'English, Spanish, etc.',
            'id': 'profile-language'
        })
    )
    country = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': 'United States',
            'id': 'profile-country'
        })
    )
    state = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': 'California',
            'id': 'profile-state'
        })
    )
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': 'San Francisco',
            'id': 'profile-city'
        })
    )

    # Student specific profile fields
    age = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': '8',
            'id': 'profile-age'
        })
    )
    grade = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': 'Grade 3',
            'id': 'profile-grade'
        })
    )
    parent_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control rounded-pill glass-input',
            'placeholder': 'Parent / Guardian Name',
            'id': 'profile-parent-name'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'profile_picture', 'bio', 'date_of_birth', 'gender', 'language', 'country', 'state', 'city']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control rounded-pill glass-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control rounded-pill glass-input', 'placeholder': 'Last Name'}),
            'username': forms.TextInput(attrs={'class': 'form-control rounded-pill glass-input', 'placeholder': 'Username'}),
            'bio': forms.Textarea(attrs={'class': 'form-control glass-input', 'rows': 3, 'placeholder': 'Tell us a bit about yourself...'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control rounded-pill glass-input', 'id': 'profile-pic'})
        }


class UserProfileForm(CompleteProfileForm):
    pass

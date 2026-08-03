import time
from django.conf import settings
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from accounts.models import AuditLog

class InactivityTimeoutMiddleware:
    """
    Middleware that checks for session inactivity and logs out user after timeout.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check if Remember Me was selected (session.get_expiry_age() > 86400)
            is_remembered = request.session.get('remember_me', False)
            timeout = 3600 * 24 * 30 if is_remembered else 1800  # 30 days vs 30 minutes

            last_activity = request.session.get('last_activity')
            now = time.time()

            if last_activity and (now - last_activity > timeout):
                logout(request)
                messages.warning(request, 'Your session expired due to inactivity. Please log in again.')
                return redirect('login')

            request.session['last_activity'] = now

        response = self.get_response(request)
        return response


class AuditLogMiddleware:
    """
    Middleware that provides utility methods to capture client IP address and user agent.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def log_action(request, user, action):
        ip = AuditLogMiddleware.get_client_ip(request)
        ua = request.META.get('HTTP_USER_AGENT', '')
        AuditLog.objects.create(
            user=user if (user and getattr(user, 'is_authenticated', False)) else None,
            action=action,
            ip_address=ip,
            user_agent=ua
        )

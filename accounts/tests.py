from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from accounts.models import (
    StudentProfile, ParentProfile,
    EmailVerificationToken, PasswordResetToken, FailedLoginAttempt
)

User = get_user_model()

class Phase1AuthSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student_user = User.objects.create_user(
            username='student_alex',
            email='alex@eduverse.ai',
            password='Password123!',
            role='Student',
            first_name='Alex',
            last_name='Johnson',
            email_verified=True,
            is_profile_complete=True
        )
        StudentProfile.objects.create(user=self.student_user, grade='Grade 4', age=9)

        self.parent_user = User.objects.create_user(
            username='parent_mary',
            email='mary@eduverse.ai',
            password='Password123!',
            role='Parent',
            email_verified=True,
            is_profile_complete=True
        )
        ParentProfile.objects.create(user=self.parent_user)

    def test_user_creation_and_str(self):
        self.assertEqual(self.student_user.username, 'student_alex')
        self.assertEqual(self.student_user.email, 'alex@eduverse.ai')
        self.assertEqual(self.student_user.role, 'Student')
        self.assertTrue(str(self.student_user).startswith('student_alex'))

    def test_dual_login_email_and_username(self):
        # 1. Login with Username
        response_username = self.client.post(reverse('login'), {
            'identifier': 'student_alex',
            'password': 'Password123!'
        })
        self.assertEqual(response_username.status_code, 302)
        self.assertRedirects(response_username, reverse('dashboard_student'))
        self.client.logout()

        # 2. Login with Email
        response_email = self.client.post(reverse('login'), {
            'identifier': 'alex@eduverse.ai',
            'password': 'Password123!'
        })
        self.assertEqual(response_email.status_code, 302)
        self.assertRedirects(response_email, reverse('dashboard_student'))

    def test_remember_me_session(self):
        response = self.client.post(reverse('login'), {
            'identifier': 'alex@eduverse.ai',
            'password': 'Password123!',
            'remember_me': True
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get_expiry_age(), 1209600)

    def test_failed_login_lockout(self):
        for _ in range(5):
            self.client.post(reverse('login'), {
                'identifier': 'alex@eduverse.ai',
                'password': 'WrongPassword123!'
            })
        
        lockout = FailedLoginAttempt.objects.get(identifier='alex@eduverse.ai')
        self.assertTrue(lockout.is_locked())

    def test_registration_validation(self):
        # Weak password test
        response_weak = self.client.post(reverse('register'), {
            'full_name': 'Test User',
            'username': 'new_user',
            'email': 'new@eduverse.ai',
            'role': 'Student',
            'password': 'weak',
            'confirm_password': 'weak',
            'terms': True
        })
        self.assertEqual(response_weak.status_code, 200)
        self.assertFormError(response_weak.context['form'], 'password', 'Password must be at least 8 characters long.')

        # Valid registration
        response_valid = self.client.post(reverse('register'), {
            'full_name': 'New Learner',
            'username': 'new_learner',
            'email': 'learner@eduverse.ai',
            'role': 'Student',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
            'terms': True
        })
        self.assertEqual(response_valid.status_code, 302)
        self.assertTrue(User.objects.filter(username='new_learner').exists())

    def test_google_oauth_flow(self):
        response = self.client.get(reverse('google_oauth'), {
            'email': 'google_test@eduverse.ai',
            'name': 'Google Kid'
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email='google_test@eduverse.ai')
        self.assertTrue(user.email_verified)
        self.assertEqual(user.role, 'Student')

    def test_email_verification_token(self):
        user = User.objects.create_user(
            username='unverified_user',
            email='unverified@eduverse.ai',
            password='Password123!',
            email_verified=False
        )
        token = EmailVerificationToken.objects.create(user=user)
        self.assertTrue(token.is_valid())

        response = self.client.get(reverse('verify_email', kwargs={'token': token.token}))
        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertTrue(user.email_verified)

    def test_password_reset_flow(self):
        token = PasswordResetToken.objects.create(user=self.student_user)
        self.assertTrue(token.is_valid())

        response = self.client.post(reverse('reset_password', kwargs={'token': token.token}), {
            'password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.student_user.refresh_from_db()
        self.assertTrue(self.student_user.check_password('NewPassword123!'))

    def test_role_based_access_control(self):
        # Student attempting to access Parent Dashboard
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('dashboard_parent'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard_student'))

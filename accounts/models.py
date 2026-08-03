import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = (
        ('Student', 'Student'),
        ('Parent', 'Parent'),
        ('Admin', 'Admin'),
    )

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
        ('PreferNotToSay', 'Prefer not to say'),
    )

    email = models.EmailField('Email Address', unique=True)
    role = models.CharField('User Role', max_length=20, choices=ROLE_CHOICES, default='Student')
    email_verified = models.BooleanField('Email Verified', default=False)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField('Bio / Description', blank=True)
    
    date_of_birth = models.DateField('Date of Birth', null=True, blank=True)
    gender = models.CharField('Gender', max_length=20, choices=GENDER_CHOICES, null=True, blank=True)
    language = models.CharField('Preferred Language', max_length=50, default='English')
    country = models.CharField('Country', max_length=100, blank=True)
    state = models.CharField('State / Region', max_length=100, blank=True)
    city = models.CharField('City', max_length=100, blank=True)
    is_profile_complete = models.BooleanField('Profile Complete', default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.username

    def __str__(self):
        return f"{self.username} ({self.email}) — [{self.role}]"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    age = models.IntegerField(default=8)
    grade = models.CharField(max_length=50, default='Grade 3')
    parent_name = models.CharField(max_length=150, blank=True)
    xp = models.IntegerField(default=250)
    coins = models.IntegerField(default=45)
    streak_days = models.IntegerField(default=3)

    def __str__(self):
        return f"StudentProfile: {self.user.username}"


class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    phone_number = models.CharField(max_length=20, blank=True)
    screen_time_limit_minutes = models.IntegerField(default=120)

    def __str__(self):
        return f"ParentProfile: {self.user.username}"


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.action} - User: {self.user}"


class FailedLoginAttempt(models.Model):
    identifier = models.CharField(max_length=255, unique=True)
    attempts = models.IntegerField(default=1)
    last_attempt = models.DateTimeField(auto_now=True)
    is_locked_until = models.DateTimeField(null=True, blank=True)

    def is_locked(self):
        if self.is_locked_until and timezone.now() < self.is_locked_until:
            return True
        return False

    def __str__(self):
        return f"{self.identifier} ({self.attempts} attempts)"

"""
Accounts Models
Defines custom User model with roles, Voter profile, and OTP for MFA.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import random, string


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('voter', 'Voter'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='voter')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_voter(self):
        return self.role == 'voter'


class VoterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='voter_profile')
    voter_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    constituency = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    has_voted = models.BooleanField(default=False)
    is_eligible = models.BooleanField(default=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'voter_profiles'

    def __str__(self):
        return f"Voter: {self.voter_id} — {self.user.email}"


class OTPRecord(models.Model):
    PURPOSE_CHOICES = [
        ('login', 'Login Verification'),
        ('vote', 'Vote Confirmation'),
        ('reset', 'Password Reset'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES, default='login')
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'otp_records'
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP for {self.user.email} [{self.purpose}]"

    @classmethod
    def generate(cls, user, purpose='login'):
        from django.conf import settings
        from datetime import timedelta
        cls.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)
        code = ''.join(random.choices(string.digits, k=6))
        expiry = timezone.now() + timedelta(minutes=getattr(settings, 'OTP_EXPIRY_MINUTES', 10))
        return cls.objects.create(user=user, otp_code=code, purpose=purpose, expires_at=expiry)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('login_failed', 'Failed Login'),
        ('otp_sent', 'OTP Sent'),
        ('otp_verified', 'OTP Verified'),
        ('vote_cast', 'Vote Cast'),
        ('vote_attempt', 'Vote Attempt (Already Voted)'),
        ('admin_action', 'Admin Action'),
        ('election_created', 'Election Created'),
        ('election_modified', 'Election Modified'),
        ('candidate_added', 'Candidate Added'),
        ('voter_uploaded', 'Voter List Uploaded'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, blank=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.action} — {self.user}"

    @classmethod
    def log(cls, action, request=None, user=None, description=''):
        ip = None
        ua = ''
        session_key = ''
        if request:
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
            ua = request.META.get('HTTP_USER_AGENT', '')[:500]
            session_key = request.session.session_key or ''
            if not user and request.user.is_authenticated:
                user = request.user
        return cls.objects.create(
            user=user, action=action, description=description,
            ip_address=ip or None, user_agent=ua, session_key=session_key,
        )

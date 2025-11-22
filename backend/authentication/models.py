from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from datetime import timedelta


class UserManager(BaseUserManager):
    """Custom manager for User model with login_id as the unique identifier."""
    
    def create_user(self, login_id, email, password=None, **extra_fields):
        """Create and save a regular user with the given login_id, email and password."""
        if not login_id:
            raise ValueError('The Login ID must be set')
        if not email:
            raise ValueError('The Email must be set')
        
        email = self.normalize_email(email)
        user = self.model(login_id=login_id, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, login_id, email, password=None, **extra_fields):
        """Create and save a superuser with the given login_id, email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(login_id, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with login_id as the unique identifier.
    
    Requirements:
    - 1.1: Login ID must be 6-12 alphanumeric characters
    - 1.2: Login ID must be unique
    - 1.3: Email must be unique
    """
    login_id = models.CharField(
        max_length=12,
        unique=True,
        db_index=True,
        help_text='Unique login identifier (6-12 alphanumeric characters)'
    )
    email = models.EmailField(
        unique=True,
        db_index=True,
        help_text='Unique email address'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'login_id'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.login_id


class PasswordResetOTP(models.Model):
    """
    Model to store OTP codes for password reset functionality.
    
    Requirements:
    - 3.1: Generate unique OTP code
    - 3.3: Set expiration time for OTP
    - 3.5: Store OTP securely in database
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_otps'
    )
    otp_code = models.CharField(
        max_length=6,
        help_text='6-digit OTP code'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text='OTP expiration timestamp (10 minutes from creation)'
    )
    is_used = models.BooleanField(
        default=False,
        help_text='Flag to track if OTP has been used'
    )
    
    class Meta:
        db_table = 'password_reset_otps'
        verbose_name = 'Password Reset OTP'
        verbose_name_plural = 'Password Reset OTPs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.user.login_id} - {self.otp_code}"
    
    def is_expired(self):
        """Check if the OTP has expired."""
        return timezone.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        """Override save to set expiration time if not set."""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

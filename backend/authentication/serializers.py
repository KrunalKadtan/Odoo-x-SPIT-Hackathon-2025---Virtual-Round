"""
Serializers for authentication endpoints.

This module contains DRF serializers for user registration, login,
and password reset functionality.
"""

import re
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration (signup).
    
    Requirements:
    - 1.1: Validate login_id (6-12 alphanumeric characters)
    - 1.2: Validate login_id uniqueness
    - 1.3: Validate email uniqueness
    - 1.4: Validate password complexity (8+ chars, 1 uppercase, 1 special)
    - 1.5: Hash password before storage
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['id', 'login_id', 'email', 'password', 'date_joined']
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'login_id': {'required': True},
            'email': {'required': True},
        }
    
    def validate_login_id(self, value):
        """
        Validate login_id format and uniqueness.
        
        Requirement 1.1: Login ID must be 6-12 alphanumeric characters
        Requirement 1.2: Login ID must be unique
        """
        # Check length
        if len(value) < 6 or len(value) > 12:
            raise serializers.ValidationError(
                "Login ID must be between 6 and 12 characters long"
            )
        
        # Check alphanumeric only
        if not re.match(r'^[a-zA-Z0-9]+$', value):
            raise serializers.ValidationError(
                "Login ID must contain only alphanumeric characters"
            )
        
        # Check uniqueness
        if User.objects.filter(login_id=value).exists():
            raise serializers.ValidationError(
                "Login ID already exists"
            )
        
        return value
    
    def validate_email(self, value):
        """
        Validate email uniqueness.
        
        Requirement 1.3: Email must be unique
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Email already exists"
            )
        
        return value
    
    def validate_password(self, value):
        """
        Validate password complexity.
        
        Requirement 1.4: Password must contain at least 8 characters,
        1 uppercase letter, and 1 special character
        """
        # Check minimum length
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long"
            )
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError(
                "Password must contain at least 1 uppercase letter"
            )
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError(
                "Password must contain at least 1 special character"
            )
        
        # Run Django's built-in password validators
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        return value
    
    def create(self, validated_data):
        """
        Create a new user with hashed password.
        
        Requirement 1.5: Hash password using Argon2 or PBKDF2 before storage
        """
        password = validated_data.pop('password')
        user = User.objects.create_user(
            login_id=validated_data['login_id'],
            email=validated_data['email'],
            password=password
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login (authentication).
    
    Requirements:
    - 2.1: Authenticate user using login_id and password
    - 2.5: Compare submitted passwords against stored hashes
    """
    login_id = serializers.CharField(
        required=True,
        max_length=12,
        help_text='User login identifier'
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='User password'
    )
    
    def validate(self, attrs):
        """
        Validate user credentials using Django's authenticate().
        
        Requirement 2.1: Authenticate the user using provided login_id and password
        Requirement 2.5: Compare submitted passwords against stored hashes
        """
        login_id = attrs.get('login_id')
        password = attrs.get('password')
        
        if login_id and password:
            # Use Django's authenticate() to verify credentials
            # This automatically handles password hash comparison
            user = authenticate(
                request=self.context.get('request'),
                username=login_id,
                password=password
            )
            
            if user is None:
                # Generic error message to prevent credential enumeration
                raise serializers.ValidationError(
                    'Invalid credentials',
                    code='authentication'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled',
                    code='authentication'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Must include "login_id" and "password"',
                code='authentication'
            )



class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    
    Requirements:
    - 3.4: Return generic success message to prevent email enumeration
    - 3.5: Store OTP securely in database
    
    This serializer accepts an email address and initiates the password
    reset process by generating and sending an OTP.
    """
    email = serializers.EmailField(
        required=True,
        help_text='Email address associated with the account'
    )
    
    def validate_email(self, value):
        """
        Validate email format.
        
        Note: We don't validate if the email exists in the database here
        to prevent email enumeration attacks. The view will handle this.
        """
        return value.lower()
    
    def save(self):
        """
        Generate and send OTP for password reset.
        
        Requirements:
        - 3.4: Return generic success message regardless of email existence
        - 3.5: Store OTP in database
        
        Returns:
            dict: Always returns success message to prevent email enumeration
        """
        from .utils import generate_otp, send_otp_email
        
        email = self.validated_data['email']
        
        try:
            # Try to find user by email
            user = User.objects.get(email=email)
            
            # Generate OTP
            otp_instance = generate_otp(user)
            
            # Send OTP via email
            send_otp_email(user, otp_instance.otp_code)
            
        except User.DoesNotExist:
            # Don't reveal that the email doesn't exist
            # This prevents email enumeration attacks
            pass
        
        # Always return generic success message (Requirement 3.4)
        return {
            'message': 'If the email exists, an OTP has been sent'
        }


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    
    Requirements:
    - 4.1: Validate OTP matches stored code
    - 4.2: Validate OTP has not expired
    - 4.3: Validate new password meets complexity requirements
    
    This serializer accepts email, OTP code, and new password to complete
    the password reset process.
    """
    email = serializers.EmailField(
        required=True,
        help_text='Email address associated with the account'
    )
    otp_code = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        help_text='6-digit OTP code received via email'
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='New password for the account'
    )
    
    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.lower()
    
    def validate_otp_code(self, value):
        """Validate OTP code format (6 digits)."""
        if not value.isdigit():
            raise serializers.ValidationError(
                "OTP code must contain only digits"
            )
        return value
    
    def validate_new_password(self, value):
        """
        Validate new password complexity.
        
        Requirement 4.3: New password must meet complexity requirements
        (8+ chars, 1 uppercase, 1 special character)
        """
        # Check minimum length
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long"
            )
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError(
                "Password must contain at least 1 uppercase letter"
            )
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError(
                "Password must contain at least 1 special character"
            )
        
        # Run Django's built-in password validators
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        return value
    
    def validate(self, attrs):
        """
        Validate OTP against stored code and expiration.
        
        Requirements:
        - 4.1: Validate OTP matches stored code
        - 4.2: Validate OTP has not expired
        """
        from .models import PasswordResetOTP
        from django.utils import timezone
        
        email = attrs.get('email')
        otp_code = attrs.get('otp_code')
        
        try:
            # Find user by email
            user = User.objects.get(email=email)
            
            # Find the most recent unused OTP for this user
            otp_instance = PasswordResetOTP.objects.filter(
                user=user,
                otp_code=otp_code,
                is_used=False
            ).order_by('-created_at').first()
            
            if not otp_instance:
                # Requirement 4.1: OTP doesn't match stored code
                raise serializers.ValidationError(
                    "Invalid or expired OTP",
                    code='invalid_otp'
                )
            
            # Requirement 4.2: Check if OTP has expired
            if otp_instance.is_expired():
                raise serializers.ValidationError(
                    "Invalid or expired OTP",
                    code='expired_otp'
                )
            
            # Store user and otp_instance for use in save()
            attrs['user'] = user
            attrs['otp_instance'] = otp_instance
            
        except User.DoesNotExist:
            # User with this email doesn't exist
            raise serializers.ValidationError(
                "Invalid or expired OTP",
                code='invalid_email'
            )
        
        return attrs
    
    def save(self):
        """
        Update user password and mark OTP as used.
        
        Requirements:
        - 4.4: Hash new password before updating user
        - 4.5: Mark OTP as used after successful reset
        - 4.6: Generate and return new JWT tokens
        
        Returns:
            dict: Response data with tokens and success message
        """
        user = self.validated_data['user']
        otp_instance = self.validated_data['otp_instance']
        new_password = self.validated_data['new_password']
        
        # Requirement 4.4: Hash new password before updating
        user.set_password(new_password)
        user.save()
        
        # Requirement 4.5: Mark OTP as used
        otp_instance.is_used = True
        otp_instance.save()
        
        # Requirement 4.6: Generate JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        return {
            'message': 'Password reset successful',
            'access_token': access_token,
            'refresh_token': refresh_token
        }

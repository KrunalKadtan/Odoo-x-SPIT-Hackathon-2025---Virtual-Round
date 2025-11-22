"""
API views for authentication endpoints.

This module contains DRF views for user registration, login,
and password reset functionality.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import SignUpSerializer, LoginSerializer

User = get_user_model()


class SignUpView(APIView):
    """
    API endpoint for user registration (signup).
    
    POST /api/auth/signup/
    
    Requirements:
    - 1.6: Return JWT tokens upon successful registration
    
    Request Body:
    {
        "login_id": "user123",
        "email": "user@example.com",
        "password": "SecurePass@123"
    }
    
    Response (201 Created):
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "user": {
            "id": 1,
            "login_id": "user123",
            "email": "user@example.com",
            "date_joined": "2025-11-22T10:30:00Z"
        }
    }
    
    Response (400 Bad Request):
    {
        "error": "Validation failed",
        "details": {
            "login_id": ["Login ID must be 6-12 alphanumeric characters"],
            "password": ["Password must contain at least 1 uppercase letter"]
        }
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle user registration."""
        serializer = SignUpSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create the user
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Prepare response data
            response_data = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'login_id': user.login_id,
                    'email': user.email,
                    'date_joined': user.date_joined.isoformat()
                }
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        # Handle validation errors
        return Response(
            {
                'error': 'Validation failed',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    """
    API endpoint for user login (authentication).
    
    POST /api/auth/login/
    
    Requirements:
    - 2.2: Generate new access token on successful authentication
    - 2.3: Generate new refresh token on successful authentication
    - 2.4: Return generic error message on authentication failure
    
    Request Body:
    {
        "login_id": "user123",
        "password": "SecurePass@123"
    }
    
    Response (200 OK):
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "user": {
            "id": 1,
            "login_id": "user123",
            "email": "user@example.com"
        }
    }
    
    Response (401 Unauthorized):
    {
        "error": "Invalid credentials"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle user login."""
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # Get authenticated user from serializer
            user = serializer.validated_data['user']
            
            # Generate JWT tokens (Requirements 2.2, 2.3)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Prepare response data
            response_data = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'login_id': user.login_id,
                    'email': user.email
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        # Handle authentication errors (Requirement 2.4)
        # Return generic error message to prevent credential enumeration
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )



class PasswordResetRequestView(APIView):
    """
    API endpoint for password reset request.
    
    POST /api/auth/password-reset/request/
    
    Requirements:
    - 3.4: Return generic success message to prevent email enumeration
    - 3.5: Store OTP securely in database
    
    Request Body:
    {
        "email": "user@example.com"
    }
    
    Response (200 OK):
    {
        "message": "If the email exists, an OTP has been sent"
    }
    
    Note: Always returns 200 OK with generic message to prevent
    email enumeration attacks, regardless of whether the email exists.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle password reset request."""
        from .serializers import PasswordResetRequestSerializer
        
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            # Generate and send OTP
            result = serializer.save()
            
            # Always return generic success message (Requirement 3.4)
            return Response(result, status=status.HTTP_200_OK)
        
        # Handle validation errors
        return Response(
            {
                'error': 'Validation failed',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )



class PasswordResetConfirmView(APIView):
    """
    API endpoint for password reset confirmation.
    
    POST /api/auth/password-reset/confirm/
    
    Requirements:
    - 4.4: Hash new password before updating user
    - 4.5: Mark OTP as used after successful reset
    - 4.6: Generate and return new JWT tokens
    
    Request Body:
    {
        "email": "user@example.com",
        "otp_code": "123456",
        "new_password": "NewSecure@456"
    }
    
    Response (200 OK):
    {
        "message": "Password reset successful",
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    
    Response (400 Bad Request):
    {
        "error": "Invalid or expired OTP"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle password reset confirmation."""
        from .serializers import PasswordResetConfirmSerializer
        
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            # Update password, mark OTP as used, and generate tokens
            result = serializer.save()
            
            return Response(result, status=status.HTTP_200_OK)
        
        # Handle validation errors
        return Response(
            {
                'error': 'Validation failed',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

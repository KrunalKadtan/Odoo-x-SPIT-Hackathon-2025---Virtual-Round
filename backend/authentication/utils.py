"""
Utility functions for authentication module.

This module contains helper functions for OTP generation,
email sending, and other authentication-related utilities.
"""

import random
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import PasswordResetOTP

User = get_user_model()


def generate_otp(user):
    """
    Generate a random 6-digit OTP code for password reset.
    
    Requirements:
    - 3.1: Generate unique OTP code
    - 3.3: Set expiration time for OTP (10 minutes)
    
    Args:
        user: User instance for whom the OTP is being generated
    
    Returns:
        PasswordResetOTP: The created OTP instance
    """
    # Generate random 6-digit OTP code
    otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # Set expiration time to 10 minutes from now
    expires_at = timezone.now() + timedelta(minutes=10)
    
    # Create and store OTP in database
    otp_instance = PasswordResetOTP.objects.create(
        user=user,
        otp_code=otp_code,
        expires_at=expires_at
    )
    
    return otp_instance



def send_otp_email(user, otp_code):
    """
    Send OTP code to user's email address for password reset.
    
    Requirement 3.2: Send OTP code to registered email address
    
    Args:
        user: User instance to send the email to
        otp_code: The 6-digit OTP code to send
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    from django.core.mail import send_mail
    from django.conf import settings
    
    subject = 'StockMaster - Password Reset OTP'
    
    # Email message with OTP
    message = f"""
Hello {user.login_id},

You have requested to reset your password for your StockMaster account.

Your One-Time Password (OTP) is: {otp_code}

This OTP will expire in 10 minutes.

If you did not request a password reset, please ignore this email.

Best regards,
StockMaster Team
    """
    
    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .otp-code {{
            font-size: 32px;
            font-weight: bold;
            color: #2563eb;
            text-align: center;
            padding: 20px;
            background-color: #f3f4f6;
            border-radius: 8px;
            margin: 20px 0;
            letter-spacing: 4px;
        }}
        .warning {{
            color: #dc2626;
            font-size: 14px;
            margin-top: 20px;
        }}
        .footer {{
            margin-top: 30px;
            font-size: 12px;
            color: #6b7280;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Password Reset Request</h2>
        <p>Hello <strong>{user.login_id}</strong>,</p>
        <p>You have requested to reset your password for your StockMaster account.</p>
        
        <p>Your One-Time Password (OTP) is:</p>
        <div class="otp-code">{otp_code}</div>
        
        <p class="warning">⚠️ This OTP will expire in 10 minutes.</p>
        
        <p>If you did not request a password reset, please ignore this email.</p>
        
        <div class="footer">
            <p>Best regards,<br>StockMaster Team</p>
        </div>
    </div>
</body>
</html>
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error sending email: {e}")
        return False

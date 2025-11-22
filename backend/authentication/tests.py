from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import PasswordResetOTP

User = get_user_model()


class SignUpEndpointTests(APITestCase):
    """
    Integration tests for signup endpoint.
    
    Requirements tested:
    - 1.1: Login ID validation (6-12 alphanumeric characters)
    - 1.2: Login ID uniqueness
    - 1.3: Email uniqueness
    - 1.4: Password complexity validation
    """
    
    def setUp(self):
        """Set up test data."""
        self.signup_url = '/api/auth/signup/'
        self.valid_data = {
            'login_id': 'user123',
            'email': 'user@example.com',
            'password': 'SecurePass@123'
        }
    
    def test_successful_registration_with_valid_data(self):
        """Test successful registration with valid data."""
        response = self.client.post(self.signup_url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['login_id'], 'user123')
        self.assertEqual(response.data['user']['email'], 'user@example.com')
        
        # Verify user was created in database
        user = User.objects.get(login_id='user123')
        self.assertEqual(user.email, 'user@example.com')
        self.assertTrue(user.check_password('SecurePass@123'))
    
    def test_validation_error_for_short_login_id(self):
        """Test validation error for login_id shorter than 6 characters."""
        data = self.valid_data.copy()
        data['login_id'] = 'usr12'  # Only 5 characters
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('login_id', response.data['details'])
    
    def test_validation_error_for_long_login_id(self):
        """Test validation error for login_id longer than 12 characters."""
        data = self.valid_data.copy()
        data['login_id'] = 'user1234567890'  # 14 characters
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('login_id', response.data['details'])
    
    def test_validation_error_for_non_alphanumeric_login_id(self):
        """Test validation error for login_id with special characters."""
        data = self.valid_data.copy()
        data['login_id'] = 'user@123'  # Contains special character
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('login_id', response.data['details'])
    
    def test_uniqueness_constraint_for_login_id(self):
        """Test uniqueness constraint for login_id (Requirement 1.2)."""
        # Create first user
        User.objects.create_user(
            login_id='user123',
            email='first@example.com',
            password='SecurePass@123'
        )
        
        # Try to create second user with same login_id
        data = self.valid_data.copy()
        data['email'] = 'second@example.com'  # Different email
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('login_id', response.data['details'])
    
    def test_uniqueness_constraint_for_email(self):
        """Test uniqueness constraint for email (Requirement 1.3)."""
        # Create first user
        User.objects.create_user(
            login_id='user123',
            email='user@example.com',
            password='SecurePass@123'
        )
        
        # Try to create second user with same email
        data = self.valid_data.copy()
        data['login_id'] = 'user456'  # Different login_id
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('email', response.data['details'])
    
    def test_password_complexity_validation_short_password(self):
        """Test password validation for passwords shorter than 8 characters."""
        data = self.valid_data.copy()
        data['password'] = 'Pass@1'  # Only 6 characters
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('password', response.data['details'])
    
    def test_password_complexity_validation_no_uppercase(self):
        """Test password validation for passwords without uppercase letter."""
        data = self.valid_data.copy()
        data['password'] = 'securepass@123'  # No uppercase
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('password', response.data['details'])
    
    def test_password_complexity_validation_no_special_char(self):
        """Test password validation for passwords without special character."""
        data = self.valid_data.copy()
        data['password'] = 'SecurePass123'  # No special character
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('password', response.data['details'])


class LoginEndpointTests(APITestCase):
    """
    Integration tests for login endpoint.
    
    Requirements tested:
    - 2.1: Authenticate user using login_id and password
    - 2.2: Generate new access token on success
    - 2.3: Generate new refresh token on success
    - 2.4: Return generic error message on failure
    """
    
    def setUp(self):
        """Set up test data."""
        self.login_url = '/api/auth/login/'
        self.user = User.objects.create_user(
            login_id='testuser',
            email='test@example.com',
            password='TestPass@123'
        )
    
    def test_successful_login_with_correct_credentials(self):
        """Test successful login with correct credentials (Requirements 2.1, 2.2, 2.3)."""
        data = {
            'login_id': 'testuser',
            'password': 'TestPass@123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['login_id'], 'testuser')
        self.assertEqual(response.data['user']['email'], 'test@example.com')
    
    def test_failed_login_with_incorrect_password(self):
        """Test failed login with incorrect password (Requirement 2.4)."""
        data = {
            'login_id': 'testuser',
            'password': 'WrongPass@123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid credentials')
    
    def test_failed_login_with_nonexistent_login_id(self):
        """Test failed login with non-existent login_id (Requirement 2.4)."""
        data = {
            'login_id': 'nonexistent',
            'password': 'TestPass@123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid credentials')
    
    def test_jwt_tokens_are_returned(self):
        """Verify JWT tokens are returned on successful login."""
        data = {
            'login_id': 'testuser',
            'password': 'TestPass@123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify tokens are strings and not empty
        self.assertIsInstance(response.data['access_token'], str)
        self.assertIsInstance(response.data['refresh_token'], str)
        self.assertGreater(len(response.data['access_token']), 0)
        self.assertGreater(len(response.data['refresh_token']), 0)


class PasswordResetFlowTests(APITestCase):
    """
    Integration tests for password reset flow.
    
    Requirements tested:
    - 3.1: Generate unique OTP code
    - 3.2: Send OTP via email
    - 3.3: Set expiration time for OTP
    - 3.4: Return generic success message
    - 4.1: Validate OTP matches stored code
    - 4.2: Validate OTP has not expired
    - 4.5: Mark OTP as used after successful reset
    """
    
    def setUp(self):
        """Set up test data."""
        self.reset_request_url = '/api/auth/password-reset/request/'
        self.reset_confirm_url = '/api/auth/password-reset/confirm/'
        self.user = User.objects.create_user(
            login_id='resetuser',
            email='reset@example.com',
            password='OldPass@123'
        )
    
    def test_otp_request_with_valid_email(self):
        """Test OTP request with valid email (Requirements 3.1, 3.2, 3.3)."""
        data = {'email': 'reset@example.com'}
        
        response = self.client.post(self.reset_request_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify OTP was created in database
        otp = PasswordResetOTP.objects.filter(user=self.user).first()
        self.assertIsNotNone(otp)
        self.assertEqual(len(otp.otp_code), 6)
        self.assertTrue(otp.otp_code.isdigit())
        self.assertFalse(otp.is_used)
        
        # Verify expiration time is set (approximately 10 minutes from now)
        time_diff = otp.expires_at - timezone.now()
        self.assertGreater(time_diff.total_seconds(), 590)  # At least 9:50
        self.assertLess(time_diff.total_seconds(), 610)  # At most 10:10
    
    def test_otp_request_with_invalid_email(self):
        """Test OTP request with invalid email (Requirement 3.4)."""
        data = {'email': 'nonexistent@example.com'}
        
        response = self.client.post(self.reset_request_url, data, format='json')
        
        # Should return success message to prevent email enumeration
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(
            response.data['message'],
            'If the email exists, an OTP has been sent'
        )
    
    def test_password_reset_with_valid_otp(self):
        """Test password reset with valid OTP (Requirements 4.1, 4.5)."""
        # Create OTP
        otp = PasswordResetOTP.objects.create(
            user=self.user,
            otp_code='123456',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        data = {
            'email': 'reset@example.com',
            'otp_code': '123456',
            'new_password': 'NewPass@456'
        }
        
        response = self.client.post(self.reset_confirm_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        
        # Verify password was updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass@456'))
        
        # Verify OTP was marked as used (Requirement 4.5)
        otp.refresh_from_db()
        self.assertTrue(otp.is_used)
    
    def test_password_reset_with_expired_otp(self):
        """Test password reset with expired OTP (Requirement 4.2)."""
        # Create expired OTP
        otp = PasswordResetOTP.objects.create(
            user=self.user,
            otp_code='123456',
            expires_at=timezone.now() - timedelta(minutes=1)  # Expired 1 minute ago
        )
        
        data = {
            'email': 'reset@example.com',
            'otp_code': '123456',
            'new_password': 'NewPass@456'
        }
        
        response = self.client.post(self.reset_confirm_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
        # Verify password was NOT updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('OldPass@123'))
    
    def test_password_reset_with_invalid_otp(self):
        """Test password reset with invalid OTP (Requirement 4.1)."""
        # Create OTP with different code
        otp = PasswordResetOTP.objects.create(
            user=self.user,
            otp_code='123456',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        data = {
            'email': 'reset@example.com',
            'otp_code': '999999',  # Wrong OTP
            'new_password': 'NewPass@456'
        }
        
        response = self.client.post(self.reset_confirm_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
        # Verify password was NOT updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('OldPass@123'))
    
    def test_password_reset_with_used_otp(self):
        """Test password reset with already used OTP."""
        # Create used OTP
        otp = PasswordResetOTP.objects.create(
            user=self.user,
            otp_code='123456',
            expires_at=timezone.now() + timedelta(minutes=10),
            is_used=True  # Already used
        )
        
        data = {
            'email': 'reset@example.com',
            'otp_code': '123456',
            'new_password': 'NewPass@456'
        }
        
        response = self.client.post(self.reset_confirm_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
        # Verify password was NOT updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('OldPass@123'))

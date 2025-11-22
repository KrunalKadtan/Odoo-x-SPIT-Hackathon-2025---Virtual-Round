# Implementation Plan

- [x] 1. Set up Django project and PostgreSQL configuration





  - Create Django project 'stockmaster' in backend directory
  - Configure PostgreSQL database connection in settings.py
  - Update requirements.txt with all necessary dependencies
  - Configure environment variables for sensitive data
  - _Requirements: 5.5_

- [ ] 2. Create custom User model and authentication app
  - Create 'authentication' Django app
  - Implement custom User model with login_id field extending AbstractBaseUser
  - Create PasswordResetOTP model for OTP storage
  - Configure AUTH_USER_MODEL in settings.py
  - Create and run database migrations
  - _Requirements: 1.1, 1.2, 1.3, 3.5_

- [ ] 3. Configure password hashing and JWT authentication
  - Configure Argon2 password hasher in settings.py
  - Install and configure djangorestframework-simplejwt
  - Set JWT token lifetimes (15 min access, 7 days refresh)
  - Configure REST framework authentication classes
  - _Requirements: 5.1, 5.2, 5.3, 5.5_

- [ ] 4. Implement user registration (signup) functionality
  - [ ] 4.1 Create SignUpSerializer with validation logic
    - Implement login_id validation (6-12 alphanumeric characters)
    - Implement email uniqueness validation
    - Implement password complexity validation (8+ chars, 1 uppercase, 1 special)
    - Implement password hashing in create method
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [ ] 4.2 Create SignUpView API endpoint
    - Implement POST endpoint at /api/auth/signup/
    - Generate JWT tokens upon successful registration
    - Return user data and tokens in response
    - Handle validation errors with appropriate status codes
    - _Requirements: 1.6_

- [ ] 5. Implement user login functionality
  - [ ] 5.1 Create LoginSerializer for authentication
    - Accept login_id and password fields
    - Implement authentication logic using Django's authenticate()
    - Validate credentials against hashed passwords
    - _Requirements: 2.1, 2.5_
  
  - [ ] 5.2 Create LoginView API endpoint
    - Implement POST endpoint at /api/auth/login/
    - Generate new access and refresh tokens on success
    - Return generic error message on authentication failure
    - Return user data and tokens in response
    - _Requirements: 2.2, 2.3, 2.4_

- [ ] 6. Implement password reset request functionality
  - [ ] 6.1 Create OTP generation utility function
    - Generate random 6-digit OTP code
    - Set expiration time to 10 minutes from creation
    - Store OTP in PasswordResetOTP model
    - _Requirements: 3.1, 3.3_
  
  - [ ] 6.2 Create email sending utility function
    - Configure Django email backend
    - Create email template for OTP delivery
    - Implement send_otp_email function
    - _Requirements: 3.2_
  
  - [ ] 6.3 Create PasswordResetRequestSerializer and view
    - Accept email field
    - Implement POST endpoint at /api/auth/password-reset/request/
    - Generate and send OTP for valid emails
    - Return generic success message to prevent email enumeration
    - _Requirements: 3.4, 3.5_

- [ ] 7. Implement password reset confirmation functionality
  - [ ] 7.1 Create PasswordResetConfirmSerializer with validation
    - Accept email, otp_code, and new_password fields
    - Validate OTP matches stored code
    - Validate OTP has not expired
    - Validate new password meets complexity requirements
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [ ] 7.2 Create PasswordResetConfirmView API endpoint
    - Implement POST endpoint at /api/auth/password-reset/confirm/
    - Hash new password before updating user
    - Mark OTP as used after successful reset
    - Generate and return new JWT tokens
    - _Requirements: 4.4, 4.5, 4.6_

- [ ] 8. Configure URL routing and CORS
  - Create authentication/urls.py with all endpoint routes
  - Include authentication URLs in main urls.py
  - Configure CORS headers for frontend communication
  - Add token refresh endpoint
  - _Requirements: All_

- [ ] 9. Create custom password validator
  - Implement custom validator class for password complexity
  - Check for minimum 8 characters
  - Check for at least 1 uppercase letter
  - Check for at least 1 special character
  - Add validator to PASSWORD_VALIDATORS in settings.py
  - _Requirements: 1.4, 4.3_

- [ ] 10. Write integration tests for authentication endpoints
  - [ ] 10.1 Test signup endpoint
    - Test successful registration with valid data
    - Test validation errors for invalid login_id format
    - Test uniqueness constraints for login_id and email
    - Test password complexity validation
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [ ] 10.2 Test login endpoint
    - Test successful login with correct credentials
    - Test failed login with incorrect password
    - Test failed login with non-existent login_id
    - Verify JWT tokens are returned
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [ ] 10.3 Test password reset flow
    - Test OTP request with valid email
    - Test OTP request with invalid email
    - Test password reset with valid OTP
    - Test password reset with expired OTP
    - Test password reset with invalid OTP
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.5_

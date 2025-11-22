# Design Document

## Overview

The StockMaster Authentication System is built using Django 3.2+ with Django REST Framework (DRF) and PostgreSQL. It implements JWT-based stateless authentication with secure password management using Argon2 hashing. The system provides three main API endpoints: user registration, login, and two-step password reset.

## Architecture

### Technology Stack

- **Backend Framework**: Django 3.2+ with Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens) using `djangorestframework-simplejwt`
- **Password Hashing**: Argon2 (via `django-argon2-password-hasher`)
- **Email Service**: Django's email backend (SMTP configuration)

### Project Structure

```
backend/
├── stockmaster/              # Django project root
│   ├── settings.py          # Project settings
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI application
├── authentication/           # Authentication app
│   ├── models.py            # User model with Login ID
│   ├── serializers.py       # DRF serializers for validation
│   ├── views.py             # API view classes
│   ├── urls.py              # Authentication endpoints
│   └── utils.py             # Helper functions (OTP generation, email)
├── manage.py
└── requirements.txt
```

## Components and Interfaces

### 1. Custom User Model

**File**: `authentication/models.py`

The custom User model extends Django's `AbstractBaseUser` and `PermissionsMixin`:

```python
class User(AbstractBaseUser, PermissionsMixin):
    login_id = CharField(unique=True, max_length=12)  # 6-12 alphanumeric
    email = EmailField(unique=True)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    date_joined = DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'login_id'
    REQUIRED_FIELDS = ['email']
```

**OTP Model** for password reset:

```python
class PasswordResetOTP(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    otp_code = CharField(max_length=6)
    created_at = DateTimeField(auto_now_add=True)
    expires_at = DateTimeField()
    is_used = BooleanField(default=False)
```

### 2. Serializers

**File**: `authentication/serializers.py`

**SignUpSerializer**:
- Validates Login ID (6-12 alphanumeric characters, unique)
- Validates email (unique, valid format)
- Validates password (8+ chars, 1 uppercase, 1 special char)
- Hashes password before saving

**LoginSerializer**:
- Accepts `login_id` and `password`
- Authenticates user credentials
- Returns JWT tokens on success

**PasswordResetRequestSerializer**:
- Accepts email address
- Generates 6-digit OTP
- Sends OTP via email

**PasswordResetConfirmSerializer**:
- Accepts email, OTP, and new password
- Validates OTP (correct, not expired, not used)
- Validates new password requirements
- Updates password and invalidates OTP

### 3. API Views

**File**: `authentication/views.py`

All views use DRF's `APIView` or generic views:

**SignUpView** (`POST /api/auth/signup/`):
- Input: `login_id`, `email`, `password`
- Output: `access_token`, `refresh_token`, `user` data
- Status: 201 Created on success, 400 Bad Request on validation error

**LoginView** (`POST /api/auth/login/`):
- Input: `login_id`, `password`
- Output: `access_token`, `refresh_token`, `user` data
- Status: 200 OK on success, 401 Unauthorized on failure

**PasswordResetRequestView** (`POST /api/auth/password-reset/request/`):
- Input: `email`
- Output: Success message (generic to prevent email enumeration)
- Status: 200 OK (always, even if email doesn't exist)

**PasswordResetConfirmView** (`POST /api/auth/password-reset/confirm/`):
- Input: `email`, `otp_code`, `new_password`
- Output: `access_token`, `refresh_token`, success message
- Status: 200 OK on success, 400 Bad Request on validation error

### 4. URL Configuration

**File**: `authentication/urls.py`

```python
urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
```

Include in main `urls.py`:
```python
urlpatterns = [
    path('api/auth/', include('authentication.urls')),
]
```

## Data Models

### User Model Schema

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto | Unique user identifier |
| login_id | String(12) | Unique, Not Null | User's login identifier (6-12 chars) |
| email | String(254) | Unique, Not Null | User's email address |
| password | String(128) | Not Null | Argon2 hashed password |
| is_active | Boolean | Default: True | Account active status |
| is_staff | Boolean | Default: False | Staff access flag |
| date_joined | DateTime | Auto | Account creation timestamp |

### PasswordResetOTP Model Schema

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto | Unique OTP record identifier |
| user | ForeignKey | Not Null, CASCADE | Reference to User |
| otp_code | String(6) | Not Null | 6-digit OTP code |
| created_at | DateTime | Auto | OTP generation timestamp |
| expires_at | DateTime | Not Null | OTP expiration timestamp (10 min) |
| is_used | Boolean | Default: False | OTP usage status |

## Error Handling

### Validation Errors

All validation errors return HTTP 400 with structured JSON:

```json
{
  "error": "Validation failed",
  "details": {
    "login_id": ["Login ID must be 6-12 alphanumeric characters"],
    "password": ["Password must contain at least 1 uppercase letter and 1 special character"]
  }
}
```

### Authentication Errors

Failed login returns HTTP 401:

```json
{
  "error": "Invalid credentials"
}
```

### OTP Errors

Invalid or expired OTP returns HTTP 400:

```json
{
  "error": "Invalid or expired OTP"
}
```

### Database Errors

Unique constraint violations return HTTP 400:

```json
{
  "error": "Login ID already exists"
}
```

## Security Considerations

### Password Security

1. **Hashing Algorithm**: Argon2 (recommended) or PBKDF2
2. **Django Configuration**:
   ```python
   PASSWORD_HASHERS = [
       'django.contrib.auth.hashers.Argon2PasswordHasher',
       'django.contrib.auth.hashers.PBKDF2PasswordHasher',
   ]
   ```
3. **Password Validation**: Custom validator for complexity requirements
4. **No Plain Text**: Passwords never stored or logged in plain text

### JWT Token Security

1. **Access Token**: Short-lived (15 minutes)
2. **Refresh Token**: Longer-lived (7 days)
3. **Token Storage**: Client-side (localStorage or httpOnly cookies)
4. **Token Rotation**: Refresh tokens can generate new access tokens

### OTP Security

1. **Expiration**: 10 minutes from generation
2. **Single Use**: OTP marked as used after successful reset
3. **Rate Limiting**: Prevent brute force attacks (implementation recommended)
4. **Email Enumeration Prevention**: Generic success messages

### CORS Configuration

Configure CORS for frontend communication:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
]
```

## Testing Strategy

### Unit Tests

**Test Coverage**:
1. User model validation (login_id format, email uniqueness)
2. Password hashing and verification
3. Serializer validation logic
4. OTP generation and expiration
5. Token generation

**Test Files**:
- `authentication/tests/test_models.py`
- `authentication/tests/test_serializers.py`
- `authentication/tests/test_utils.py`

### Integration Tests

**API Endpoint Tests**:
1. Signup flow with valid/invalid data
2. Login flow with correct/incorrect credentials
3. Password reset request with existing/non-existing email
4. Password reset confirmation with valid/invalid/expired OTP
5. Token refresh functionality

**Test File**:
- `authentication/tests/test_views.py`

### Test Database

Use SQLite for testing to avoid PostgreSQL dependency in CI/CD:
```python
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
```

## Configuration Requirements

### Django Settings

**Required Settings** (`stockmaster/settings.py`):

```python
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'stockmaster_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

# Password Hashers
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
DEFAULT_FROM_EMAIL = 'StockMaster <noreply@stockmaster.com>'

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
```

### Environment Variables

Store sensitive data in `.env` file:
```
DB_NAME=stockmaster_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
SECRET_KEY=your_django_secret_key
```

## Dependencies

**Updated `requirements.txt`**:
```
Django>=3.2,<4.0
djangorestframework>=3.12.0
djangorestframework-simplejwt>=5.0.0
psycopg2-binary>=2.9.0
django-cors-headers>=3.10.0
django-argon2-password-hasher>=1.4.0
python-decouple>=3.6
```

## API Response Examples

### Successful Signup

**Request**:
```json
POST /api/auth/signup/
{
  "login_id": "user123",
  "email": "user@example.com",
  "password": "SecurePass@123"
}
```

**Response** (201):
```json
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
```

### Successful Login

**Request**:
```json
POST /api/auth/login/
{
  "login_id": "user123",
  "password": "SecurePass@123"
}
```

**Response** (200):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "login_id": "user123",
    "email": "user@example.com"
  }
}
```

### Password Reset Request

**Request**:
```json
POST /api/auth/password-reset/request/
{
  "email": "user@example.com"
}
```

**Response** (200):
```json
{
  "message": "If the email exists, an OTP has been sent"
}
```

### Password Reset Confirm

**Request**:
```json
POST /api/auth/password-reset/confirm/
{
  "email": "user@example.com",
  "otp_code": "123456",
  "new_password": "NewSecure@456"
}
```

**Response** (200):
```json
{
  "message": "Password reset successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

# StockMaster Frontend

React-based frontend for the StockMaster Inventory Management System with complete authentication flow.

## Features

### Authentication System
- ✅ **User Registration (Signup)** - Create new account with validation
- ✅ **User Login** - Authenticate with login ID and password
- ✅ **Forgot Password** - Request OTP via email
- ✅ **Reset Password** - Reset password using OTP verification
- ✅ **JWT Token Management** - Automatic token refresh and storage
- ✅ **Protected Routes** - Secure dashboard access

### Tech Stack
- **React 19.2.0** - UI library
- **React Router DOM** - Client-side routing
- **Axios** - HTTP client for API calls
- **Input OTP** - OTP input component
- **React Icons** - Icon library
- **Vite** - Build tool and dev server

## Project Structure

```
src/
├── components/
│   ├── ui/
│   │   ├── Button.jsx          # Reusable button component
│   │   ├── Button.css
│   │   ├── Input.jsx           # Reusable input component
│   │   ├── Input.css
│   │   ├── Label.jsx           # Reusable label component
│   │   └── Label.css
│   └── ProtectedRoute.jsx      # Route protection wrapper
├── pages/
│   ├── LoginPage.jsx           # Login page
│   ├── LoginPage.css
│   ├── SignupPage.jsx          # Registration page
│   ├── ForgotPasswordPage.jsx  # Request password reset
│   ├── ResetPasswordPage.jsx   # Reset password with OTP
│   ├── ResetPasswordPage.css
│   ├── Dashboard.jsx           # Main dashboard
│   └── Dashboard.css
├── services/
│   └── api.js                  # API service and token management
├── App.jsx                     # Main app with routing
├── main.jsx                    # App entry point
└── index.css                   # Global styles
```

## Getting Started

### Prerequisites
- Node.js 16+ installed
- Backend server running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

## API Integration

The frontend connects to the Django backend at `http://localhost:8000/api/auth/`

### Endpoints Used:
- `POST /signup/` - User registration
- `POST /login/` - User authentication
- `POST /password-reset/request/` - Request OTP
- `POST /password-reset/confirm/` - Reset password
- `POST /token/refresh/` - Refresh JWT token

## Features Implementation

### Form Validation
- **Login ID**: 6-12 alphanumeric characters
- **Email**: Valid email format
- **Password**: Minimum 8 characters, 1 uppercase, 1 special character
- Real-time validation feedback

### Security
- JWT token storage in localStorage
- Automatic token refresh on 401 errors
- Protected routes requiring authentication
- Secure password reset flow with OTP

### User Experience
- Split-screen design with branding
- Responsive layout
- Loading states during API calls
- Error handling with user-friendly messages
- Success feedback and redirects

## Styling Approach

All components use **plain CSS** (no Tailwind) with:
- CSS custom properties for theming
- BEM-like naming conventions
- Responsive design with media queries
- Consistent spacing and colors

## Development Notes

- Uses JSX (not TSX) as per project requirements
- All React features utilized (hooks, state, props, etc.)
- Component-based architecture
- Reusable UI components
- Clean separation of concerns

## Future Enhancements

- Dashboard inventory features
- User profile management
- Settings page
- Move history tracking
- Warehouse management

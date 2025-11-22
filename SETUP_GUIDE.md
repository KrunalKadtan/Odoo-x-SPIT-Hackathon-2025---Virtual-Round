# StockMaster Setup Guide

Complete guide to run the StockMaster Inventory Management System.

## Prerequisites

- Python 3.10+
- Node.js 16+
- PostgreSQL 12+

## Backend Setup

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Activate virtual environment
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies (if not already installed)
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the backend directory with:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=stockmaster_db
DB_USER=postgres
DB_PASSWORD=your-postgres-password
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:5173
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 5. Create PostgreSQL database
```sql
CREATE DATABASE stockmaster_db;
```

### 6. Run migrations
```bash
python manage.py migrate
```

### 7. Start backend server
```bash
python manage.py runserver
```

Backend will run at: `http://localhost:8000`

---

## Frontend Setup

### 1. Navigate to frontend directory
```bash
cd frontend
```

### 2. Install dependencies (if not already installed)
```bash
npm install
```

### 3. Start development server
```bash
npm run dev
```

Frontend will run at: `http://localhost:5173`

---

## Testing the Application

### 1. Open browser
Navigate to: `http://localhost:5173`

### 2. Create an account
- Click "Sign up"
- Enter Login ID (6-12 alphanumeric characters)
- Enter valid email
- Create password (min 8 chars, 1 uppercase, 1 special character)
- Click "Sign Up"

### 3. Login
- Enter your Login ID
- Enter your password
- Click "Sign In"

### 4. Test Password Reset
- Click "Forgot password?"
- Enter your email
- Check console for OTP (since we're using console email backend)
- Enter OTP and new password
- Reset password

---

## API Endpoints

All endpoints are prefixed with `/api/auth/`

### Authentication Endpoints:
- `POST /signup/` - User registration
- `POST /login/` - User login
- `POST /password-reset/request/` - Request OTP
- `POST /password-reset/confirm/` - Reset password with OTP
- `POST /token/refresh/` - Refresh JWT token

---

## Troubleshooting

### Backend Issues

**Database connection error:**
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists

**Migration errors:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Port already in use:**
```bash
python manage.py runserver 8001
```
Update frontend API URL accordingly.

### Frontend Issues

**Module not found:**
```bash
npm install
```

**Port already in use:**
Edit `vite.config.js` to change port:
```js
export default defineConfig({
  server: {
    port: 3000
  }
})
```

**CORS errors:**
- Verify backend is running
- Check CORS_ALLOWED_ORIGINS in backend `.env`

---

## Development Notes

### Backend
- Django REST Framework for API
- JWT authentication (15 min access, 7 days refresh)
- Argon2 password hashing
- PostgreSQL database
- Custom User model with login_id

### Frontend
- React 19 with JSX
- React Router for navigation
- Axios for API calls
- Plain CSS (no Tailwind)
- JWT token management
- Protected routes

---

## Production Deployment

### Backend
1. Set `DEBUG=False` in `.env`
2. Configure production database
3. Set secure `SECRET_KEY`
4. Configure email backend (SMTP)
5. Set allowed hosts
6. Collect static files: `python manage.py collectstatic`
7. Use production WSGI server (gunicorn, uwsgi)

### Frontend
1. Build production bundle: `npm run build`
2. Serve `dist/` folder with nginx or similar
3. Update API base URL for production backend

---

## Support

For issues or questions, refer to:
- Backend README: `backend/Readme.md`
- Frontend README: `frontend/README.md`

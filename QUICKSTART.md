# Quick Start Guide

Get StockMaster up and running in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.10+ installed
- ✅ Node.js 16+ installed  
- ✅ PostgreSQL 12+ installed and running
- ✅ Git (optional)

---

## Step 1: Database Setup (2 minutes)

Open PostgreSQL and create the database:

```sql
CREATE DATABASE stockmaster_db;
```

---

## Step 2: Backend Setup (2 minutes)

### Windows:
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Linux/Mac:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Backend should now be running at:** `http://localhost:8000`

Keep this terminal open!

---

## Step 3: Frontend Setup (1 minute)

Open a **NEW terminal** window:

```bash
cd frontend
npm install
npm run dev
```

**Frontend should now be running at:** `http://localhost:5173`

---

## Step 4: Test the Application

1. Open browser: `http://localhost:5173`
2. Click **"Sign up"**
3. Create account:
   - Login ID: `testuser1` (6-12 alphanumeric)
   - Email: `test@example.com`
   - Password: `Test@1234` (8+ chars, 1 uppercase, 1 special)
   - Confirm Password: `Test@1234`
4. Click **"Sign Up"** → You'll be logged in automatically!

---

## Common Issues & Solutions

### ❌ Backend won't start

**Error:** `django.db.utils.OperationalError`
- **Solution:** Check PostgreSQL is running and database exists

**Error:** `ModuleNotFoundError`
- **Solution:** Activate virtual environment and run `pip install -r requirements.txt`

### ❌ Frontend won't start

**Error:** `Cannot find module`
- **Solution:** Run `npm install` in frontend directory

**Error:** `Port 5173 already in use`
- **Solution:** Kill the process or change port in `vite.config.js`

### ❌ CORS errors in browser

- **Solution:** Ensure backend is running on port 8000
- Check `CORS_ALLOWED_ORIGINS` in backend `.env` includes `http://localhost:5173`

### ❌ Login fails

- **Solution:** Check backend terminal for errors
- Verify database migrations ran successfully
- Try creating a new account

---

## Environment Configuration (Optional)

### Backend `.env` file:
Create `backend/.env` with:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=stockmaster_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:5173
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## Testing Password Reset

1. Click **"Forgot password?"** on login page
2. Enter your email: `test@example.com`
3. Check **backend terminal** for OTP code (6 digits)
4. Enter OTP and new password
5. Login with new password!

---

## What's Next?

✅ **You're all set!** The authentication system is fully functional.

### Explore:
- Dashboard (after login)
- User profile info
- Logout functionality

### Develop:
- Add inventory features
- Build warehouse management
- Create receipt tracking
- Implement move history

---

## Stopping the Application

### Stop Frontend:
Press `Ctrl + C` in frontend terminal

### Stop Backend:
Press `Ctrl + C` in backend terminal

### Deactivate Python Environment:
```bash
deactivate
```

---

## Need Help?

📖 **Documentation:**
- Backend: `backend/Readme.md`
- Frontend: `frontend/README.md`
- Full Setup: `SETUP_GUIDE.md`
- Implementation: `frontend/IMPLEMENTATION_NOTES.md`

🐛 **Troubleshooting:**
- Check both terminal windows for errors
- Verify PostgreSQL is running
- Ensure ports 8000 and 5173 are available
- Check browser console for frontend errors

---

## Quick Commands Reference

### Backend:
```bash
# Start server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test
```

### Frontend:
```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

---

## Success Indicators

✅ Backend running: Terminal shows "Starting development server at http://127.0.0.1:8000/"

✅ Frontend running: Terminal shows "Local: http://localhost:5173/"

✅ Database connected: No errors in backend terminal

✅ Application working: Can access login page in browser

---

**Happy coding! 🚀**

# StockMaster Backend

Django REST API backend for the StockMaster Inventory Management System.

## Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Virtual environment (already created in `venv/`)

### Installation

1. Activate the virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Update the `.env` file with your configuration:
   - Set a secure `SECRET_KEY`
   - Configure PostgreSQL database credentials
   - Configure email settings (optional for development)

5. Create the PostgreSQL database:
   ```sql
   CREATE DATABASE stockmaster_db;
   ```

6. Run migrations:
   ```bash
   python manage.py migrate
   ```

7. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

8. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
backend/
├── stockmaster/          # Django project configuration
│   ├── settings.py      # Project settings with PostgreSQL & JWT config
│   ├── urls.py          # Root URL configuration
│   ├── wsgi.py          # WSGI application
│   └── asgi.py          # ASGI application
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── .gitignore          # Git ignore rules
```

## Configuration

### Database

PostgreSQL is configured as the default database. Update these environment variables in `.env`:

- `DB_NAME`: Database name (default: stockmaster_db)
- `DB_USER`: Database user (default: postgres)
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)

### Authentication

JWT authentication is configured with:
- Access token lifetime: 15 minutes
- Refresh token lifetime: 7 days
- Password hashing: Argon2 (primary), PBKDF2 (fallback)

### CORS

CORS is configured to allow requests from the frontend (default: http://localhost:5173).
Update `CORS_ALLOWED_ORIGINS` in `.env` to add more origins.

## Development

### Running Tests

```bash
python manage.py test
```

### Checking for Issues

```bash
python manage.py check
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## API Documentation

API endpoints will be available at `/api/auth/` once the authentication app is implemented.

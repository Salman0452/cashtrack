# CashTrack - Django Cash Management System

Shop management system for tracking cash transactions, mobile wallet services, bills, and daily balance history.

## Features
- Transaction tracking (Mobile Wallet, Cash Credit, Stationary Sales)
- Bill management with due dates and bulk operations
- Daily balance history with opening/closing balances
- User authentication
- Dashboard with statistics

## Production Deployment (PythonAnywhere)

### 1. Setup on PythonAnywhere

1. **Create Account**: Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)

2. **Upload Code**:
   ```bash
   # On PythonAnywhere Bash console
   git clone YOUR_REPO_URL
   # OR upload files via Files tab
   ```

3. **Create Virtual Environment**:
   ```bash
   cd ~/django/website
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   ```bash
   # Create .env file
   cp .env.example .env
   nano .env
   ```
   
   Edit `.env`:
   ```
   SECRET_KEY=your-very-secure-random-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=yourusername.pythonanywhere.com
   STATIC_ROOT=/home/yourusername/saeedaccounts/staticfiles
   ```
   
   **IMPORTANT**: Replace `yourusername` with your actual PythonAnywhere username!

5. **Generate Secret Key**:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

6. **Setup Database**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   ```

### 2. Configure Web App

1. Go to **Web** tab on PythonAnywhere
2. Click **Add a new web app**
3. Choose **Manual configuration** (not Django wizard)
4. Select **Python 3.12**

5. **Configure WSGI file** (click on WSGI configuration file link):
   ```python
   import os
   import sys
   
   path = '/home/yourusername/saeedaccounts'
   if path not in sys.path:
       sys.path.append(path)
   
   os.environ['DJANGO_SETTINGS_MODULE'] = 'cashtrack.settings'
   
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
   
   **IMPORTANT**: Replace `yourusername` with your actual PythonAnywhere username!

6. **Set Virtual Environment**:
   - Virtualenv path: `/home/yourusername/saeedaccounts/venv`

7. **Configure Static Files**:
   - URL: `/static/`
   - Directory: `/home/yourusername/saeedaccounts/staticfiles`

8. **Reload** your web app

### 3. Access Your Site

Visit: `https://yourusername.pythonanywhere.com`

## Local Development

1. **Setup**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure**:
   ```bash
   cp .env.example .env
   # Edit .env and set DEBUG=True
   ```

3. **Run**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

4. **Access**: http://127.0.0.1:8000

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | (required in production) |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `STATIC_ROOT` | Static files directory | `./staticfiles` |

## Security Checklist

- ✅ Secret key from environment variable
- ✅ DEBUG=False in production
- ✅ ALLOWED_HOSTS configured
- ✅ WhiteNoise for static files
- ✅ Security headers enabled
- ✅ CSRF protection
- ✅ SQL injection protection (Django ORM)

## Troubleshooting

**Static files not loading:**
```bash
python manage.py collectstatic --noinput
# Reload web app on PythonAnywhere
```

**ImportError:**
```bash
# Check WSGI file path matches your username
# Ensure virtualenv path is correct
```

**Database errors:**
```bash
python manage.py migrate
```

## Tech Stack

- Django 4.2.27
- Python 3.12
- SQLite3
- Bootstrap 5
- WhiteNoise (static files)

## License

Proprietary - Shop Management System

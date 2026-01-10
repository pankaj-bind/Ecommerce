# PythonAnywhere Deployment Guide

## Pre-Deployment Checklist

### 1. Update Settings for Production

In `ecomm/settings.py`, you need to add:

```python
# Add your PythonAnywhere domain to ALLOWED_HOSTS
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com', 'www.yourusername.pythonanywhere.com']
```

## PythonAnywhere Deployment Steps

### Step 1: Create a PythonAnywhere Account
1. Go to https://www.pythonanywhere.com/
2. Create a free account (or upgrade to paid if needed)
3. Log in to your dashboard

### Step 2: Clone Your Repository
Open a Bash console from PythonAnywhere dashboard and run:

```bash
git clone https://github.com/pankaj-bind/Ecommerce.git
cd Ecommerce
```

### Step 3: Create a Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.10 ecommerce-env
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Set Up Environment Variables
Create a `.env` file in your project directory:

```bash
nano .env
```

Copy content from `.env.example` and fill in your actual values:
- SECRET_KEY: Generate a new one for production
- DEBUG: Set to False
- All API keys and credentials

Save and exit (Ctrl+X, then Y, then Enter)

### Step 6: Configure Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 7: Run Migrations
```bash
python manage.py migrate
```

### Step 8: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 9: Configure Web App on PythonAnywhere

1. Go to the **Web** tab in PythonAnywhere dashboard
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"** (not Django wizard)
4. Choose **Python 3.10**

### Step 10: Configure WSGI File

1. In the Web tab, click on the WSGI configuration file link
2. Delete all content and replace with:

```python
import os
import sys

# Add your project directory to the sys.path
project_home = '/home/yourusername/Ecommerce'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variable to tell Django where settings are
os.environ['DJANGO_SETTINGS_MODULE'] = 'ecomm.settings'

# Load environment variables from .env file
from pathlib import Path
env_path = Path(project_home) / '.env'
if env_path.exists():
    from decouple import Config, RepositoryEnv
    config = Config(RepositoryEnv(str(env_path)))

# Activate virtual environment
activate_this = '/home/yourusername/.virtualenvs/ecommerce-env/bin/activate_this.py'
exec(open(activate_this).read(), {'__file__': activate_this})

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Important**: Replace `yourusername` with your actual PythonAnywhere username!

### Step 11: Configure Virtual Environment

In the Web tab:
1. Scroll to **"Virtualenv"** section
2. Enter: `/home/yourusername/.virtualenvs/ecommerce-env`
3. Replace `yourusername` with your actual username

### Step 12: Configure Static Files

In the Web tab, under **"Static files"** section, add:

| URL | Directory |
|-----|-----------|
| /static/ | /home/yourusername/Ecommerce/staticfiles |
| /media/ | /home/yourusername/Ecommerce/public/media |

Replace `yourusername` with your actual username!

### Step 13: Reload Your Web App

Click the green **"Reload yourusername.pythonanywhere.com"** button at the top of the Web tab.

### Step 14: Test Your Application

Visit: `https://yourusername.pythonanywhere.com`

## Important Security Notes

1. **Never commit your `.env` file to GitHub!**
   - It's already in `.gitignore`
   - Always use `.env.example` as a template

2. **Generate a strong SECRET_KEY for production:**
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

3. **Set DEBUG=False in production**

4. **Use environment variables for all sensitive data**

## Troubleshooting

### Check Error Logs
In PythonAnywhere:
1. Go to Web tab
2. Scroll to "Log files" section
3. Check error.log and server.log

### Database Issues
If you need to reset the database:
```bash
cd ~/Ecommerce
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
```

### Static Files Not Loading
```bash
cd ~/Ecommerce
python manage.py collectstatic --clear --noinput
```
Then reload the web app.

### Permission Issues
```bash
chmod 644 ~/Ecommerce/db.sqlite3
```

## Updating Your Application

When you push changes to GitHub:

```bash
cd ~/Ecommerce
git pull
pip install -r requirements.txt  # If requirements changed
python manage.py migrate  # If models changed
python manage.py collectstatic --noinput  # If static files changed
```

Then reload the web app from the Web tab.

## Free Tier Limitations

PythonAnywhere free tier includes:
- One web app
- Limited CPU time
- No HTTPS for custom domains (only for .pythonanywhere.com)
- Web app sleeps after inactivity

For production use, consider upgrading to a paid plan.

## Additional Configuration

### Email Configuration
For Gmail, you need to:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password
3. Use the App Password in EMAIL_HOST_PASSWORD

### Payment Gateway (Razorpay)
- Ensure you're using test credentials during development
- Switch to live credentials only in production
- Update webhook URLs in Razorpay dashboard

### Social Authentication
Update callback URLs in:
- Facebook Developer Console
- Google Cloud Console

Use: `https://yourusername.pythonanywhere.com/accounts/...` as the callback URL

## Support

- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/
- PythonAnywhere Help: https://help.pythonanywhere.com/
- Django Documentation: https://docs.djangoproject.com/

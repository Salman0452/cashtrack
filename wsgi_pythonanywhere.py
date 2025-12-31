"""
WSGI config for PythonAnywhere deployment.

Copy this file's contents to your PythonAnywhere WSGI configuration file.
Available at: Web tab → WSGI configuration file link

IMPORTANT: Replace 'yourusername' with your actual PythonAnywhere username!
"""

import os
import sys

# Add your project directory to the sys.path
# REPLACE 'yourusername' with your PythonAnywhere username
path = '/home/yourusername/django/website'
if path not in sys.path:
    sys.path.insert(0, path)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'cashtrack.settings'

# Load the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

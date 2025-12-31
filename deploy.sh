#!/bin/bash

# Production Deployment Script for PythonAnywhere
# Run this script on PythonAnywhere after uploading your code

set -e  # Exit on error

echo "🚀 Starting deployment..."

# 1. Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# 2. Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --noinput

# 3. Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# 4. Check for configuration issues
echo "🔍 Running system checks..."
python manage.py check --deploy

echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Make sure .env file is configured with production values"
echo "2. Create superuser: python manage.py createsuperuser"
echo "3. Reload your web app on PythonAnywhere"
echo "4. Visit your site: https://yourusername.pythonanywhere.com"

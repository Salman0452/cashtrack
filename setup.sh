#!/bin/bash
# Setup script for CashTrack Django Application

echo "========================================="
echo "CashTrack - Shop Management System Setup"
echo "========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Apply migrations
echo "📦 Applying database migrations..."
python3 manage.py migrate

if [ $? -eq 0 ]; then
    echo "✅ Migrations applied successfully"
else
    echo "❌ Migration failed"
    exit 1
fi

echo ""

# Create demo user
echo "👤 Creating demo user..."
python3 manage.py create_demo_user

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "🚀 To start the server:"
echo "   python3 manage.py runserver"
echo ""
echo "🌐 Access the application at:"
echo "   http://localhost:8000/"
echo ""
echo "🔐 Login credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "⚠️  Remember to change the admin password in production!"
echo ""

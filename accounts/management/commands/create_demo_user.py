"""
Management command to create a demo user for testing the cash tracking system.

Usage:
    python manage.py create_demo_user
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Creates a demo user with predefined credentials.
    
    Security Note: This is for development/testing only.
    In production, use proper user registration or admin-created accounts.
    """
    help = 'Creates a demo user for testing the application'

    def handle(self, *args, **options):
        """Create demo user if it doesn't exist."""
        username = 'admin'
        password = 'admin123'
        email = 'admin@shop.pk'
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists!')
            )
            user = User.objects.get(username=username)
            self.stdout.write(
                self.style.SUCCESS(f'You can login with: {username} / {password}')
            )
        else:
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Shop',
                last_name='Admin'
            )
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created demo user!')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Username: {username}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Password: {password}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Email: {email}')
            )
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING('⚠️  SECURITY: Change this password in production!')
            )

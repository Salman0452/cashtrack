"""
Authentication views for the cash management system.
Handles user login and logout functionality.
"""
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.contrib import messages


class LoginView(DjangoLoginView):
    """
    Custom login view using Django's built-in authentication.
    Redirects authenticated users to dashboard.
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_invalid(self, form):
        """Show friendly error message on failed login."""
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)
    
    def form_valid(self, form):
        """Show success message on successful login."""
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)


class LogoutView(DjangoLogoutView):
    """
    Custom logout view.
    Logs out the user and redirects to login page.
    """
    def dispatch(self, request, *args, **kwargs):
        """Show logout message."""
        if request.user.is_authenticated:
            messages.info(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


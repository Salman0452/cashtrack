"""
Views for shop settings management.
"""
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from .models import ShopSettings
from .forms import ShopSettingsForm


class ShopSettingsUpdateView(LoginRequiredMixin, UpdateView):
    """View to update shop settings."""
    model = ShopSettings
    form_class = ShopSettingsForm
    template_name = 'shop_settings/settings_form.html'
    success_url = reverse_lazy('shop_settings:update')
    
    def get_object(self, queryset=None):
        """Get or create the single settings instance."""
        return ShopSettings.get_settings()
    
    def form_valid(self, form):
        messages.success(self.request, 'Settings updated successfully!')
        return super().form_valid(form)


class ShopSettingsAPIView(View):
    """API endpoint to get print costs."""
    
    def get(self, request):
        settings = ShopSettings.get_settings()
        return JsonResponse({
            'print_bw_cost': float(settings.print_bw_cost),
            'print_color_cost': float(settings.print_color_cost),
        })

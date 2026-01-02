from django.contrib import admin
from .models import ShopSettings


@admin.register(ShopSettings)
class ShopSettingsAdmin(admin.ModelAdmin):
    list_display = ['print_bw_cost', 'print_color_cost', 'updated_at']
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not ShopSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False

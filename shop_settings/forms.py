"""
Forms for shop settings.
"""
from django import forms
from .models import ShopSettings


class ShopSettingsForm(forms.ModelForm):
    """Form for updating shop settings."""
    
    class Meta:
        model = ShopSettings
        fields = ['print_bw_cost', 'print_color_cost']
        widgets = {
            'print_bw_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
            'print_color_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
        }
        labels = {
            'print_bw_cost': 'Black & White Print Cost (per page)',
            'print_color_cost': 'Color Print Cost (per page)',
        }
        help_texts = {
            'print_bw_cost': 'Cost in PKR for one page of black & white printing',
            'print_color_cost': 'Cost in PKR for one page of color printing',
        }

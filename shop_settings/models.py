"""
Shop Settings model for configuring print/copy costs and other settings.
"""
from django.db import models
from decimal import Decimal


class ShopSettings(models.Model):
    """
    Singleton model for shop-wide settings.
    Only one instance should exist.
    """
    # Print/Copy costs
    print_bw_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('5.00'),
        help_text="Cost per page for Black & White printing (PKR)"
    )
    
    print_color_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('5.00'),
        help_text="Cost per page for Color printing (PKR)"
    )
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Shop Settings'
        verbose_name_plural = 'Shop Settings'
    
    def __str__(self):
        return 'Shop Settings'
    
    def save(self, *args, **kwargs):
        """
        Ensure only one instance exists (singleton pattern).
        """
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """
        Get or create the single settings instance.
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

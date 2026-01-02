"""
URL configuration for shop settings.
"""
from django.urls import path
from . import views

app_name = 'shop_settings'

urlpatterns = [
    path('', views.ShopSettingsUpdateView.as_view(), name='update'),
    path('api/', views.ShopSettingsAPIView.as_view(), name='api'),
]

"""
URL configuration for dashboard app.
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='home'),
    path('daily-balance-history/', views.DailyBalanceHistoryView.as_view(), name='daily_balance_history'),
]

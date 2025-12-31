"""
URL configuration for transactions app.
"""
from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='list'),
    path('create/', views.TransactionCreateView.as_view(), name='create'),
    path('<int:pk>/update/', views.TransactionUpdateView.as_view(), name='update'),
    path('<int:pk>/detail/', views.TransactionDetailView.as_view(), name='detail'),
]

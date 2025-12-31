"""
URL configuration for bills app.
"""
from django.urls import path
from . import views

app_name = 'bills'

urlpatterns = [
    path('', views.BillListView.as_view(), name='list'),
    path('create/', views.BillCreateView.as_view(), name='create'),
    path('<int:pk>/', views.BillDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.BillUpdateView.as_view(), name='update'),
    path('<int:pk>/mark-paid/', views.BillMarkAsPaidView.as_view(), name='mark_paid'),
    path('bulk-mark-paid/', views.BillBulkMarkAsPaidView.as_view(), name='bulk_mark_paid'),
]

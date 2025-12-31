from django.contrib import admin
from .models import Bill


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'customer_name', 'amount', 'fee', 'due_date', 'status', 'created_at']
    list_filter = ['status', 'due_date', 'created_at']
    search_fields = ['customer_id', 'customer_name']
    readonly_fields = ['created_at', 'created_by', 'paid_at']
    date_hierarchy = 'due_date'


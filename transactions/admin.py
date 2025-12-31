"""
Admin configuration for transactions app.
Clean interface for managing shop transactions with proper filters and display.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin interface for Transaction model.
    Optimized for daily shop management with easy filtering and search.
    
    Safety Features:
    - Delete action disabled (preserves audit trail)
    - Created_by and timestamps are read-only
    - Cash_in and cash_out are auto-calculated (read-only)
    """
    
    # Disable delete action for data safety
    def has_delete_permission(self, request, obj=None):
        """
        Disable delete for all transactions.
        This ensures complete audit trail and prevents accidental data loss.
        """
        return False
    
    # Display these fields in the list view
    list_display = [
        'id',
        'created_at_formatted',
        'transaction_type_badge',
        'amount_formatted',
        'fee',
        'payment_mode',
        'cash_flow_summary',
        'created_by',
    ]
    
    # Add filters for quick filtering
    list_filter = [
        'transaction_type',
        'payment_mode',
        'created_at',
        'created_by',
    ]
    
    # Enable search by note and username
    search_fields = [
        'note',
        'created_by__username',
        'id',
    ]
    
    # Make these fields read-only (auto-calculated)
    readonly_fields = [
        'cash_in',
        'cash_out',
        'created_at',
        'updated_at',
    ]
    
    # Add date hierarchy for easy navigation
    date_hierarchy = 'created_at'
    
    # Default ordering
    ordering = ['-created_at']
    
    # Number of items per page
    list_per_page = 25
    
    # Organize fields in logical groups
    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'transaction_type',
                'amount',
                'fee',
                'payment_mode',
            )
        }),
        ('Calculated Cash Flow', {
            'fields': ('cash_in', 'cash_out'),
            'classes': ('collapse',),
            'description': 'These values are automatically calculated based on transaction type.'
        }),
        ('Additional Details', {
            'fields': ('note',)
        }),
        ('Audit Trail', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-set created_by to current user if creating new transaction."""
        if not change:  # Only on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    # Custom display methods for better readability
    
    @admin.display(description='Date & Time', ordering='created_at')
    def created_at_formatted(self, obj):
        """Display formatted date and time."""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    
    @admin.display(description='Type')
    def transaction_type_badge(self, obj):
        """Display transaction type with color coding."""
        colors = {
            'JAZZCASH_SEND': '#e74c3c',
            'EASYPAISA_SEND': '#e74c3c',
            'BILL_PAYMENT': '#e74c3c',
            'STATIONARY_SALE': '#27ae60',
            'BANK_DEPOSIT': '#e74c3c',
            'BANK_WITHDRAWAL': '#27ae60',
            'OTHER': '#95a5a6',
        }
        color = colors.get(obj.transaction_type, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_transaction_type_display()
        )
    
    @admin.display(description='Amount', ordering='amount')
    def amount_formatted(self, obj):
        """Display amount with PKR prefix and color."""
        color = '#27ae60' if obj.is_cash_in else '#e74c3c'
        symbol = '+' if obj.is_cash_in else '-'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} PKR {:,.2f}</span>',
            color,
            symbol,
            obj.amount
        )
    
    @admin.display(description='Cash Flow')
    def cash_flow_summary(self, obj):
        """Display cash in/out summary."""
        if obj.cash_in > 0:
            return format_html(
                '<span style="color: #27ae60;">↓ IN: PKR {:,.2f}</span>',
                obj.cash_in
            )
        else:
            return format_html(
                '<span style="color: #e74c3c;">↑ OUT: PKR {:,.2f}</span>',
                obj.cash_out
            )


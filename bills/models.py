"""
Bill management models for tracking customer bills.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from transactions.models import Transaction


class Bill(models.Model):
    """
    Bill model to track customer bill payments with due dates.
    Linked to transactions for payment tracking.
    """
    
    # Bill status choices
    PENDING = 'PENDING'
    PAID = 'PAID'
    OVERDUE = 'OVERDUE'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PAID, 'Paid'),
        (OVERDUE, 'Overdue'),
    ]
    
    # Bill details
    customer_id = models.CharField(
        max_length=100,
        help_text="Customer ID or reference number"
    )
    
    customer_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Customer name (optional)"
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Bill amount in PKR"
    )
    
    fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Service fee charged"
    )
    
    due_date = models.DateField(
        help_text="Bill due date"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        help_text="Current status of the bill"
    )
    
    # Payment tracking
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='bill',
        help_text="Associated transaction when bill is paid"
    )
    
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when bill was paid"
    )
    
    # Additional info
    note = models.TextField(
        blank=True,
        help_text="Additional notes or details"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='bills_created'
    )
    
    class Meta:
        ordering = ['due_date', '-created_at']
        indexes = [
            models.Index(fields=['customer_id']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Bill {self.customer_id} - PKR {self.amount} (Due: {self.due_date})"
    
    @property
    def total_amount(self):
        """Total amount including fee."""
        return self.amount + (self.fee or 0)
    
    @property
    def is_overdue(self):
        """Check if bill is overdue."""
        from django.utils import timezone
        if self.status == self.PAID:
            return False
        return timezone.now().date() > self.due_date
    
    def mark_as_paid(self, transaction):
        """Mark bill as paid and link to transaction."""
        from django.utils import timezone
        self.status = self.PAID
        self.transaction = transaction
        self.paid_at = timezone.now()
        self.save()


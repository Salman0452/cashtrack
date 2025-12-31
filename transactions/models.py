"""
Transaction model for small shop cash management system.

This model tracks all types of transactions:
- Mobile wallet services (JazzCash, EasyPaisa)
- Bill payments
- Stationary sales
- Bank operations
- Other miscellaneous transactions
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Transaction(models.Model):
    """
    Core transaction model for shop operations.
    
    Automatically calculates cash_in and cash_out based on transaction type
    to maintain accurate cash flow records.
    """
    
    # Transaction type choices - representing common shop operations
    MOBILE_WALLET_SEND = 'MOBILE_WALLET_SEND'
    MOBILE_WALLET_RECEIVE = 'MOBILE_WALLET_RECEIVE'
    CASH_CREDIT = 'CASH_CREDIT'
    STATIONARY_SALE = 'STATIONARY_SALE'
    OTHER = 'OTHER'
    
    # Keep these for backward compatibility (existing records)
    BILL_PAYMENT = 'BILL_PAYMENT'
    BANK_DEPOSIT = 'BANK_DEPOSIT'
    BANK_WITHDRAWAL = 'BANK_WITHDRAWAL'
    
    TRANSACTION_TYPE_CHOICES = [
        (MOBILE_WALLET_SEND, 'JazzCash/EasyPaisa Send'),
        (MOBILE_WALLET_RECEIVE, 'JazzCash/EasyPaisa Receive'),
        (CASH_CREDIT, 'Cash Credit (Load Balance)'),
        (STATIONARY_SALE, 'Stationary Sale'),
        (OTHER, 'Other'),
        # Hidden from forms but valid for programmatic creation (bills system)
        (BILL_PAYMENT, 'Bill Payment'),
        (BANK_DEPOSIT, 'Bank Deposit'),
        (BANK_WITHDRAWAL, 'Bank Withdrawal'),
    ]
    
    # Payment mode choices
    CASH = 'CASH'
    JAZZCASH = 'JAZZCASH'
    EASYPAISA = 'EASYPAISA'
    BANK = 'BANK'
    
    PAYMENT_MODE_CHOICES = [
        (CASH, 'Cash'),
        (JAZZCASH, 'JazzCash'),
        (EASYPAISA, 'EasyPaisa'),
        (BANK, 'Bank'),
    ]
    
    # Core transaction fields
    transaction_type = models.CharField(
        max_length=30,
        choices=TRANSACTION_TYPE_CHOICES,
        help_text="Type of transaction"
    )
    
    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODE_CHOICES,
        default=CASH,
        help_text="How the payment was made or received"
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Transaction amount in PKR"
    )
    
    fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Service fee or commission earned"
    )
    
    # Auto-calculated cash flow fields
    cash_in = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Money received (auto-calculated)"
    )
    
    cash_out = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Money paid out (auto-calculated)"
    )
    
    # Additional information
    note = models.TextField(
        blank=True,
        help_text="Additional notes or customer details"
    )
    
    # Tracking fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When transaction was recorded"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='transactions',
        help_text="Staff member who recorded this"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update time"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['payment_mode']),
        ]
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    
    def clean(self):
        """
        Model-level validation for data safety.
        
        Validates:
        - Amount is positive
        - Fee is non-negative
        - Fee doesn't exceed amount for applicable transaction types
        - Logical consistency of values
        """
        from django.core.exceptions import ValidationError
        
        errors = {}
        
        # Validate amount
        if self.amount is not None and self.amount <= 0:
            errors['amount'] = 'Amount must be greater than zero.'
        
        # Validate fee
        if self.fee is not None and self.fee < 0:
            errors['fee'] = 'Fee cannot be negative.'
        
        # Business logic validation
        if self.amount and self.fee:
            # For mobile wallet and bill payment types, fee shouldn't exceed amount
            if self.transaction_type in [self.MOBILE_WALLET_SEND, self.MOBILE_WALLET_RECEIVE, 
                                         self.BILL_PAYMENT]:
                if self.fee > self.amount:
                    errors['fee'] = 'Service fee cannot exceed transaction amount.'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-calculate cash_in and cash_out based on transaction type.
        
        Also runs full_clean() to ensure all validation passes before saving.
        This provides an additional safety layer for data integrity.
        
        Business Logic for Shop Transactions:
        
        1. JazzCash Send / EasyPaisa Send:
           - Customer gives us CASH for the amount + fee
           - We send money to recipient via mobile wallet app
           - The app transaction is separate - we only track shop cash
           - cash_in = amount + fee (total cash received from customer)
           - Profit = fee
           
        2. JazzCash Receive / EasyPaisa Receive (Credit):
           - Customer wants to withdraw cash from their mobile wallet
           - Example: Customer has 1000 in wallet, fee is 20
           - You give them: 980 cash (1000 - 20 fee)
           - Manual entry: You enter amount=1000, fee=20
           - System calculates: cash_out = 980, cash_in = 20
           - But you can also manually set cash_in/cash_out if needed
           - Net effect on shop cash: -960 (you give 980, keep 20)
           
        3. Bill Payment:
           - Customer gives us CASH for bill amount + fee
           - We pay the bill via app/online
           - The bill payment is separate - we only track shop cash
           - cash_in = amount + fee (total cash received from customer)
           - Profit = fee
           
        4. Stationary Sale:
           - Customer buys items from our shop
           - We receive payment
           - cash_in = amount (full payment received)
           
        5. Bank Deposit:
           - We take cash from shop and deposit to bank
           - Cash leaves our shop
           - cash_out = amount (cash deposited)
           
        6. Bank Withdrawal:
           - We withdraw cash from bank to shop
           - Cash comes into our shop
           - cash_in = amount (cash withdrawn)
        
        7. Other:
           - Flexible for miscellaneous transactions
           - Defaults to cash_out = amount
        """
        
        # Set fee to 0 if None
        if self.fee is None:
            self.fee = Decimal('0.00')
        
        if self.transaction_type == self.MOBILE_WALLET_SEND:
            # Mobile wallet send: customer gives us cash (amount + fee)
            # The app transfer is separate - we only track our shop cash
            self.cash_in = self.amount + self.fee  # Total cash received
            self.cash_out = Decimal('0.00')
            
        elif self.transaction_type == self.MOBILE_WALLET_RECEIVE:
            # Mobile wallet receive/credit: customer withdraws cash from wallet
            # Example: Customer says "credit 5000", fee is 100
            # - cash_out = 5000 (money goes out to customer)
            # - cash_in = 100 (your profit stays)
            self.cash_out = self.amount
            self.cash_in = self.fee
            
        elif self.transaction_type == self.CASH_CREDIT:
            # Cash credit: customer takes cash to load balance in shop's SIM
            # Example: Customer takes 1000 to deposit in your Zong/Jazz SIM
            # - cash_out = amount (money goes out)
            # - cash_in = 0 (no immediate profit, balance credited to SIM)
            self.cash_out = self.amount
            self.cash_in = Decimal('0.00')
            
        elif self.transaction_type == self.BILL_PAYMENT:
            # Bill payment: customer gives us cash (amount + fee)
            # The bill payment via app is separate - we only track our shop cash
            self.cash_in = self.amount + self.fee  # Total cash received
            self.cash_out = Decimal('0.00')
            
        elif self.transaction_type == self.STATIONARY_SALE:
            # Sale: customer pays us for items
            self.cash_in = self.amount
            self.cash_out = Decimal('0.00')
            
        elif self.transaction_type == self.BANK_DEPOSIT:
            # Deposit: cash goes from shop to bank
            self.cash_out = self.amount
            self.cash_in = Decimal('0.00')
            
        elif self.transaction_type == self.BANK_WITHDRAWAL:
            # Withdrawal: cash comes from bank to shop
            self.cash_in = self.amount
            self.cash_out = Decimal('0.00')
            
        else:
            # OTHER: flexible handling
            # If not explicitly set, default to cash_out
            if self.cash_in == Decimal('0.00') and self.cash_out == Decimal('0.00'):
                self.cash_out = self.amount
        
        # Run validation before saving (safety measure)
        # This ensures all clean() validations pass
        if not kwargs.get('skip_validation', False):
            self.full_clean()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        """String representation for admin and debugging."""
        return (
            f"#{self.id} - {self.get_transaction_type_display()} - "
            f"PKR {self.amount} - {self.created_at.strftime('%Y-%m-%d')}"
        )
    
    @property
    def net_amount(self):
        """
        Net cash flow for this transaction.
        Positive for cash in, negative for cash out.
        """
        return self.cash_in - self.cash_out
    
    @property
    def is_cash_in(self):
        """Check if this is primarily a cash in transaction (net positive)."""
        return self.cash_in > self.cash_out
    
    @property
    def is_cash_out(self):
        """Check if this is primarily a cash out transaction (net negative)."""
        return self.cash_out > self.cash_in


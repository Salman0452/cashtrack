"""
Forms for transaction management.

Users only input: transaction_type, amount, fee, payment_mode, note
The cash_in and cash_out fields are automatically calculated by the model.
"""
from django import forms
from .models import Transaction
from decimal import Decimal


class TransactionForm(forms.ModelForm):
    """
    ModelForm for creating and updating transactions.
    
    Security Features:
    - Excludes cash_in and cash_out from user input (auto-calculated)
    - Validates amount and fee are positive numbers
    - Transaction-specific validation rules
    - CSRF protection via Django (in template)
    - Clean error messages for users
    """
    
    class Meta:
        model = Transaction
        # Only allow these fields - cash_in/cash_out are auto-calculated
        fields = [
            'transaction_type',
            'amount',
            'fee',
            'payment_mode',
            'print_type',
            'quantity',
            'note',
        ]
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'id': 'id_transaction_type',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amount in PKR',
                'step': '0.01',
                'min': '0.01',
                'required': True,
            }),
            'fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter fee/profit (if any)',
                'step': '0.01',
                'min': '0',
            }),
            'payment_mode': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'print_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_print_type',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of pages/copies',
                'min': '1',
                'id': 'id_quantity',
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional: Add customer name, reference, or details',
            }),
        }
        labels = {
            'transaction_type': 'Transaction Type',
            'amount': 'Amount (PKR)',
            'fee': 'Fee/Profit (PKR)',
            'payment_mode': 'Payment Method',
            'print_type': 'Print Type',
            'quantity': 'Quantity',
            'note': 'Notes',
        }
        help_texts = {
            'amount': 'Enter the transaction amount',
            'fee': 'Service fee or commission you earn',
            'print_type': 'Select color or black & white',
            'quantity': 'Number of pages or copies',
            'note': 'Optional details for future reference',
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize form and filter transaction type choices to exclude hidden types."""
        super().__init__(*args, **kwargs)
        
        # Only show user-facing transaction types
        user_facing_choices = [
            (Transaction.MOBILE_WALLET_SEND, 'JazzCash/EasyPaisa Send'),
            (Transaction.MOBILE_WALLET_RECEIVE, 'JazzCash/EasyPaisa Receive'),
            (Transaction.STATIONARY_SALE, 'Stationary Sale'),
            (Transaction.PRINT_COPY, 'Print/Copy'),
            (Transaction.DEPOSIT, 'Deposit'),
            (Transaction.CREDIT, 'Credit'),
            (Transaction.LOAD_PACKAGE, 'Load/Package'),
            (Transaction.OTHER, 'Other'),
        ]
        self.fields['transaction_type'].choices = user_facing_choices
        
        # Make print_type and quantity not required by default
        self.fields['print_type'].required = False
        self.fields['quantity'].required = False
        
        # Remove empty choice from print_type dropdown
        if '' in dict(self.fields['print_type'].choices):
            self.fields['print_type'].choices = [
                choice for choice in self.fields['print_type'].choices if choice[0] != ''
            ]
    
    def clean_amount(self):
        """
        Validate that amount is a positive number.
        Security: Prevents negative or zero amounts.
        """
        amount = self.cleaned_data.get('amount')
        
        if not amount:
            raise forms.ValidationError('Amount is required.')
        
        if amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        
        # Reasonable upper limit to prevent data entry errors
        if amount > Decimal('10000000'):  # 10 million PKR
            raise forms.ValidationError(
                'Amount seems too large. Please verify the amount.'
            )
        
        return amount
    
    def clean_fee(self):
        """
        Validate that fee is non-negative.
        Security: Prevents negative fees.
        """
        fee = self.cleaned_data.get('fee')
        
        if fee is None:
            return Decimal('0.00')
        
        if fee < 0:
            raise forms.ValidationError('Fee cannot be negative.')
        
        return fee
    
    def clean(self):
        """
        Cross-field validation for business logic consistency.
        
        Validates relationships between transaction type, amount, and fee:
        - Mobile wallet sends: Fee should not exceed amount
        - Bill payments: Fee is expected
        - Bank operations: Fee is unusual (warning only)
        """
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        fee = cleaned_data.get('fee', Decimal('0.00'))
        amount = cleaned_data.get('amount', Decimal('0.00'))
        
        # Skip validation if required fields are missing (already handled above)
        if not transaction_type or not amount:
            return cleaned_data
        
        # Validation: Fee should not exceed amount for mobile wallet transactions
        if transaction_type == Transaction.MOBILE_WALLET_SEND:
            if fee > amount:
                raise forms.ValidationError({
                    'fee': 'Service fee cannot be greater than the send amount.'
                })
            
            # Warn if no fee for mobile wallet (optional - can be removed if too strict)
            if fee == 0:
                # Non-blocking warning - just adds to field errors
                self.add_error('fee', 
                    'Tip: Mobile wallet transactions typically have a service fee.')
        
        # Validation: Bill payment should typically have a fee
        elif transaction_type == Transaction.BILL_PAYMENT:
            if fee == 0:
                self.add_error('fee',
                    'Tip: Bill payment service should include a fee.')
        
        # Info: Bank operations typically don't have fees
        elif transaction_type in [Transaction.BANK_DEPOSIT, Transaction.BANK_WITHDRAWAL]:
            if fee > 0:
                # Just informational - not blocking
                self.add_error('fee',
                    'Note: Bank operations don\'t usually have fees, but will be recorded.')
        
        # Validation: Stationary sale - fee is optional but shouldn't exceed amount
        elif transaction_type == Transaction.STATIONARY_SALE:
            if fee > amount:
                raise forms.ValidationError({
                    'fee': 'Fee cannot exceed the sale amount.'
                })
        
        return cleaned_data

"""
Forms for bill management.
"""
from django import forms
from .models import Bill
from decimal import Decimal


class BillForm(forms.ModelForm):
    """Form for creating and updating bills."""
    
    class Meta:
        model = Bill
        fields = [
            'customer_id',
            'customer_name',
            'amount',
            'fee',
            'due_date',
            'note',
        ]
        widgets = {
            'customer_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer ID',
                'required': True,
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name (optional)',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter bill amount',
                'step': '0.01',
                'min': '0.01',
                'required': True,
            }),
            'fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter service fee',
                'step': '0.01',
                'min': '0',
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True,
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes',
            }),
        }
        labels = {
            'customer_id': 'Customer ID',
            'customer_name': 'Customer Name',
            'amount': 'Bill Amount (PKR)',
            'fee': 'Service Fee (PKR)',
            'due_date': 'Due Date',
            'note': 'Notes',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

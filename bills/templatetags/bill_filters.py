"""
Custom template filters for bills.
"""
from django import template

register = template.Library()


@register.filter
def sum_total_amounts(bills):
    """Calculate total amount for a list of bills."""
    return sum(bill.total_amount for bill in bills)

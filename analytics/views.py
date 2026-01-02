"""
Analytics views for transaction analysis and reporting.
"""
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from transactions.models import Transaction


class AnalyticsView(LoginRequiredMixin, TemplateView):
    """View for analytics dashboard with charts and breakdowns."""
    template_name = 'analytics/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current date and time with timezone awareness
        now = timezone.localtime(timezone.now())
        today = now.date()
        yesterday = today - timedelta(days=1)
        month_start = today.replace(day=1)
        
        # Define transaction type groups for analysis
        transaction_types = {
            'mobile_wallet_send': [
                Transaction.MOBILE_WALLET_SEND,
                Transaction.JAZZCASH_SEND,
                Transaction.EASYPAISA_SEND
            ],
            'mobile_wallet_receive': [
                Transaction.MOBILE_WALLET_RECEIVE,
                Transaction.JAZZCASH_RECEIVE,
                Transaction.EASYPAISA_RECEIVE
            ],
            'print_copy': [Transaction.PRINT_COPY],
            'stationary': [Transaction.STATIONARY_SALE],
            'deposit': [Transaction.DEPOSIT],
            'credit': [Transaction.CREDIT],
            'load_package': [Transaction.LOAD_PACKAGE],
            'bill_payment': [Transaction.BILL_PAYMENT],
        }
        
        # Get data for different time periods using simple date comparison
        periods = {
            'today': {'date': today, 'type': 'single'},
            'yesterday': {'date': yesterday, 'type': 'single'},
            'monthly': {'start_date': month_start, 'end_date': today, 'type': 'range'},
            'all_time': {'type': 'all'},
        }
        
        analytics_data = {}
        
        for period_name, period_config in periods.items():
            period_data = {}
            
            for type_name, type_list in transaction_types.items():
                # Build queryset
                qs = Transaction.objects.filter(transaction_type__in=type_list)
                
                # Apply date filtering based on period type
                if period_config['type'] == 'single':
                    # Filter by exact date (today or yesterday)
                    qs = qs.filter(created_at__date=period_config['date'])
                elif period_config['type'] == 'range':
                    # Filter by date range (monthly)
                    qs = qs.filter(
                        created_at__date__gte=period_config['start_date'],
                        created_at__date__lte=period_config['end_date']
                    )
                # For 'all', no filtering needed
                
                # Get transactions and calculate totals manually
                transactions = list(qs)
                
                # Calculate net cash flow (cash_in - cash_out)
                total_cash_in = Decimal('0')
                total_cash_out = Decimal('0')
                total_profit = Decimal('0')
                
                for t in transactions:
                    total_cash_in += t.cash_in
                    total_cash_out += t.cash_out
                    
                    # Profit is always the fee
                    if t.fee:
                        total_profit += t.fee
                
                # Net cash is cash_in - cash_out (matches dashboard calculation)
                net_cash = total_cash_in - total_cash_out
                count = len(transactions)
                
                period_data[type_name] = {
                    'cash': net_cash,
                    'profit': total_profit,
                    'count': count,
                }
            
            analytics_data[period_name] = period_data
        
        context['analytics'] = analytics_data
        context['today'] = today
        context['yesterday'] = yesterday
        context['month_start'] = month_start
        
        # Calculate totals for each period
        period_totals = {}
        for period_name, period_data in analytics_data.items():
            total_cash = sum(item['cash'] for item in period_data.values())
            total_profit = sum(item['profit'] for item in period_data.values())
            total_count = sum(item['count'] for item in period_data.values())
            
            period_totals[period_name] = {
                'cash': total_cash,
                'profit': total_profit,
                'count': total_count,
            }
        
        context['period_totals'] = period_totals
        
        # Transaction type labels for display
        context['type_labels'] = {
            'mobile_wallet_send': 'Mobile Wallet Send',
            'mobile_wallet_receive': 'Mobile Wallet Receive',
            'print_copy': 'Print/Copy',
            'stationary': 'Stationary',
            'deposit': 'Deposit',
            'credit': 'Credit',
            'load_package': 'Load/Package',
            'bill_payment': 'Bill Payment',
        }
        
        return context

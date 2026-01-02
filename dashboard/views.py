"""
Dashboard view displaying key financial metrics and recent transactions.
Provides real-time overview of shop's cash position and daily activity.

Performance optimizations:
- Uses Django ORM aggregation for efficient queries
- Minimizes database hits with select_related
- Leverages database-level calculations
"""
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q
from django.utils import timezone
from transactions.models import Transaction
from datetime import datetime, time, timedelta


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard for shop cash management.
    
    Displays:
    1. Total cash in hand (cash_in - cash_out across all time)
    2. Today's profit (sum of fees for today)
    3. Total transactions today
    4. Latest 10 transactions
    
    Uses class-based view with efficient ORM aggregation.
    """
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        """
        Calculate and provide all dashboard metrics.
        
        Optimization: Uses aggregation to calculate sums in database
        rather than loading all records into Python memory.
        """
        context = super().get_context_data(**kwargs)
        
        # Get today's date range in Pakistan timezone (Asia/Karachi)
        now = timezone.localtime(timezone.now())
        today_start = timezone.make_aware(
            datetime.combine(now.date(), time.min)
        )
        today_end = timezone.make_aware(
            datetime.combine(now.date(), time.max)
        )
        
        # =====================================================
        # ALL-TIME METRICS (using single aggregation query)
        # =====================================================
        all_time_stats = Transaction.objects.aggregate(
            total_cash_in=Sum('cash_in'),
            total_cash_out=Sum('cash_out'),
            total_profit=Sum('fee'),
        )
        
        # Total cash in hand: net balance of all transactions
        context['total_cash_in_hand'] = (
            (all_time_stats['total_cash_in'] or 0) - 
            (all_time_stats['total_cash_out'] or 0)
        )
        
        # Total profit: sum of all fees earned
        context['total_profit'] = all_time_stats['total_profit'] or 0
        
        # =====================================================
        # TODAY'S METRICS (using single aggregation query)
        # =====================================================
        today_stats = Transaction.objects.filter(
            created_at__range=(today_start, today_end)
        ).aggregate(
            count=Count('id'),
            cash_in=Sum('cash_in'),
            cash_out=Sum('cash_out'),
            fees=Sum('fee'),
        )
        
        context['today_transactions_count'] = today_stats['count'] or 0
        context['today_cash_in'] = today_stats['cash_in'] or 0
        context['today_cash_out'] = today_stats['cash_out'] or 0
        context['today_fees'] = today_stats['fees'] or 0
        context['today_net'] = (
            (today_stats['cash_in'] or 0) - 
            (today_stats['cash_out'] or 0)
        )
        
        # =====================================================
        # TODAY'S PROFIT (explicitly for dashboard display)
        # =====================================================
        # This is the same as today_fees but separated for clarity
        context['today_profit'] = today_stats['fees'] or 0
        
        # =====================================================
        # THIS MONTH'S PROFIT
        # =====================================================
        # Calculate profit for current month
        month_start = timezone.make_aware(
            datetime.combine(now.date().replace(day=1), time.min)
        )
        month_end = today_end
        
        month_stats = Transaction.objects.filter(
            created_at__range=(month_start, month_end)
        ).aggregate(
            fees=Sum('fee'),
        )
        
        context['month_profit'] = month_stats['fees'] or 0
        
        # =====================================================
        # BREAKDOWN BY TRANSACTION TYPE (Today)
        # =====================================================
        # Shows which transaction types were most active today
        context['today_by_type'] = Transaction.objects.filter(
            created_at__range=(today_start, today_end)
        ).values('transaction_type').annotate(
            count=Count('id'),
            total_amount=Sum('amount'),
            total_fees=Sum('fee'),
        ).order_by('-total_amount')
        
        # =====================================================
        # RECENT TRANSACTIONS (Latest 10)
        # =====================================================
        # Use select_related to fetch user data in single query (prevents N+1)
        context['recent_transactions'] = Transaction.objects.select_related(
            'created_by'
        ).order_by('-created_at')[:10]
        
        # =====================================================
        # ADDITIONAL CONTEXT
        # =====================================================
        context['current_date'] = now
        context['today_date'] = now.date()
        
        return context


class DailyBalanceHistoryView(LoginRequiredMixin, TemplateView):
    """
    Shows daily balance history with opening and closing balances.
    
    Displays:
    - Each day's opening balance (previous day closing)
    - Total cash in for the day
    - Total cash out for the day
    - Closing balance
    - Net change for the day
    """
    template_name = 'dashboard/daily_balance_history.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from query params or default to last 30 days
        now = timezone.localtime(timezone.now())
        
        # Parse dates from request or use defaults
        end_date = now.date()
        start_date = end_date - timedelta(days=30)
        
        if self.request.GET.get('start_date'):
            start_date = datetime.strptime(
                self.request.GET.get('start_date'), '%Y-%m-%d'
            ).date()
        
        if self.request.GET.get('end_date'):
            end_date = datetime.strptime(
                self.request.GET.get('end_date'), '%Y-%m-%d'
            ).date()
        
        # Get all transactions grouped by date
        daily_data = []
        current_date = start_date
        opening_balance = 0
        
        # Calculate opening balance (all transactions before start_date)
        transactions_before = Transaction.objects.filter(
            created_at__lt=timezone.make_aware(
                datetime.combine(start_date, time.min)
            )
        ).aggregate(
            cash_in=Sum('cash_in'),
            cash_out=Sum('cash_out'),
        )
        
        opening_balance = (
            (transactions_before['cash_in'] or 0) - 
            (transactions_before['cash_out'] or 0)
        )
        
        # Loop through each day in the range
        while current_date <= end_date:
            day_start = timezone.make_aware(
                datetime.combine(current_date, time.min)
            )
            day_end = timezone.make_aware(
                datetime.combine(current_date, time.max)
            )
            
            # Get transactions for this day
            day_stats = Transaction.objects.filter(
                created_at__range=(day_start, day_end)
            ).aggregate(
                cash_in=Sum('cash_in'),
                cash_out=Sum('cash_out'),
                fee=Sum('fee'),
                count=Count('id'),
            )
            
            cash_in = day_stats['cash_in'] or 0
            cash_out = day_stats['cash_out'] or 0
            fee = day_stats['fee'] or 0
            count = day_stats['count'] or 0
            
            net_change = cash_in - cash_out
            closing_balance = opening_balance + net_change
            
            # Only include days with transactions or if it's today
            if count > 0 or current_date == now.date():
                daily_data.append({
                    'date': current_date,
                    'opening_balance': opening_balance,
                    'cash_in': cash_in,
                    'cash_out': cash_out,
                    'fee': fee,
                    'net_change': net_change,
                    'closing_balance': closing_balance,
                    'transaction_count': count,
                    'is_today': current_date == now.date(),
                })
            
            # Next day's opening is today's closing
            opening_balance = closing_balance
            current_date += timedelta(days=1)
        
        # Reverse to show most recent first
        daily_data.reverse()
        
        context['daily_data'] = daily_data
        context['start_date'] = start_date
        context['end_date'] = end_date
        context['current_balance'] = opening_balance  # Latest closing balance
        
        return context

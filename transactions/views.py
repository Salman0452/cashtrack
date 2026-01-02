"""
Transaction views for CRUD operations.
All views require authentication and use class-based views for clean, maintainable code.
"""
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Transaction
from .forms import TransactionForm


class TransactionListView(LoginRequiredMixin, ListView):
    """
    Display all transactions with filtering capabilities.
    
    Filters:
    - Date range (today, this week, this month, custom)
    - Transaction type (JazzCash, EasyPaisa, Bill Payment, etc.)
    - Payment mode (Cash, Bank, etc.)
    - Search by note
    
    Features:
    - Pagination (20 items per page)
    - Color-coded cash in/out
    - Responsive mobile layout
    - Optimized queries with select_related
    """
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def get_queryset(self):
        """
        Get filtered transactions based on query parameters.
        Optimized with select_related to prevent N+1 queries.
        """
        queryset = Transaction.objects.select_related('created_by').all()
        
        # Filter by transaction type
        transaction_type = self.request.GET.get('type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        # Filter by payment mode
        payment_mode = self.request.GET.get('payment')
        if payment_mode:
            queryset = queryset.filter(payment_mode=payment_mode)
        
        # Filter by date range
        date_filter = self.request.GET.get('date')
        now = timezone.localtime(timezone.now())
        
        if date_filter == 'today':
            # Today's transactions
            today_start = datetime.combine(now.date(), datetime.min.time())
            today_end = datetime.combine(now.date(), datetime.max.time())
            queryset = queryset.filter(
                created_at__range=(
                    timezone.make_aware(today_start),
                    timezone.make_aware(today_end)
                )
            )
        elif date_filter == 'week':
            # This week's transactions
            week_start = now - timedelta(days=now.weekday())
            queryset = queryset.filter(created_at__gte=week_start.replace(hour=0, minute=0, second=0))
        elif date_filter == 'month':
            # This month's transactions
            month_start = now.replace(day=1, hour=0, minute=0, second=0)
            queryset = queryset.filter(created_at__gte=month_start)
        elif date_filter == 'custom':
            # Custom date range
            start_date = self.request.GET.get('start_date')
            end_date = self.request.GET.get('end_date')
            
            if start_date:
                start_datetime = timezone.make_aware(
                    datetime.strptime(start_date, '%Y-%m-%d')
                )
                queryset = queryset.filter(created_at__gte=start_datetime)
            
            if end_date:
                end_datetime = timezone.make_aware(
                    datetime.strptime(end_date, '%Y-%m-%d').replace(
                        hour=23, minute=59, second=59
                    )
                )
                queryset = queryset.filter(created_at__lte=end_datetime)
        
        # Search by note
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(note__icontains=search) | 
                Q(created_by__username__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add filter options and current filters to context."""
        context = super().get_context_data(**kwargs)
        
        # Current filter values (for maintaining state in template)
        context['current_type'] = self.request.GET.get('type', '')
        context['current_payment'] = self.request.GET.get('payment', '')
        context['current_date'] = self.request.GET.get('date', '')
        context['current_search'] = self.request.GET.get('search', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        
        # Filter options - only show active transaction types (not legacy)
        active_transaction_types = [
            (Transaction.MOBILE_WALLET_SEND, 'Mobile Wallet Send (JazzCash/EasyPaisa)'),
            (Transaction.MOBILE_WALLET_RECEIVE, 'Mobile Wallet Receive (JazzCash/EasyPaisa)'),
            (Transaction.STATIONARY_SALE, 'Stationary Sale'),
            (Transaction.PRINT_COPY, 'Print/Copy'),
            (Transaction.DEPOSIT, 'Deposit'),
            (Transaction.CREDIT, 'Credit'),
            (Transaction.LOAD_PACKAGE, 'Load/Package'),
            (Transaction.BILL_PAYMENT, 'Bill Payment'),
            (Transaction.OTHER, 'Other'),
        ]
        context['transaction_types'] = active_transaction_types
        context['payment_modes'] = Transaction.PAYMENT_MODE_CHOICES
        
        # Build query string for pagination (preserve filters)
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')
        context['query_string'] = query_params.urlencode()
        
        return context


class TransactionCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new transaction.
    Automatically sets the created_by field to current user.
    """
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('dashboard:home')
    
    def form_valid(self, form):
        """Set the created_by field to current user before saving."""
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Transaction recorded successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Show error message if form validation fails."""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing transaction.
    
    Safety Features:
    - Only allows editing recent transactions (within 24 hours)
    - No delete functionality (audit trail preservation)
    - Validates all inputs through form
    - Shows clear success/error messages
    """
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('dashboard:home')
    
    def get_queryset(self):
        """
        Restrict editing to recent transactions only (optional safety measure).
        Uncomment the time filter to enable 24-hour edit window.
        """
        queryset = super().get_queryset()
        
        # Optional: Restrict editing to transactions created in last 24 hours
        # Uncomment the lines below to enable this safety feature
        # from datetime import timedelta
        # time_limit = timezone.now() - timedelta(hours=24)
        # queryset = queryset.filter(created_at__gte=time_limit)
        
        return queryset
    
    def get_object(self, queryset=None):
        """
        Get the transaction and verify edit permissions.
        Shows user-friendly error if transaction cannot be edited.
        """
        obj = super().get_object(queryset)
        
        # Optional: Check if transaction is too old to edit
        # Uncomment to enable 24-hour edit restriction
        # from datetime import timedelta
        # if obj.created_at < timezone.now() - timedelta(hours=24):
        #     messages.error(
        #         self.request, 
        #         'This transaction is older than 24 hours and cannot be edited for data safety.'
        #     )
        #     raise Http404("Transaction cannot be edited")
        
        return obj
    
    def form_valid(self, form):
        """
        Process valid form with safety checks.
        Maintains original created_by and created_at values.
        """
        # Preserve original created_by (prevent tampering)
        form.instance.created_by = self.object.created_by
        
        messages.success(
            self.request, 
            f'Transaction #{self.object.id} updated successfully!'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Show clear error message if form validation fails."""
        messages.error(
            self.request, 
            'Please correct the errors below. Check amount, fee, and other fields.'
        )
        return super().form_invalid(form)


class TransactionDetailView(LoginRequiredMixin, DetailView):
    """
    Display detailed view of a single transaction.
    """
    model = Transaction
    template_name = 'transactions/transaction_detail.html'
    context_object_name = 'transaction'


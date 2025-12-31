"""
Views for bill management.
"""
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.db import transaction as db_transaction
from .models import Bill
from .forms import BillForm
from transactions.models import Transaction


class BillListView(LoginRequiredMixin, ListView):
    """View to list all bills with filtering and grouping by due date."""
    model = Bill
    template_name = 'bills/bill_list.html'
    context_object_name = 'bills'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Bill.objects.select_related('created_by', 'transaction')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by customer ID
        customer_id = self.request.GET.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id__icontains=customer_id)
        
        # Filter by date range
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(due_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(due_date__lte=end_date)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(customer_id__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(note__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all bills for statistics
        all_bills = Bill.objects.all()
        
        # Total bills count
        context['total_bills'] = all_bills.count()
        context['pending_bills'] = all_bills.filter(status=Bill.PENDING).count()
        context['paid_bills'] = all_bills.filter(status=Bill.PAID).count()
        context['overdue_bills'] = all_bills.filter(
            status=Bill.PENDING,
            due_date__lt=timezone.now().date()
        ).count()
        
        # Today's date for highlighting
        context['today'] = timezone.now().date()
        
        # Group bills by due date (only pending bills)
        bills_by_date = Bill.objects.filter(
            status=Bill.PENDING
        ).values('due_date').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('due_date')[:10]  # Next 10 due dates
        
        context['bills_by_date'] = bills_by_date
        
        # Query string for pagination
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')
        context['query_string'] = query_params.urlencode()
        
        return context


class BillCreateView(LoginRequiredMixin, CreateView):
    """View to create a new bill."""
    model = Bill
    form_class = BillForm
    template_name = 'bills/bill_form.html'
    success_url = reverse_lazy('bills:list')
    
    @db_transaction.atomic
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        bill = form.save()
        
        # Automatically create transaction for the bill
        # Customer pays upfront (amount + fee)
        txn = Transaction.objects.create(
            transaction_type=Transaction.BILL_PAYMENT,
            payment_mode=Transaction.CASH,
            amount=bill.amount,
            fee=bill.fee,
            note=f"Bill payment for customer {bill.customer_id}",
            created_by=self.request.user
        )
        
        # Mark bill as paid immediately
        bill.mark_as_paid(txn)
        
        messages.success(self.request, f'Bill created and marked as paid! Transaction #{txn.id} created.')
        return redirect(self.success_url)


class BillUpdateView(LoginRequiredMixin, UpdateView):
    """View to update an existing bill."""
    model = Bill
    form_class = BillForm
    template_name = 'bills/bill_form.html'
    success_url = reverse_lazy('bills:list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Bill updated successfully!')
        return super().form_valid(form)


class BillDetailView(LoginRequiredMixin, DetailView):
    """View to see bill details."""
    model = Bill
    template_name = 'bills/bill_detail.html'
    context_object_name = 'bill'


class BillMarkAsPaidView(LoginRequiredMixin, View):
    """View to mark a bill as paid and create associated transaction."""
    
    @db_transaction.atomic
    def post(self, request, pk):
        bill = get_object_or_404(Bill, pk=pk)
        
        # Check if already paid
        if bill.status == Bill.PAID:
            messages.warning(request, 'This bill is already marked as paid.')
            return redirect('bills:detail', pk=pk)
        
        # Create transaction for bill payment
        txn = Transaction.objects.create(
            transaction_type=Transaction.BILL_PAYMENT,
            payment_mode=Transaction.CASH,
            amount=bill.amount,
            fee=bill.fee,
            note=f"Bill payment for customer {bill.customer_id}",
            created_by=request.user
        )
        
        # Mark bill as paid
        bill.mark_as_paid(txn)
        
        messages.success(request, f'Bill marked as paid! Transaction #{txn.id} created.')
        return redirect('bills:detail', pk=pk)


class BillBulkMarkAsPaidView(LoginRequiredMixin, View):
    """View to mark multiple bills as paid in bulk."""
    
    @db_transaction.atomic
    def post(self, request):
        bill_ids = request.POST.getlist('bill_ids')
        
        if not bill_ids:
            messages.warning(request, 'No bills selected.')
            return redirect('bills:list')
        
        # Get pending bills only
        bills = Bill.objects.filter(id__in=bill_ids, status=Bill.PENDING)
        
        if not bills.exists():
            messages.warning(request, 'No pending bills found in selection.')
            return redirect('bills:list')
        
        count = 0
        for bill in bills:
            # Create transaction for each bill
            txn = Transaction.objects.create(
                transaction_type=Transaction.BILL_PAYMENT,
                payment_mode=Transaction.CASH,
                amount=bill.amount,
                fee=bill.fee,
                note=f"Bill payment for customer {bill.customer_id}",
                created_by=request.user
            )
            
            # Mark bill as paid
            bill.mark_as_paid(txn)
            count += 1
        
        messages.success(request, f'{count} bill(s) marked as paid successfully!')
        return redirect('bills:list')



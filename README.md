# CashTrack - Shop Cash Management System

A production-ready Django application for managing cash transactions in a small shop in Pakistan.

## Features

- **Transaction Management**: Record and track all shop transactions
- **Automatic Cash Flow Calculation**: Smart business logic handles cash in/out automatically
- **Dashboard**: Real-time overview of cash position, profit, and daily activity
- **Mobile Wallet Support**: JazzCash and EasyPaisa integration
- **Multiple Transaction Types**: Stationary sales, bill payments, bank operations
- **User Authentication**: Secure login system
- **Responsive Design**: Bootstrap 5 mobile-first UI

## Transaction Types & Business Logic

### 1. JazzCash Send / EasyPaisa Send
**Scenario**: Customer wants to send money via mobile wallet
- **Cash Flow**: 
  - `cash_out = amount` (money sent to recipient)
  - `cash_in = fee` (your commission)
- **Example**: Customer sends PKR 5,000, you charge PKR 50 fee
  - You receive PKR 5,050 from customer
  - You send PKR 5,000 via JazzCash
  - You keep PKR 50 as profit

### 2. Bill Payment
**Scenario**: Customer asks you to pay their utility bill
- **Cash Flow**:
  - `cash_in = fee` (service charge only)
  - Amount cancels out (you pay bill, customer pays you back)
- **Example**: Customer's bill is PKR 3,000, you charge PKR 30
  - You pay PKR 3,000 to utility company
  - Customer pays you PKR 3,030
  - Net: PKR 30 profit

### 3. Stationary Sale
**Scenario**: Customer buys items from your shop
- **Cash Flow**:
  - `cash_in = amount` (payment received)
- **Example**: Customer buys items worth PKR 500
  - You receive PKR 500

### 4. Bank Deposit
**Scenario**: You deposit cash from shop to bank
- **Cash Flow**:
  - `cash_out = amount` (cash leaves shop)
- **Example**: Deposit PKR 10,000 to bank
  - Shop cash reduces by PKR 10,000

### 5. Bank Withdrawal
**Scenario**: You withdraw cash from bank to shop
- **Cash Flow**:
  - `cash_in = amount` (cash comes to shop)
- **Example**: Withdraw PKR 10,000 from bank
  - Shop cash increases by PKR 10,000

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Django 4.2+

### 2. Initial Setup

```bash
# Navigate to project directory
cd /Users/salmanahmad/django/website

# Create migrations (if needed)
python3 manage.py makemigrations

# Apply migrations
python3 manage.py migrate

# Create superuser for admin access
python3 manage.py createsuperuser

# Run development server
python3 manage.py runserver
```

### 3. Access the Application

- **Main Application**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **Login**: Use the superuser credentials you created

## Project Structure

```
cashtrack/
├── cashtrack/              # Project settings
│   ├── settings.py        # Configuration
│   ├── urls.py            # Main URL routing
│   └── wsgi.py
├── accounts/              # Authentication app
│   ├── views.py           # Login/logout views
│   └── urls.py
├── transactions/          # Transaction management
│   ├── models.py          # Transaction model with business logic
│   ├── forms.py           # Transaction form with validation
│   ├── views.py           # CRUD views
│   ├── admin.py           # Admin configuration
│   └── urls.py
├── dashboard/             # Dashboard app
│   ├── views.py           # Dashboard metrics
│   └── urls.py
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── accounts/          # Login templates
│   ├── transactions/      # Transaction templates
│   └── dashboard/         # Dashboard templates
└── static/                # Static files (CSS, JS, images)
```

## Key Models

### Transaction Model
- `transaction_type`: Type of transaction (JazzCash, EasyPaisa, Bill, Sale, etc.)
- `payment_mode`: Payment method (Cash, JazzCash, EasyPaisa, Bank)
- `amount`: Transaction amount in PKR
- `fee`: Service fee or commission
- `cash_in`: Money received (auto-calculated)
- `cash_out`: Money paid out (auto-calculated)
- `note`: Additional notes
- `created_at`: Timestamp
- `created_by`: User who created the transaction

## Dashboard Metrics

- **Total Cash in Hand**: Net balance (total cash_in - total cash_out)
- **Total Profit**: Sum of all fees earned
- **Today's Transactions**: Count and breakdown of today's activity
- **Recent Transactions**: Last 10 transactions

## Admin Features

- List view with filters by type, payment mode, date, user
- Color-coded transaction types (green for cash in, red for cash out)
- Search by note and username
- Date hierarchy for easy navigation
- Auto-calculated fields (cash_in, cash_out)
- Audit trail (created_by, timestamps)

## Best Practices Implemented

1. **Class-Based Views**: Clean, maintainable code
2. **Database Indexing**: Optimized queries with indexes on frequently searched fields
3. **N+1 Query Prevention**: Using `select_related()` for foreign keys
4. **Validation**: Form and model-level validation
5. **Comments**: Clear documentation throughout code
6. **Security**: Login required for all views, CSRF protection
7. **Timezone**: Configured for Asia/Karachi (Pakistan time)
8. **Responsive Design**: Mobile-first Bootstrap 5 UI

## Usage Tips

1. **Daily Operations**: Use the dashboard to monitor cash position
2. **Recording Transactions**: Click "New Transaction" and select appropriate type
3. **Fees**: Always enter service fees for mobile wallet and bill payment transactions
4. **Bank Operations**: Use Bank Deposit/Withdrawal to track bank transfers
5. **Reports**: Use admin panel for detailed filtering and search

## Production Considerations

Before deploying to production:

1. Change `SECRET_KEY` in settings.py
2. Set `DEBUG = False`
3. Configure `ALLOWED_HOSTS`
4. Use PostgreSQL instead of SQLite
5. Set up static file serving (collectstatic)
6. Configure HTTPS
7. Set up backup strategy for database
8. Configure logging
9. Use environment variables for sensitive settings

## Support

For issues or questions, review the code comments in:
- `transactions/models.py` - Business logic implementation
- `transactions/forms.py` - Validation rules
- `dashboard/views.py` - Dashboard calculations

## License

Proprietary - For internal shop use only.

---

**Version**: 1.0  
**Date**: December 30, 2025  
**Developer**: Senior Django Engineer

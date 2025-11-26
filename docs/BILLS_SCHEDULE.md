# Bills Schedule Generator Utility

## Overview
The Bills Schedule Generator is a utility for creating projected bills schedules to help with financial planning and budgeting. It calculates when bills will be due over a specified period and tracks balance changes.

## Location
`backend/utils/bills_schedule.py`

## Main Function

### `generate_bills_schedule()`

```python
from utils.bills_schedule import generate_bills_schedule
from datetime import date

result = generate_bills_schedule(
    start_date=date(2025, 11, 1),
    months_to_project=3,
    starting_balance=2000.0,
    actual_starting_balance=1800.0,
    bills=bills_list,
    buffer=100.0  # optional
)
```

### Parameters

- **start_date** (date): Starting date for the projection
- **months_to_project** (int): Number of months to project forward
- **starting_balance** (float): Expected/ideal starting balance
- **actual_starting_balance** (float): Current actual balance
- **bills** (List[Dict]): List of bill dictionaries (see format below)
- **buffer** (float, optional): Additional buffer amount (default: 0.0)

### Bills List Format

Each bill should be a dictionary with the following keys:

```python
bills = [
    {
        'name': 'Rent',
        'amount': 1200.0,
        'due_date': 1,  # Day of month (1-31)
        'autopay_enabled': True
    },
    {
        'name': 'Electric Bill',
        'amount': 150.0,
        'due_date': 15,
        'autopay_enabled': False
    }
]
```

**Required Fields**:
- `name`: Bill name/description
- `amount`: Bill amount (positive number)
- `due_date`: Day of month when bill is due (1-31)
- `autopay_enabled`: Whether bill is automatically paid

## Return Format

The function returns a dictionary with two main sections:

### Schedule Entries
```python
{
    'schedule': [
        {
            'date': '2025-11-01',
            'bill_name': 'Rent',
            'payment': 1200.0,  # Amount if autopay, None if manual
            'deposit': None,     # Reserved for future use
            'expected_balance': 800.0,
            'is_autopay': True
        }
    ]
}
```

### Summary Statistics
```python
{
    'summary': {
        'expected_minimum': 150.0,
        'actual_minimum': -50.0,
        'extra_payment_required': 250.0,
        'starting_balance': 2000.0,
        'actual_starting_balance': 1800.0,
        'buffer': 100.0,
        'projection_period': {
            'start_date': '2025-11-01',
            'end_date': '2026-02-01',
            'months': 3
        },
        'total_bills': 12,
        'total_autopay_amount': 4200.0,
        'total_manual_bills': 3
    }
}
```

## Key Features

### 1. Automatic Date Handling
- Handles months with different numbers of days
- If a bill is due on the 31st but the month only has 30 days, it schedules for the 30th
- Properly handles leap years

### 2. Balance Tracking
- **Expected Balance**: Tracks balance assuming ideal starting amount
- **Actual Balance**: Tracks balance from actual starting amount
- **Minimum Tracking**: Records the lowest balance during the projection period

### 3. Autopay vs Manual Bills
- **Autopay bills**: Show payment amount in the `payment` field
- **Manual bills**: Show `None` for payment (user must manually pay)

### 4. Summary Calculations
- **Expected Minimum**: Lowest balance if starting with expected amount
- **Actual Minimum**: Lowest balance with actual starting amount
- **Extra Payment Required**: Amount needed to bridge the gap between actual and expected balances, plus buffer

## Integration with Database Models

To use with your database models, convert model data to the required format:

```python
from models.bill import Bill
from utils.bills_schedule import generate_bills_schedule

# Get bills from database
db_bills = Bill.query.filter_by(user_id=user_id).all()

# Convert to required format
bills_list = []
for bill in db_bills:
    bills_list.append({
        'name': bill.name,
        'amount': bill.amount,
        'due_date': bill.due_date,  # Assuming this is day of month
        'autopay_enabled': bill.autopay_enabled
    })

# Generate schedule
schedule = generate_bills_schedule(
    start_date=date.today(),
    months_to_project=6,
    starting_balance=target_balance,
    actual_starting_balance=current_balance,
    bills=bills_list
)
```

## Example Output

```python
{
    'schedule': [
        {
            'date': '2025-11-01',
            'bill_name': 'Rent',
            'payment': 1200.0,
            'deposit': None,
            'expected_balance': 800.0,
            'is_autopay': True
        },
        {
            'date': '2025-11-15',
            'bill_name': 'Electric Bill',
            'payment': None,
            'deposit': None,
            'expected_balance': 650.0,
            'is_autopay': False
        }
    ],
    'summary': {
        'expected_minimum': 200.0,
        'actual_minimum': 0.0,
        'extra_payment_required': 300.0,
        'total_bills': 6,
        'total_autopay_amount': 3600.0,
        'total_manual_bills': 2
    }
}
```

## Future Enhancements

The utility is designed to be extensible for future features:

- **Adjusted Deposit** column for income projections
- **Actual Balance** tracking with real transaction data
- **Variable bill amounts** based on historical data
- **Income integration** for more accurate projections
- **What-if scenarios** with different starting balances
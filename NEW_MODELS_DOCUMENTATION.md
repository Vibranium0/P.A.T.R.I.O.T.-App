# P.A.T.R.I.O.T. Database Models - Implementation Complete

## Overview

The P.A.T.R.I.O.T. application now includes comprehensive database models for managing household finances. This document provides an overview of all models, their relationships, and usage examples.

## New Models Added

### 1. Category Model (`patriot/backend/models/category.py`)

**Purpose**: Organize expenses, income, and other financial items with hierarchical categorization.

**Key Features**:
- Hierarchical structure (parent-child relationships)
- Support for expense, income, savings, and debt categories
- Budget amount tracking per category
- Icon and color customization
- Default category templates

**Fields**:
- `id`: Primary key
- `household_id`: Foreign key to Household
- `name`: Category name
- `description`: Optional description
- `category_type`: Type (expense, income, savings, debt)
- `parent_id`: Foreign key to parent Category (for subcategories)
- `icon`: Icon name or emoji
- `color`: Hex color code
- `budget_amount`: Optional monthly budget limit
- `is_active`: Active status flag
- `created_at`: Timestamp

**Relationships**:
- `household`: Many-to-one with Household
- `parent`: Self-referential for hierarchy
- `subcategories`: One-to-many with child Categories
- `expenses`: One-to-many with Expenses
- `savings`: One-to-many with Savings

**Methods**:
- `to_dict(include_subcategories=False)`: Serialize to dictionary
- `full_name`: Property returning hierarchical name (e.g., "Housing > Utilities")
- `get_default_categories()`: Static method returning default category structures

---

### 2. Expense Model (`patriot/backend/models/expense.py`)

**Purpose**: Track all household expenditures with detailed information.

**Key Features**:
- Link to accounts, categories, and bills
- Support for recurring expenses
- Flexible tagging system
- Receipt storage capability
- Comprehensive expense analytics

**Fields**:
- `id`: Primary key
- `household_id`: Foreign key to Household
- `created_by_user_id`: Foreign key to User
- `account_id`: Foreign key to Account (optional)
- `category_id`: Foreign key to Category (optional)
- `bill_id`: Foreign key to Bill (optional)
- `date`: Expense date
- `amount`: Expense amount
- `description`: Expense description
- `merchant`: Store or vendor name
- `payment_method`: Payment type (cash, credit, debit, etc.)
- `is_recurring`: Recurring expense flag
- `tags`: Comma-separated tags
- `receipt_url`: Link to receipt image/document
- `notes`: Additional notes
- `created_at`: Timestamp
- `updated_at`: Last update timestamp

**Relationships**:
- `household`: Many-to-one with Household
- `created_by`: Many-to-one with User
- `account`: Many-to-one with Account
- `category`: Many-to-one with Category
- `bill`: Many-to-one with Bill

**Methods**:
- `to_dict()`: Serialize to dictionary with nested data
- `get_total_by_category(household_id, start_date, end_date)`: Static method for category totals
- `get_total_for_period(household_id, start_date, end_date)`: Static method for period totals
- `get_monthly_average(household_id, months=6)`: Static method for average calculations

---

### 3. Goal Model (`patriot/backend/models/goal.py`)

**Purpose**: Track financial objectives and progress toward achieving them.

**Key Features**:
- Target amount and date tracking
- Current progress monitoring
- Priority levels
- Link to funds or dedicated accounts
- Automatic completion detection
- Progress analytics

**Fields**:
- `id`: Primary key
- `household_id`: Foreign key to Household
- `created_by_user_id`: Foreign key to User
- `name`: Goal name
- `description`: Detailed description
- `target_amount`: Target amount to achieve
- `current_amount`: Current progress amount
- `target_date`: Optional deadline
- `start_date`: Goal start date
- `category`: Goal category (emergency_fund, vacation, etc.)
- `priority`: Priority level (low, medium, high, critical)
- `fund_id`: Foreign key to Fund (optional)
- `account_id`: Foreign key to Account (optional)
- `is_active`: Active status
- `is_completed`: Completion status
- `completed_at`: Completion timestamp
- `icon`: Icon for UI
- `color`: Color code for UI
- `notes`: Additional notes
- `created_at`: Timestamp
- `updated_at`: Last update timestamp

**Relationships**:
- `household`: Many-to-one with Household
- `created_by`: Many-to-one with User
- `fund`: Many-to-one with Fund
- `account`: Many-to-one with Account
- `savings_records`: One-to-many with Savings

**Properties**:
- `progress_percentage`: Calculated progress as percentage
- `amount_remaining`: Amount needed to reach goal
- `days_remaining`: Days until target date
- `days_elapsed`: Days since goal started
- `recommended_monthly_contribution`: Suggested monthly amount

**Methods**:
- `to_dict()`: Serialize to dictionary with calculated fields
- `add_contribution(amount)`: Add funds and auto-complete if target reached
- `withdraw(amount)`: Withdraw funds and update completion status
- `get_active_goals(household_id)`: Static method for active goals
- `get_completed_goals(household_id)`: Static method for completed goals

---

### 4. Saving Model (`patriot/backend/models/saving.py`)

**Purpose**: Track savings deposits, withdrawals, and progress.

**Key Features**:
- Link to goals, funds, and accounts
- Track different transaction types
- Support for automatic transfers
- Recurring savings tracking
- Comprehensive savings analytics

**Fields**:
- `id`: Primary key
- `household_id`: Foreign key to Household
- `created_by_user_id`: Foreign key to User
- `account_id`: Foreign key to Account (optional)
- `fund_id`: Foreign key to Fund (optional)
- `goal_id`: Foreign key to Goal (optional)
- `category_id`: Foreign key to Category (optional)
- `date`: Transaction date
- `amount`: Transaction amount
- `transaction_type`: Type (deposit, withdrawal, interest)
- `source`: Source of savings
- `description`: Transaction description
- `is_recurring`: Recurring transaction flag
- `is_automatic`: Auto-transfer flag
- `notes`: Additional notes
- `created_at`: Timestamp
- `updated_at`: Last update timestamp

**Relationships**:
- `household`: Many-to-one with Household
- `created_by`: Many-to-one with User
- `account`: Many-to-one with Account
- `fund`: Many-to-one with Fund
- `goal`: Many-to-one with Goal
- `category`: Many-to-one with Category

**Methods**:
- `to_dict()`: Serialize to dictionary
- `get_total_for_period(household_id, start_date, end_date, transaction_type)`: Static method for totals
- `get_net_savings(household_id, start_date, end_date)`: Static method for net savings
- `get_savings_rate(household_id, start_date, end_date)`: Static method for savings rate
- `get_monthly_average(household_id, months=6)`: Static method for averages
- `get_by_goal(household_id, goal_id)`: Static method for goal-specific savings
- `get_by_fund(household_id, fund_id)`: Static method for fund-specific savings

---

## Existing Models (Updated)

### Account Model
- Enhanced with relationships to Expenses, Goals, and Savings
- Updated to support new financial tracking features

### Income Model
- Added `get_total_for_period()` static method for period calculations
- Now supports savings rate calculations

### Fund Model
- Enhanced relationships with Goals and Savings
- Existing functionality preserved

### Bill Model
- Enhanced relationship with Expenses
- Existing functionality preserved

---

## Database Schema Relationships

```
Household
  ├── Users
  ├── Accounts
  │   ├── Expenses
  │   ├── Goals
  │   ├── Savings
  │   ├── Funds
  │   └── Bills
  ├── Categories (hierarchical)
  │   ├── Subcategories
  │   ├── Expenses
  │   └── Savings
  ├── Expenses
  │   ├── Created by User
  │   ├── From Account
  │   ├── In Category
  │   └── For Bill
  ├── Goals
  │   ├── Created by User
  │   ├── Linked to Fund
  │   ├── Linked to Account
  │   └── Savings records
  ├── Savings
  │   ├── Created by User
  │   ├── To Account
  │   ├── For Fund
  │   ├── For Goal
  │   └── In Category
  ├── Funds
  ├── Bills
  ├── Debts
  └── Transactions
```

---

## Migration Instructions

### Generate Migration

```bash
python3 generate_new_models_migration.py
```

This will create a new Alembic migration file with all the new tables and relationships.

### Apply Migration

```bash
python3 apply_new_migration.py
```

This will apply the migration to your database, creating the new tables:
- `categories`
- `expenses`
- `goals`
- `savings`

### Test Models

```bash
python3 test_new_models.py
```

This comprehensive test script will:
1. Create test data for all models
2. Verify relationships between models
3. Test model methods and properties
4. Validate data serialization
5. Clean up test data

---

## Usage Examples

### Creating a Category with Subcategories

```python
# Create parent category
housing = Category(
    household_id=household.id,
    name="Housing",
    category_type="expense",
    icon="🏠",
    budget_amount=1500.00
)
db.session.add(housing)
db.session.flush()

# Create subcategories
rent = Category(
    household_id=household.id,
    name="Rent",
    category_type="expense",
    parent_id=housing.id,
    budget_amount=1200.00
)
db.session.add(rent)
db.session.commit()

# Access hierarchy
print(rent.full_name)  # "Housing > Rent"
print(len(housing.subcategories))  # 1
```

### Tracking an Expense

```python
expense = Expense(
    household_id=household.id,
    created_by_user_id=user.id,
    account_id=checking_account.id,
    category_id=groceries_category.id,
    date=date.today(),
    amount=125.50,
    description="Weekly groceries",
    merchant="Whole Foods",
    payment_method="credit",
    tags="food,groceries,weekly"
)
db.session.add(expense)
db.session.commit()

# Query expenses
total = Expense.get_total_for_period(
    household.id,
    start_date=first_of_month,
    end_date=today
)
```

### Managing a Financial Goal

```python
# Create a goal
vacation_goal = Goal(
    household_id=household.id,
    created_by_user_id=user.id,
    name="European Vacation",
    target_amount=5000.00,
    current_amount=1500.00,
    target_date=date(2026, 6, 1),
    category="vacation",
    priority="high",
    icon="✈️"
)
db.session.add(vacation_goal)
db.session.commit()

# Add contribution
vacation_goal.add_contribution(250.00)
db.session.commit()

# Check progress
print(f"Progress: {vacation_goal.progress_percentage:.1f}%")
print(f"Remaining: ${vacation_goal.amount_remaining}")
print(f"Recommended monthly: ${vacation_goal.recommended_monthly_contribution:.2f}")
```

### Recording Savings

```python
# Record a savings deposit
saving = Saving(
    household_id=household.id,
    created_by_user_id=user.id,
    account_id=savings_account.id,
    goal_id=vacation_goal.id,
    date=date.today(),
    amount=250.00,
    transaction_type="deposit",
    source="Paycheck",
    description="Monthly automatic savings",
    is_automatic=True,
    is_recurring=True
)
db.session.add(saving)
db.session.commit()

# Calculate savings metrics
net_savings = Saving.get_net_savings(
    household.id,
    start_date=first_of_month,
    end_date=today
)
savings_rate = Saving.get_savings_rate(
    household.id,
    start_date=first_of_month,
    end_date=today
)
print(f"Net savings: ${net_savings}")
print(f"Savings rate: {savings_rate:.1f}%")
```

---

## API Integration

These models are ready for API integration. Consider creating the following routes:

### Categories API
- `GET /api/categories` - List all categories
- `POST /api/categories` - Create category
- `GET /api/categories/<id>` - Get category details
- `PUT /api/categories/<id>` - Update category
- `DELETE /api/categories/<id>` - Delete category
- `GET /api/categories/defaults` - Get default category structures

### Expenses API
- `GET /api/expenses` - List expenses (with filters)
- `POST /api/expenses` - Create expense
- `GET /api/expenses/<id>` - Get expense details
- `PUT /api/expenses/<id>` - Update expense
- `DELETE /api/expenses/<id>` - Delete expense
- `GET /api/expenses/stats` - Get expense statistics
- `GET /api/expenses/by-category` - Group by category

### Goals API
- `GET /api/goals` - List goals
- `POST /api/goals` - Create goal
- `GET /api/goals/<id>` - Get goal details
- `PUT /api/goals/<id>` - Update goal
- `DELETE /api/goals/<id>` - Delete goal
- `POST /api/goals/<id>/contribute` - Add contribution
- `POST /api/goals/<id>/withdraw` - Withdraw from goal
- `GET /api/goals/active` - Get active goals
- `GET /api/goals/completed` - Get completed goals

### Savings API
- `GET /api/savings` - List savings transactions
- `POST /api/savings` - Create savings record
- `GET /api/savings/<id>` - Get savings details
- `PUT /api/savings/<id>` - Update savings
- `DELETE /api/savings/<id>` - Delete savings
- `GET /api/savings/stats` - Get savings statistics
- `GET /api/savings/rate` - Get savings rate

---

## Next Steps

1. **Run migrations** to create the database tables
2. **Run tests** to verify everything works correctly
3. **Create API routes** for the new models
4. **Update frontend** to use the new models
5. **Add data validation** and business logic
6. **Implement reporting** features using the new analytics methods

---

## Notes

- All models include comprehensive `to_dict()` methods for easy API serialization
- Static methods provide powerful analytics capabilities
- Relationships are properly defined for efficient queries
- Models include helpful properties for calculated fields
- All timestamps are in UTC
- Foreign keys maintain referential integrity
- Models support soft deletion through `is_active` flags where appropriate

---

**Implementation Date**: January 6, 2026
**Version**: 1.0
**Status**: ✅ Complete and Ready for Testing

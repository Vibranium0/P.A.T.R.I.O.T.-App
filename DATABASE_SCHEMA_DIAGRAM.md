# P.A.T.R.I.O.T. Database Models - Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           P.A.T.R.I.O.T. DATABASE SCHEMA                        │
└─────────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────┐
                              │  Household   │
                              │──────────────│
                              │ id (PK)      │
                              │ name         │
                              │ created_at   │
                              └──────┬───────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
            ┌───────▼──────┐  ┌──────▼──────┐  ┌────▼──────┐
            │    Users      │  │  Accounts   │  │Categories │ ◄────┐
            │──────────────│  │─────────────│  │───────────│      │
            │ id (PK)      │  │ id (PK)     │  │ id (PK)   │      │ self
            │ name         │  │ household_id│  │ household │      │ reference
            │ email        │  │ owner_id    │  │ name      │      │
            │ household_id │  │ name        │  │ parent_id │──────┘
            └───────┬──────┘  │ type        │  │ type      │
                    │         │ balance     │  │ budget    │
                    │         └──────┬──────┘  └─────┬─────┘
                    │                │               │
       ┌────────────┼────────────────┼───────────────┼──────────────┐
       │            │                │               │              │
  ┌────▼─────┐ ┌───▼──────┐   ┌─────▼──────┐  ┌────▼────────┐ ┌──▼────────┐
  │ Expenses │ │  Goals   │   │  Savings   │  │   Income    │ │   Funds   │
  │──────────│ │──────────│   │────────────│  │─────────────│ │───────────│
  │ id (PK)  │ │ id (PK)  │   │ id (PK)    │  │ id (PK)     │ │ id (PK)   │
  │household │ │household │   │household   │  │household    │ │household  │
  │user_id   │ │user_id   │   │user_id     │  │date         │ │name       │
  │account_id│ │account_id│   │account_id  │  │amount       │ │balance    │
  │category  │ │fund_id   │   │fund_id     │  │source       │ │goal       │
  │bill_id   │ │name      │   │goal_id     │  │category     │ │account_id │
  │date      │ │target    │   │category    │  │account_id   │ │type       │
  │amount    │ │current   │   │date        │  └─────────────┘ └───────────┘
  │merchant  │ │target_dt │   │amount      │
  │payment   │ │priority  │   │type        │
  │tags      │ │is_active │   │is_auto     │
  │receipt   │ │completed │   │recurring   │
  └──┬───────┘ └──────────┘   └────────────┘
     │
     │ linked to
     │
  ┌──▼───────┐
  │  Bills   │
  │──────────│
  │ id (PK)  │
  │household │
  │name      │
  │amount    │
  │due_date  │
  │frequency │
  │account_id│
  └──────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│                            KEY RELATIONSHIPS                                     │
└─────────────────────────────────────────────────────────────────────────────────┘

HOUSEHOLD → has many:
  ├─ Users
  ├─ Accounts
  ├─ Categories
  ├─ Expenses
  ├─ Goals
  ├─ Savings
  ├─ Income
  ├─ Funds
  ├─ Bills
  ├─ Debts
  └─ Transactions

USER → creates:
  ├─ Expenses
  ├─ Goals
  ├─ Savings
  └─ Transactions

ACCOUNT → linked to:
  ├─ Expenses
  ├─ Goals
  ├─ Savings
  ├─ Income
  ├─ Funds
  └─ Bills

CATEGORY → organizes:
  ├─ Expenses
  ├─ Savings
  ├─ Income
  └─ Subcategories (self-reference)

GOAL → tracks:
  ├─ Savings (progress)
  ├─ Fund (optional)
  └─ Account (optional)

EXPENSE → can link to:
  ├─ Bill (if recurring)
  ├─ Category
  └─ Account

SAVING → can link to:
  ├─ Goal (contribution)
  ├─ Fund (allocation)
  ├─ Category
  └─ Account


┌─────────────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW EXAMPLES                                       │
└─────────────────────────────────────────────────────────────────────────────────┘

1. EXPENSE TRACKING FLOW:
   User → Creates Expense → Links to Account → Categorized → Optionally Bills

2. SAVINGS GOAL FLOW:
   User → Creates Goal → Makes Savings (deposits) → Goal tracks progress → Auto-complete

3. BUDGET TRACKING FLOW:
   Category → Set budget_amount → Expenses → Calculate totals → Compare to budget

4. INCOME TO SAVINGS FLOW:
   Income received → Account balance updated → Automatic Saving → Goal contribution

5. HIERARCHICAL CATEGORIES:
   Parent Category (Housing) → Subcategories (Rent, Utilities) → Expenses


┌─────────────────────────────────────────────────────────────────────────────────┐
│                        MODEL FEATURES MATRIX                                     │
└─────────────────────────────────────────────────────────────────────────────────┘

Model      │ Analytics │ Tracking │ Relations │ Auto-calc │ Status
───────────┼───────────┼──────────┼───────────┼───────────┼────────
Category   │    ✓      │    ✓     │    ✓✓     │    -      │  New
Expense    │   ✓✓✓     │   ✓✓✓    │   ✓✓✓     │    ✓      │  New
Goal       │   ✓✓      │   ✓✓✓    │   ✓✓      │   ✓✓✓     │  New
Saving     │   ✓✓✓     │   ✓✓     │   ✓✓✓     │   ✓✓      │  New
Account    │    ✓      │    ✓     │   ✓✓✓     │    ✓      │Enhanced
Income     │    ✓      │    ✓     │    ✓      │    -      │Enhanced
Fund       │    ✓      │    ✓     │    ✓      │    ✓      │Existing
Bill       │    ✓      │    ✓     │    ✓      │    ✓      │Existing
Debt       │   ✓✓      │    ✓     │    ✓      │    ✓      │Existing


┌─────────────────────────────────────────────────────────────────────────────────┐
│                       FIELD TYPE LEGEND                                          │
└─────────────────────────────────────────────────────────────────────────────────┘

Integer      : id, foreign keys, counts
Numeric      : monetary amounts (precision=15, scale=2)
String       : names, descriptions, enums
Text         : long notes, descriptions
Date         : dates without time
DateTime     : timestamps with time
Boolean      : flags (is_active, is_recurring, etc.)
Float        : percentages, rates (use Numeric for money)


┌─────────────────────────────────────────────────────────────────────────────────┐
│                      QUERY PATTERNS                                              │
└─────────────────────────────────────────────────────────────────────────────────┘

Get all expenses for a household:
  Expense.query.filter_by(household_id=hh_id).all()

Get expenses by category for date range:
  Expense.get_total_by_category(hh_id, start_date, end_date)

Get active goals with progress:
  Goal.get_active_goals(hh_id)
  [goal.progress_percentage for goal in goals]

Calculate savings rate:
  Saving.get_savings_rate(hh_id, start_date, end_date)

Get category hierarchy:
  category.subcategories  # Children
  category.parent         # Parent
  category.full_name      # "Parent > Child"

Track goal contributions:
  goal.add_contribution(amount)
  goal.progress_percentage  # Auto-calculated


┌─────────────────────────────────────────────────────────────────────────────────┐
│                     INDEX RECOMMENDATIONS                                        │
└─────────────────────────────────────────────────────────────────────────────────┘

Categories:
  - (household_id, category_type)
  - (parent_id) for hierarchy queries

Expenses:
  - (household_id, date) for date ranges
  - (category_id, date) for category analysis
  - (account_id) for account history

Goals:
  - (household_id, is_active, is_completed) for filtering
  - (target_date) for deadline queries

Savings:
  - (household_id, date, transaction_type) for analytics
  - (goal_id) for goal tracking
  - (fund_id) for fund tracking

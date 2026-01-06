# P.A.T.R.I.O.T. API Endpoints Documentation

## Overview
Complete CRUD API endpoints for all P.A.T.R.I.O.T. financial models. All endpoints require JWT authentication and automatically filter data by the authenticated user's household.

---

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

---

## 1. Categories API (`/api/categories`)

### List Categories
**GET** `/api/categories`

**Query Parameters:**
- `type` (string): Filter by category type (income/expense)
- `parent_id` (int): Filter by parent category ID
- `include_inactive` (boolean): Include inactive categories (default: false)

**Response:**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Housing",
      "type": "expense",
      "parent_id": null,
      "subcategories": [...],
      "is_active": true,
      "icon": "🏠",
      "color": "#3b82f6"
    }
  ],
  "count": 1
}
```

### Get Single Category
**GET** `/api/categories/<id>`

### Create Category
**POST** `/api/categories`

**Request Body:**
```json
{
  "name": "Groceries",
  "type": "expense",
  "parent_id": 1,
  "icon": "🛒",
  "color": "#10b981",
  "description": "Food and household items"
}
```

### Update Category
**PUT** `/api/categories/<id>`

### Delete Category (Soft Delete)
**DELETE** `/api/categories/<id>`

### Get Default Categories
**GET** `/api/categories/defaults`

### Create Default Categories
**POST** `/api/categories/defaults/create`

---

## 2. Expenses API (`/api/expenses`)

### List Expenses
**GET** `/api/expenses`

**Query Parameters:**
- `category_id` (int): Filter by category
- `account_id` (int): Filter by account
- `start_date` (ISO date): Filter by start date
- `end_date` (ISO date): Filter by end date
- `merchant` (string): Filter by merchant name
- `min_amount` (decimal): Minimum amount
- `max_amount` (decimal): Maximum amount
- `sort_by` (string): Sort field (date/amount, default: date)
- `order` (string): Sort order (asc/desc, default: desc)

**Response:**
```json
{
  "expenses": [
    {
      "id": 1,
      "amount": 150.00,
      "date": "2024-01-15",
      "merchant": "Whole Foods",
      "category": {...},
      "account": {...},
      "description": "Weekly groceries"
    }
  ],
  "count": 1
}
```

### Get Single Expense
**GET** `/api/expenses/<id>`

### Create Expense
**POST** `/api/expenses`

**Request Body:**
```json
{
  "amount": 150.00,
  "date": "2024-01-15",
  "merchant": "Whole Foods",
  "category_id": 5,
  "account_id": 2,
  "description": "Weekly groceries",
  "is_recurring": false,
  "receipt_url": "https://...",
  "notes": "Organic produce"
}
```

### Update Expense
**PUT** `/api/expenses/<id>`

### Delete Expense
**DELETE** `/api/expenses/<id>`

### Get Expense Statistics
**GET** `/api/expenses/stats`

**Query Parameters:**
- `start_date` (ISO date, required)
- `end_date` (ISO date, required)

**Response:**
```json
{
  "by_category": [
    {
      "category_id": 5,
      "category_name": "Groceries",
      "total": 600.00
    }
  ],
  "monthly_average": 450.00,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

---

## 3. Goals API (`/api/goals`)

### List Goals
**GET** `/api/goals`

**Query Parameters:**
- `is_active` (boolean): Filter active goals
- `is_completed` (boolean): Filter completed goals
- `category` (string): Filter by goal category
- `priority` (string): Filter by priority (low/medium/high)

**Response:**
```json
{
  "goals": [
    {
      "id": 1,
      "name": "Emergency Fund",
      "target_amount": 10000.00,
      "current_amount": 5000.00,
      "progress_percentage": 50.0,
      "amount_remaining": 5000.00,
      "target_date": "2024-12-31",
      "is_completed": false
    }
  ],
  "count": 1
}
```

### Get Active Goals
**GET** `/api/goals/active`

### Get Completed Goals
**GET** `/api/goals/completed`

### Get Single Goal
**GET** `/api/goals/<id>`

### Create Goal
**POST** `/api/goals`

**Request Body:**
```json
{
  "name": "Emergency Fund",
  "description": "6 months of expenses",
  "target_amount": 10000.00,
  "current_amount": 0.00,
  "target_date": "2024-12-31",
  "category": "savings",
  "priority": "high",
  "account_id": 2,
  "fund_id": null,
  "icon": "🏦",
  "color": "#ef4444"
}
```

### Update Goal
**PUT** `/api/goals/<id>`

### Delete Goal
**DELETE** `/api/goals/<id>`

### Add Contribution to Goal
**POST** `/api/goals/<id>/contribute`

**Request Body:**
```json
{
  "amount": 500.00
}
```

### Withdraw from Goal
**POST** `/api/goals/<id>/withdraw`

**Request Body:**
```json
{
  "amount": 200.00
}
```

---

## 4. Savings API (`/api/savings`)

### List Savings Transactions
**GET** `/api/savings`

**Query Parameters:**
- `account_id` (int): Filter by account
- `fund_id` (int): Filter by fund
- `goal_id` (int): Filter by goal
- `transaction_type` (string): Filter by type (deposit/withdrawal/interest)
- `start_date` (ISO date): Filter by start date
- `end_date` (ISO date): Filter by end date
- `sort_by` (string): Sort field (date/amount, default: date)
- `order` (string): Sort order (asc/desc, default: desc)

**Response:**
```json
{
  "savings": [
    {
      "id": 1,
      "amount": 500.00,
      "date": "2024-01-15",
      "transaction_type": "deposit",
      "source": "Paycheck",
      "account": {...},
      "goal": {...}
    }
  ],
  "count": 1
}
```

### Get Single Savings Transaction
**GET** `/api/savings/<id>`

### Create Savings Transaction
**POST** `/api/savings`

**Request Body:**
```json
{
  "amount": 500.00,
  "date": "2024-01-15",
  "transaction_type": "deposit",
  "source": "Paycheck",
  "account_id": 2,
  "fund_id": null,
  "goal_id": 1,
  "category_id": null,
  "description": "Monthly savings contribution",
  "is_recurring": true,
  "is_automatic": true,
  "notes": "Automatic transfer"
}
```

### Update Savings Transaction
**PUT** `/api/savings/<id>`

### Delete Savings Transaction
**DELETE** `/api/savings/<id>`

### Get Savings Statistics
**GET** `/api/savings/stats`

**Query Parameters:**
- `start_date` (ISO date, required)
- `end_date` (ISO date, required)

**Response:**
```json
{
  "net_savings": 5000.00,
  "deposits": 6000.00,
  "withdrawals": 1000.00,
  "interest": 100.00,
  "savings_rate": 0.25,
  "monthly_average": 833.33,
  "start_date": "2024-01-01",
  "end_date": "2024-06-30"
}
```

### Get Savings by Goal
**GET** `/api/savings/by-goal/<goal_id>`

### Get Savings by Fund
**GET** `/api/savings/by-fund/<fund_id>`

---

## 5. Income API (`/api/income`)

### List Income Entries
**GET** `/api/income`

**Query Parameters:**
- `start_date` (ISO date): Filter by start date
- `end_date` (ISO date): Filter by end date
- `source` (string): Filter by income source
- `is_recurring` (boolean): Filter recurring income
- `sort_by` (string): Sort field
- `order` (string): Sort order

**Response:**
```json
{
  "income": [
    {
      "id": 1,
      "amount": 5000.00,
      "date": "2024-01-31",
      "source": "Salary",
      "account": {...},
      "is_recurring": true
    }
  ],
  "count": 1
}
```

### Get Single Income
**GET** `/api/income/<id>`

### Create Income
**POST** `/api/income`

### Update Income
**PUT** `/api/income/<id>`

### Delete Income
**DELETE** `/api/income/<id>`

---

## 6. Accounts API (`/api/financial-accounts`)

### List Accounts
**GET** `/api/financial-accounts`

**Response:**
```json
{
  "accounts": [
    {
      "id": 1,
      "name": "Checking Account",
      "account_type": "checking",
      "institution": "Chase Bank",
      "balance": 5000.00,
      "is_active": true
    }
  ],
  "count": 1
}
```

### Get Single Account
**GET** `/api/financial-accounts/<id>`

### Create Account
**POST** `/api/financial-accounts`

### Update Account
**PUT** `/api/financial-accounts/<id>`

### Delete Account
**DELETE** `/api/financial-accounts/<id>`

---

## Error Responses

All endpoints follow a consistent error response format:

```json
{
  "error": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `404` - Not Found
- `500` - Internal Server Error

---

## Data Isolation

**Important:** All endpoints automatically filter data by the authenticated user's household. Users can only access and modify data belonging to their household. This ensures complete data isolation between different households in the system.

---

## Best Practices

1. **Date Format**: Use ISO 8601 format for all dates: `YYYY-MM-DD`
2. **Authentication**: Always include JWT token in Authorization header
3. **Validation**: Foreign key references (category_id, account_id, etc.) are validated to ensure they belong to the user's household
4. **Error Handling**: Check error responses for validation failures
5. **Filtering**: Use query parameters to filter and sort large datasets
6. **Statistics**: Use stats endpoints for analytics and reporting

---

## Example Usage

### Create an Expense with cURL

```bash
curl -X POST https://api.patriot.app/api/expenses \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 150.00,
    "date": "2024-01-15",
    "merchant": "Whole Foods",
    "category_id": 5,
    "account_id": 2,
    "description": "Weekly groceries"
  }'
```

### Get Expense Statistics

```bash
curl -X GET "https://api.patriot.app/api/expenses/stats?start_date=2024-01-01&end_date=2024-12-31" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Add Contribution to Goal

```bash
curl -X POST https://api.patriot.app/api/goals/1/contribute \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500.00
  }'
```

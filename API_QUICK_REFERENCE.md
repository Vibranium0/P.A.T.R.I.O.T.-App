# P.A.T.R.I.O.T. API Quick Reference

## Base URL
```
http://localhost:5000/api
```

## Authentication
All requests require JWT token:
```
Authorization: Bearer <token>
```

---

## Categories `/categories`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all categories |
| GET | `/<id>` | Get single category |
| POST | `/` | Create category |
| PUT | `/<id>` | Update category |
| DELETE | `/<id>` | Delete category (soft) |
| GET | `/defaults` | Get default templates |
| POST | `/defaults/create` | Create defaults for household |

**Common Filters:** `?type=expense&parent_id=1&include_inactive=false`

---

## Expenses `/expenses`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all expenses |
| GET | `/<id>` | Get single expense |
| POST | `/` | Create expense |
| PUT | `/<id>` | Update expense |
| DELETE | `/<id>` | Delete expense |
| GET | `/stats` | Get statistics |

**Common Filters:** `?category_id=1&start_date=2024-01-01&end_date=2024-12-31&sort_by=amount&order=desc`

**Stats Required:** `?start_date=2024-01-01&end_date=2024-12-31`

---

## Goals `/goals`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all goals |
| GET | `/active` | List active goals |
| GET | `/completed` | List completed goals |
| GET | `/<id>` | Get single goal |
| POST | `/` | Create goal |
| PUT | `/<id>` | Update goal |
| DELETE | `/<id>` | Delete goal |
| POST | `/<id>/contribute` | Add contribution |
| POST | `/<id>/withdraw` | Withdraw from goal |

**Common Filters:** `?is_active=true&priority=high&category=savings`

---

## Savings `/savings`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all transactions |
| GET | `/<id>` | Get single transaction |
| POST | `/` | Create transaction |
| PUT | `/<id>` | Update transaction |
| DELETE | `/<id>` | Delete transaction |
| GET | `/stats` | Get statistics |
| GET | `/by-goal/<goal_id>` | Get by goal |
| GET | `/by-fund/<fund_id>` | Get by fund |

**Common Filters:** `?transaction_type=deposit&start_date=2024-01-01&goal_id=1`

**Stats Required:** `?start_date=2024-01-01&end_date=2024-12-31`

**Transaction Types:** `deposit`, `withdrawal`, `interest`

---

## Income `/income`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all income |
| GET | `/<id>` | Get single income |
| POST | `/` | Create income |
| PUT | `/<id>` | Update income |
| DELETE | `/<id>` | Delete income |

**Common Filters:** `?start_date=2024-01-01&is_recurring=true&source=Salary`

---

## Accounts `/financial-accounts`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all accounts |
| GET | `/<id>` | Get single account |
| POST | `/` | Create account |
| PUT | `/<id>` | Update account |
| DELETE | `/<id>` | Delete account |

---

## Quick Examples

### Get JWT Token
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'
```

### Create Default Categories
```bash
curl -X POST http://localhost:5000/api/categories/defaults/create \
  -H "Authorization: Bearer $TOKEN"
```

### Create Expense
```bash
curl -X POST http://localhost:5000/api/expenses \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 150.00,
    "date": "2024-01-15",
    "merchant": "Whole Foods",
    "category_id": 1,
    "account_id": 1,
    "description": "Groceries"
  }'
```

### Create Goal
```bash
curl -X POST http://localhost:5000/api/goals \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Emergency Fund",
    "target_amount": 10000.00,
    "target_date": "2024-12-31",
    "priority": "high"
  }'
```

### Add Contribution
```bash
curl -X POST http://localhost:5000/api/goals/1/contribute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 500.00}'
```

### Get Expense Stats
```bash
curl -X GET "http://localhost:5000/api/expenses/stats?start_date=2024-01-01&end_date=2024-12-31" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Savings Stats
```bash
curl -X GET "http://localhost:5000/api/savings/stats?start_date=2024-01-01&end_date=2024-12-31" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Response Format

### Success (200/201)
```json
{
  "message": "Success message",
  "data": {...}
}
```

### Error (400/404/500)
```json
{
  "error": "Error message"
}
```

---

## Date Format
Always use ISO 8601: `YYYY-MM-DD`

Example: `2024-01-15`

---

## Common Status Codes

- `200` OK - Success
- `201` Created - Resource created
- `400` Bad Request - Validation error
- `404` Not Found - Resource not found
- `500` Internal Server Error - Server error

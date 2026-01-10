# Enhanced Funds API Documentation

## Overview
The updated `funds_bp` Blueprint provides comprehensive management of user funds with goal tracking, automatic balance updates, and tight integration with the transaction system.

## Core Endpoints (As Requested)

### `GET /funds`
- **Description**: List all user funds
- **Authentication**: JWT required
- **Response**: Array of fund objects with goal tracking
- **Features**: Ordered by creation date (newest first)

### `POST /funds`
- **Description**: Create a new fund
- **Authentication**: JWT required
- **Required Fields**:
  - `name` (string) - Fund name
- **Optional Fields**:
  - `balance` (float, defaults to 0.0) - Initial balance
  - `goal` (float, defaults to 0.0) - Target amount
- **Validation**: 
  - Prevents duplicate names per user
  - Validates positive numbers for balance/goal

### `PATCH /funds/<id>`
- **Description**: Edit name, goal, or balance
- **Authentication**: JWT required
- **Updatable Fields**:
  - `name` (string)
  - `goal` (float)
  - `balance` (float)
- **Features**: Partial updates supported, validates ownership

### `DELETE /funds/<id>`
- **Description**: Delete a fund
- **Authentication**: JWT required
- **Safety**: Prevents deletion if fund has linked transactions
- **Response**: Error message with transaction count if deletion blocked

### `GET /funds/<id>/transactions`
- **Description**: Return all transactions linked to a fund
- **Authentication**: JWT required
- **Response**: Fund details + array of transactions
- **Features**: Transactions ordered by date (newest first)

## Additional Utility Endpoints

### `GET /funds/<id>`
- **Description**: Get detailed fund information
- **Response**: Fund data + transaction count + goal progress

### `GET /funds/summary`
- **Description**: Get overview of all user funds
- **Response**: Aggregated statistics and fund list
- **Features**: 
  - Total balance across all funds
  - Total goal amount
  - Overall progress percentage
  - Funds with goals count

### `POST /funds/<id>/deposit`
- **Description**: Direct deposit to fund (alternative to transaction)
- **Required Fields**: `amount` (positive float)
- **Features**: Updates fund balance using safe `add_funds()` method

### `POST /funds/<id>/withdraw`
- **Description**: Direct withdrawal from fund (alternative to transaction)
- **Required Fields**: `amount` (positive float)
- **Features**: 
  - Validates sufficient balance
  - Uses safe `withdraw_funds()` method
  - Returns previous and new balance

## Enhanced Features

### 1. **Goal Tracking Integration**
- Every fund now supports optional goal setting
- Automatic progress percentage calculation
- Amount remaining to goal calculation
- Goal validation (non-negative values)

### 2. **Automatic Balance Management**
- Fund balances update automatically when transactions are created/updated/deleted
- Integration with enhanced Transaction model
- Safe withdrawal validation (prevents negative balances)

### 3. **Transaction Safety**
- Prevents fund deletion if transactions exist
- Shows transaction count in fund details
- Proper error handling with transaction counts

### 4. **Enhanced Fund Model Integration**
- Uses `fund.to_dict()` for consistent JSON responses
- Leverages fund properties (`progress_percentage`, `amount_to_goal`)
- Uses fund methods (`add_funds()`, `withdraw_funds()`)

### 5. **Comprehensive Validation**
- User ownership verification
- Duplicate name prevention
- Positive amount validation
- Proper error handling with detailed messages

## Example Usage

### Create a Fund
```json
POST /funds
{
  "name": "Emergency Fund",
  "balance": 1000.0,
  "goal": 10000.0
}
```

### Update Fund Goal
```json
PATCH /funds/1
{
  "goal": 15000.0
}
```

### Get Fund with Transactions
```json
GET /funds/1/transactions
// Response:
{
  "fund": {
    "id": 1,
    "name": "Emergency Fund",
    "balance": 1500.0,
    "goal": 10000.0,
    "progress_percentage": 15.0
  },
  "transaction_count": 5,
  "transactions": [...]
}
```

### Funds Summary
```json
GET /funds/summary
// Response:
{
  "fund_count": 3,
  "total_balance": 5000.0,
  "total_goal": 25000.0,
  "overall_progress_percentage": 20.0,
  "funds_with_goals": 2,
  "funds": [...]
}
```

## Integration with Transactions

### Automatic Balance Updates
When transactions are created/updated/deleted through the Transaction API:
- If `fund_id` is specified, fund balance updates automatically
- Income transactions add to fund balance
- Expense transactions subtract from fund balance
- Failed transactions don't affect fund balances (proper rollback)

### Transaction Validation
- Fund ownership verified before linking transactions
- Sufficient balance checked for expense transactions
- Prevents fund deletion if transactions exist

## Migration Notes

### Changes from Previous Version:
- ❌ Removed `fund_type` field (was 'savings', 'checking', etc.)
- ❌ Removed `Decimal` usage for balance
- ✅ Added `goal` field for target amounts
- ✅ Changed to `Float` for balance and goal
- ✅ Added goal tracking properties and methods
- ✅ Enhanced validation and error handling

### Database Impact:
The Fund model structure has changed significantly. You may need to:
1. Drop and recreate the funds table, OR
2. Create a migration script to update existing funds, OR
3. Manually update existing fund records to add goal field

## API Benefits

1. **Goal-Oriented Savings**: Users can set and track progress toward financial goals
2. **Automatic Sync**: Fund balances stay synchronized with transactions
3. **Safety Features**: Prevents data loss and invalid operations
4. **Comprehensive Views**: Multiple ways to view and manage funds
5. **Flexible Operations**: Direct fund operations or transaction-based changes

The enhanced Funds API provides a robust foundation for personal financial management! 💰
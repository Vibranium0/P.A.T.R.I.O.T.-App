# Enhanced Transactions API Documentation

## Overview
The new `transactions_bp` Blueprint provides comprehensive CRUD operations for transactions using the enhanced Transaction model with automatic fund balance management and autopay functionality.

## Endpoints

### Core CRUD Operations

#### `GET /transactions`
- **Description**: Returns all user transactions
- **Authentication**: JWT required
- **Response**: Array of transaction objects with all fields (user_id, amount, category, fund_id, bill_id, etc.)

#### `POST /transactions`
- **Description**: Creates a new transaction with automatic fund balance updates
- **Authentication**: JWT required
- **Required Fields**:
  - `amount` (Decimal)
  - `description` (string)
  - `category` (string)
- **Optional Fields**:
  - `transaction_type` ('income', 'expense', 'transfer' - defaults to 'expense')
  - `fund_id` (integer, nullable)
  - `bill_id` (integer, nullable)
  - `is_autopay` (boolean, defaults to false)
  - `date` (ISO date string, defaults to today)
- **Features**:
  - Automatically updates fund balance if fund_id provided
  - Validates fund ownership and sufficient balance for expenses
  - Validates bill ownership if bill_id provided

#### `POST /transactions/auto-generate`
- **Description**: Creates autopay transactions for bills due today or earlier
- **Authentication**: JWT required
- **Features**:
  - Finds bills marked as `is_autopay=True` and `due_date <= today`
  - Prevents duplicate autopay transactions for the same day
  - Creates expense transactions linked to bills
  - Returns count and details of created transactions

#### `GET /transactions/<id>`
- **Description**: Get a specific transaction
- **Authentication**: JWT required
- **Validation**: Ensures user owns the transaction

#### `PUT /transactions/<id>`
- **Description**: Update a transaction with automatic fund balance adjustment
- **Authentication**: JWT required
- **Features**:
  - Reverts original fund balance changes
  - Applies new fund balance changes
  - Validates new fund ownership and balances
  - Supports updating all transaction fields

#### `DELETE /transactions/<id>`
- **Description**: Deletes a transaction and updates linked fund balance
- **Authentication**: JWT required
- **Features**:
  - Automatically reverts fund balance changes
  - Returns updated fund balance if applicable

### Additional Utility Endpoints

#### `GET /transactions/by-category`
- **Description**: Get transactions grouped by category
- **Query Parameters**:
  - `start_date` (optional, YYYY-MM-DD)
  - `end_date` (optional, YYYY-MM-DD)
- **Response**: Array of category summaries with transaction lists

#### `GET /transactions/summary`
- **Description**: Get transaction summary (income, expenses, net balance)
- **Query Parameters**:
  - `start_date` (optional, YYYY-MM-DD)
  - `end_date` (optional, YYYY-MM-DD)
- **Response**: Financial summary with totals and counts

## Enhanced Features

### 1. **Comprehensive Transaction Model**
- Links to users, funds, and bills
- Supports income, expense, and transfer types
- Includes categories for budgeting
- Autopay functionality for recurring bills

### 2. **Automatic Fund Balance Management**
- Income transactions add to fund balance
- Expense transactions subtract from fund balance
- Validates sufficient funds for expenses
- Handles balance updates for transaction modifications

### 3. **Autopay System**
- Identifies due bills marked for autopay
- Prevents duplicate autopay transactions
- Creates properly categorized expense transactions
- Links transactions to original bills

### 4. **Smart Validation**
- User ownership verification for all related entities
- Fund balance validation for expenses
- Date parsing and validation
- Amount validation with Decimal precision

### 5. **Comprehensive Error Handling**
- Proper rollback on failures
- Detailed error messages
- HTTP status codes for different scenarios

## Example Usage

### Create a Regular Transaction
```json
POST /transactions
{
  "amount": 50.00,
  "description": "Grocery shopping",
  "category": "Food",
  "transaction_type": "expense",
  "fund_id": 1
}
```

### Create Income Transaction
```json
POST /transactions
{
  "amount": 1000.00,
  "description": "Salary",
  "category": "Income",
  "transaction_type": "income",
  "fund_id": 2
}
```

### Auto-Generate Autopay Transactions
```json
POST /transactions/auto-generate
// Response:
{
  "message": "Successfully created 3 autopay transactions",
  "transactions_created": 3,
  "transactions": [...]
}
```

## Migration Benefits

1. **User-Centric**: Transactions now belong directly to users (not just funds)
2. **Flexible**: Supports fund-linked and general transactions
3. **Automated**: Autopay functionality for recurring bills
4. **Comprehensive**: Full financial tracking with categories
5. **Precise**: Uses Decimal for financial accuracy
6. **Safe**: Proper validation and error handling

The new API supports both simple budgeting transactions and complex fund management scenarios!
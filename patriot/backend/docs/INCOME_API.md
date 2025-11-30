# Income API Endpoints

## Overview
The Income API provides endpoints for managing income entries in the budgeting application. All endpoints require JWT authentication.

## Endpoints

### 1. GET /income
**Description**: Retrieve all income entries for the authenticated user

**Query Parameters**:
- `sort_by` (optional): Sort field - "date", "amount", or "source" (default: "date")
- `order` (optional): Sort order - "asc" or "desc" (default: "desc")
- `source` (optional): Filter by source (case-insensitive partial match)

**Response**:
```json
{
    "success": true,
    "income_entries": [
        {
            "id": 1,
            "user_id": "testuser",
            "date": "2025-10-22",
            "amount": 3000.0,
            "source": "Paycheck",
            "description": "Monthly salary"
        }
    ],
    "total_entries": 1,
    "total_amount": 3000.0
}
```

### 2. POST /income
**Description**: Create a new income entry

**Request Body**:
```json
{
    "amount": 3000.0,
    "source": "Paycheck",
    "description": "Monthly salary",
    "date": "2025-10-22"
}
```

**Required Fields**: `amount`, `source`
**Optional Fields**: `description`, `date` (defaults to today)

**Response**:
```json
{
    "success": true,
    "message": "Income entry created successfully",
    "income_entry": {
        "id": 1,
        "user_id": "testuser",
        "date": "2025-10-22",
        "amount": 3000.0,
        "source": "Paycheck",
        "description": "Monthly salary"
    }
}
```

### 3. DELETE /income/<id>
**Description**: Delete a specific income entry

**URL Parameters**:
- `id`: Income entry ID

**Response**:
```json
{
    "success": true,
    "message": "Income entry deleted successfully",
    "deleted_entry": {
        "id": 1,
        "user_id": "testuser",
        "date": "2025-10-22",
        "amount": 3000.0,
        "source": "Paycheck",
        "description": "Monthly salary"
    }
}
```

### 4. GET /income/summary
**Description**: Get income summary breakdown by source type

**Query Parameters**:
- `start_date` (optional): Filter from date (YYYY-MM-DD format)
- `end_date` (optional): Filter to date (YYYY-MM-DD format)

**Response**:
```json
{
    "success": true,
    "summary": {
        "total_income": 5500.0,
        "total_entries": 3,
        "unique_sources": 2,
        "by_source": {
            "Paycheck": {
                "total_amount": 5000.0,
                "count": 2,
                "average_amount": 2500.0,
                "percentage": 90.91
            },
            "Bonus": {
                "total_amount": 500.0,
                "count": 1,
                "average_amount": 500.0,
                "percentage": 9.09
            }
        },
        "date_range": {
            "start_date": null,
            "end_date": null
        }
    }
}
```

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Error Responses
All endpoints return error responses in the following format:
```json
{
    "success": false,
    "message": "Error description"
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request (validation errors)
- 401: Unauthorized (invalid/missing JWT)
- 404: Not Found
- 500: Internal Server Error
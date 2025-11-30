from flask import Blueprint, request, jsonify
from backend.database import db
from backend.models import Transaction, Fund, Bill, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import func
from backend.utils.auth_helpers import get_current_household_id, get_current_user_id

tx_bp = Blueprint("transactions", __name__)

@tx_bp.route("/", methods=["GET"])
@jwt_required()
def list_transactions():
    """Get all transactions for the current user"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    # Get all transactions for the user, ordered by date descending
    transactions = Transaction.query.filter_by(
        household_id=household_id
    ).order_by(Transaction.date.desc()).all()
    
    return jsonify([transaction.to_dict() for transaction in transactions]), 200


@tx_bp.route("/", methods=["POST"])
@jwt_required()
def create_transaction():
    """Create a new transaction and automatically update fund balance if fund_id is provided"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    current_user_id = get_current_user_id()
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Required fields
    amount = data.get("amount")
    description = data.get("description")
    category = data.get("category")
    transaction_type = data.get("transaction_type", "expense")
    
    # Optional fields
    account_id = data.get("account_id")
    fund_id = data.get("fund_id")
    bill_id = data.get("bill_id")
    to_account_id = data.get("to_account_id")  # For transfers
    to_fund_id = data.get("to_fund_id")  # For transfers
    is_autopay = data.get("is_autopay", False)
    transaction_date = data.get("date")
    
    # Recurring transaction fields
    is_recurring = data.get("is_recurring", False)
    frequency = data.get("frequency")  # 'weekly', 'biweekly', 'monthly', 'yearly'
    
    # Validate required fields
    if amount is None:
        return jsonify({"error": "amount is required"}), 400
    
    if not description:
        return jsonify({"error": "description is required"}), 400
    
    if not category:
        return jsonify({"error": "category is required"}), 400
    
    # Validate transaction type
    valid_types = ["income", "expense", "transfer"]
    if transaction_type not in valid_types:
        return jsonify({"error": f"Invalid transaction type. Must be one of: {', '.join(valid_types)}"}), 400
    
    # Validate amount
    try:
        amount = Decimal(str(amount))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount"}), 400
    
    # Parse date if provided
    parsed_date = date.today()
    if transaction_date:
        try:
            parsed_date = datetime.fromisoformat(transaction_date.replace('Z', '+00:00')).date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use ISO format (YYYY-MM-DD)"}), 400
    
    # Validate account if provided
    from models import Account
    account = None
    if account_id:
        account = Account.query.filter_by(id=account_id, household_id=household_id).first()
        if not account:
            return jsonify({"error": "Account not found or access denied"}), 404
    
    # Validate fund if provided
    fund = None
    if fund_id:
        fund = Fund.query.filter_by(id=fund_id, household_id=household_id).first()
        if not fund:
            return jsonify({"error": "Fund not found or access denied"}), 404
        
        # For expenses and withdrawals from fund, check if fund has sufficient balance
        if transaction_type == "expense" and fund.balance < abs(amount):
            return jsonify({"error": "Insufficient fund balance"}), 400
    
    # Validate bill if provided
    bill = None
    if bill_id:
        bill = Bill.query.filter_by(id=bill_id, household_id=household_id).first()
        if not bill:
            return jsonify({"error": "Bill not found or access denied"}), 404
    
    # Validate transfer destinations if transfer
    to_account = None
    to_fund = None
    if transaction_type == "transfer":
        if not (to_account_id or to_fund_id):
            return jsonify({"error": "Transfer requires to_account_id or to_fund_id"}), 400
        
        if to_account_id:
            to_account = Account.query.filter_by(id=to_account_id, household_id=household_id).first()
            if not to_account:
                return jsonify({"error": "Destination account not found"}), 404
        
        if to_fund_id:
            to_fund = Fund.query.filter_by(id=to_fund_id, household_id=household_id).first()
            if not to_fund:
                return jsonify({"error": "Destination fund not found"}), 404
    
    try:
        # Create transaction
        transaction = Transaction(
            household_id=household_id,
            created_by_user_id=current_user_id,
            amount=amount,
            description=description,
            category=category,
            transaction_type=transaction_type,
            account_id=account_id,
            fund_id=fund_id,
            bill_id=bill_id,
            to_account_id=to_account_id,
            to_fund_id=to_fund_id,
            is_autopay=is_autopay,
            date=parsed_date,
            is_recurring=is_recurring,
            frequency=frequency if is_recurring else None
        )
        
        # Calculate next occurrence if recurring
        if is_recurring and frequency:
            transaction.next_occurrence = transaction.calculate_next_occurrence(parsed_date)
        
        # Handle balance updates based on transaction type
        # Account.balance is Numeric (Decimal), Fund.balance is Float
        amount_value = abs(amount)
        
        if transaction_type == "transfer":
            # TRANSFER: Deduct from source, add to destination
            # Deduct from source
            if account:
                account.balance -= Decimal(str(amount_value))
            elif fund:
                fund.balance -= float(amount_value)
                if fund.account:
                    fund.account.balance -= Decimal(str(amount_value))
            
            # Add to destination
            if to_account:
                to_account.balance += Decimal(str(amount_value))
            elif to_fund:
                to_fund.balance += float(amount_value)
                if to_fund.account:
                    to_fund.account.balance += Decimal(str(amount_value))
                    
        elif transaction_type == "income":
            # INCOME: Add to account or fund
            if account and not fund:
                account.balance += Decimal(str(amount_value))
            if fund:
                fund.balance += float(amount_value)
                if fund.account:
                    fund.account.balance += Decimal(str(amount_value))
                    
        elif transaction_type == "expense":
            # EXPENSE: Deduct from account or fund
            if account and not fund:
                account.balance -= Decimal(str(amount_value))
            if fund:
                fund.balance -= float(amount_value)
                if fund.account:
                    fund.account.balance -= Decimal(str(amount_value))
        
        db.session.add(transaction)
        db.session.commit()
        
        response_data = {
            "message": "Transaction created successfully",
            "transaction": transaction.to_dict()
        }
        
        if account:
            response_data["updated_account_balance"] = float(account.balance)
        
        if fund:
            response_data["updated_fund_balance"] = float(fund.balance)
            if fund.account:
                response_data["updated_account_balance"] = float(fund.account.balance)
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create transaction: {str(e)}"}), 500


@tx_bp.route("/auto-generate", methods=["POST"])
@jwt_required()
def auto_generate_transactions():
    """Create new transactions for bills marked as autopay and due today or earlier"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    current_user_id = get_current_user_id()
    
    # Find bills that are autopay, active, and due today or earlier using next_due_date
    today = date.today()
    due_bills = Bill.query.filter(
        Bill.household_id == household_id,
        Bill.is_autopay == True,
        Bill.is_active == True,
        Bill.next_due_date <= today
    ).all()
    
    if not due_bills:
        return jsonify({
            "message": "No autopay bills found that are due",
            "transactions_created": 0
        }), 200
    
    created_transactions = []
    
    try:
        for bill in due_bills:
            # Check if transaction already exists for this bill's current due date
            existing_transaction = Transaction.query.filter(
                Transaction.household_id == household_id,
                Transaction.bill_id == bill.id,
                Transaction.date == bill.next_due_date,
                Transaction.is_autopay == True
            ).first()
            
            if existing_transaction:
                continue  # Skip if already created for this due date
            
            # Create autopay transaction
            transaction = Transaction(
                household_id=household_id,
                created_by_user_id=current_user_id,
                amount=-abs(bill.amount),  # Bills are expenses (negative)
                description=f"Autopay: {bill.name}",
                category=bill.category,
                transaction_type="expense",
                bill_id=bill.id,
                is_autopay=True,
                date=bill.next_due_date
            )
            
            db.session.add(transaction)
            created_transactions.append(transaction)
            
            # Deduct from bill's linked account if it has one
            if bill.account:
                bill.account.balance -= abs(bill.amount)
            
            # Mark bill as paid and update next due date
            bill.mark_as_paid()
        
        db.session.commit()
        
        return jsonify({
            "message": f"Successfully created {len(created_transactions)} autopay transactions",
            "transactions_created": len(created_transactions),
            "transactions": [tx.to_dict() for tx in created_transactions]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create autopay transactions: {str(e)}"}), 500


@tx_bp.route("/<int:transaction_id>", methods=["GET"])
@jwt_required()
def get_transaction(transaction_id):
    """Get a specific transaction"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        household_id=household_id
    ).first()
    
    if not transaction:
        return jsonify({"error": "Transaction not found or access denied"}), 404
    
    return jsonify(transaction.to_dict()), 200


@tx_bp.route("/<int:transaction_id>", methods=["PUT"])
@jwt_required()
def update_transaction(transaction_id):
    """Update a transaction and adjust fund balance if applicable"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        household_id=household_id
    ).first()
    
    if not transaction:
        return jsonify({"error": "Transaction not found or access denied"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        # Store original values for fund balance adjustment
        original_amount = transaction.amount
        original_fund_id = transaction.fund_id
        original_type = transaction.transaction_type
        
        # Revert original transaction's effect on fund balance
        if original_fund_id:
            fund = Fund.query.filter_by(id=original_fund_id, household_id=household_id).first()
            if fund:
                if original_type == "income":
                    fund.balance -= abs(original_amount)
                elif original_type == "expense":
                    fund.balance += abs(original_amount)
        
        # Update transaction fields
        if "amount" in data:
            try:
                transaction.amount = Decimal(str(data["amount"]))
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid amount"}), 400
        
        if "description" in data:
            transaction.description = data["description"]
        
        if "category" in data:
            transaction.category = data["category"]
        
        if "transaction_type" in data:
            new_type = data["transaction_type"]
            valid_types = ["income", "expense", "transfer"]
            if new_type not in valid_types:
                return jsonify({"error": f"Invalid transaction type. Must be one of: {', '.join(valid_types)}"}), 400
            transaction.transaction_type = new_type
        
        if "fund_id" in data:
            fund_id = data["fund_id"]
            if fund_id:
                fund = Fund.query.filter_by(id=fund_id, household_id=household_id).first()
                if not fund:
                    return jsonify({"error": "Fund not found or access denied"}), 404
            transaction.fund_id = fund_id
        
        if "bill_id" in data:
            bill_id = data["bill_id"]
            if bill_id:
                bill = Bill.query.filter_by(id=bill_id, household_id=household_id).first()
                if not bill:
                    return jsonify({"error": "Bill not found or access denied"}), 404
            transaction.bill_id = bill_id
        
        if "is_autopay" in data:
            transaction.is_autopay = bool(data["is_autopay"])
        
        if "date" in data:
            try:
                transaction.date = datetime.fromisoformat(data["date"].replace('Z', '+00:00')).date()
            except ValueError:
                return jsonify({"error": "Invalid date format. Use ISO format (YYYY-MM-DD)"}), 400
        
        # Apply updated transaction's effect on fund balance
        if transaction.fund_id:
            fund = Fund.query.filter_by(id=transaction.fund_id, household_id=household_id).first()
            if fund:
                if transaction.transaction_type == "income":
                    fund.balance += abs(transaction.amount)
                elif transaction.transaction_type == "expense":
                    if fund.balance < abs(transaction.amount):
                        return jsonify({"error": "Insufficient fund balance for this expense"}), 400
                    fund.balance -= abs(transaction.amount)
        
        db.session.commit()
        
        response_data = {
            "message": "Transaction updated successfully",
            "transaction": transaction.to_dict()
        }
        
        if transaction.fund_id:
            fund = Fund.query.get(transaction.fund_id)
            response_data["updated_fund_balance"] = float(fund.balance)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update transaction: {str(e)}"}), 500


@tx_bp.route("/<int:transaction_id>", methods=["DELETE"])
@jwt_required()
def delete_transaction(transaction_id):
    """Delete a transaction and update the linked fund balance"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        household_id=household_id
    ).first()
    
    if not transaction:
        return jsonify({"error": "Transaction not found or access denied"}), 404
    
    try:
        # Revert the transaction's effect on fund balance
        if transaction.fund_id:
            fund = Fund.query.filter_by(id=transaction.fund_id, household_id=household_id).first()
            if fund:
                if transaction.transaction_type == "income":
                    fund.balance -= abs(transaction.amount)
                elif transaction.transaction_type == "expense":
                    fund.balance += abs(transaction.amount)
        
        db.session.delete(transaction)
        db.session.commit()
        
        response_data = {"message": "Transaction deleted successfully"}
        
        if transaction.fund_id:
            fund = Fund.query.get(transaction.fund_id)
            response_data["updated_fund_balance"] = float(fund.balance)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete transaction: {str(e)}"}), 500


# Additional helpful endpoints

@tx_bp.route("/by-category", methods=["GET"])
@jwt_required()
def get_transactions_by_category():
    """Get transactions grouped by category"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    # Get optional date filters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Transaction.query.filter_by(household_id=household_id)
    
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date).date()
            query = query.filter(Transaction.date >= start_date)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400
    
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date).date()
            query = query.filter(Transaction.date <= end_date)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400
    
    transactions = query.all()
    
    # Group by category
    categories = {}
    for transaction in transactions:
        category = transaction.category
        if category not in categories:
            categories[category] = {
                "category": category,
                "total_amount": 0,
                "transaction_count": 0,
                "transactions": []
            }
        
        categories[category]["total_amount"] += float(transaction.amount)
        categories[category]["transaction_count"] += 1
        categories[category]["transactions"].append(transaction.to_dict())
    
    return jsonify(list(categories.values())), 200


@tx_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_transaction_summary():
    """Get transaction summary (income, expenses, balance)"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    # Get optional date filters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Transaction.query.filter_by(household_id=household_id)
    
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date).date()
            query = query.filter(Transaction.date >= start_date)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400
    
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date).date()
            query = query.filter(Transaction.date <= end_date)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400
    
    transactions = query.all()
    
    total_income = sum(float(t.amount) for t in transactions if t.transaction_type == "income")
    total_expenses = sum(abs(float(t.amount)) for t in transactions if t.transaction_type == "expense")
    net_balance = total_income - total_expenses
    
    return jsonify({
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": net_balance,
        "transaction_count": len(transactions),
        "date_range": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }
    }), 200


@tx_bp.route("/<int:transaction_id>/skip", methods=["PUT"])
@jwt_required()
def skip_recurring_instance(transaction_id):
    """Mark a recurring transaction instance as skipped"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        household_id=household_id
    ).first()
    
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404
    
    if not transaction.is_recurring and not transaction.parent_transaction_id:
        return jsonify({"error": "Transaction is not recurring"}), 400
    
    try:
        transaction.is_skipped = True
        db.session.commit()
        
        return jsonify({
            "message": "Transaction marked as skipped",
            "transaction": transaction.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@tx_bp.route("/process-recurring", methods=["POST"])
@jwt_required()
def process_recurring_transactions():
    """Create instances for recurring transactions that are due"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    current_user_id = get_current_user_id()
    
    # Find recurring transactions where next_occurrence is today or earlier
    today = date.today()
    due_transactions = Transaction.query.filter(
        Transaction.household_id == household_id,
        Transaction.is_recurring == True,
        Transaction.next_occurrence <= today,
        Transaction.is_skipped == False
    ).all()
    
    created_instances = []
    
    try:
        for parent_tx in due_transactions:
            # Create new instance
            new_tx = Transaction(
                household_id=household_id,
                created_by_user_id=current_user_id,
                amount=parent_tx.amount,
                description=parent_tx.description,
                category=parent_tx.category,
                transaction_type=parent_tx.transaction_type,
                account_id=parent_tx.account_id,
                fund_id=parent_tx.fund_id,
                to_account_id=parent_tx.to_account_id,
                to_fund_id=parent_tx.to_fund_id,
                parent_transaction_id=parent_tx.id,
                date=parent_tx.next_occurrence
            )
            
            # Update balances (same logic as regular transaction)
            # Account.balance is Numeric (Decimal), Fund.balance is Float
            amount_value = abs(parent_tx.amount)
            
            if parent_tx.transaction_type == "transfer":
                if parent_tx.account:
                    parent_tx.account.balance -= Decimal(str(amount_value))
                elif parent_tx.fund:
                    parent_tx.fund.balance -= float(amount_value)
                    if parent_tx.fund.account:
                        parent_tx.fund.account.balance -= Decimal(str(amount_value))
                
                if parent_tx.to_account:
                    parent_tx.to_account.balance += Decimal(str(amount_value))
                elif parent_tx.to_fund:
                    parent_tx.to_fund.balance += float(amount_value)
                    if parent_tx.to_fund.account:
                        parent_tx.to_fund.account.balance += Decimal(str(amount_value))
            elif parent_tx.transaction_type == "income":
                if parent_tx.account:
                    parent_tx.account.balance += Decimal(str(amount_value))
                if parent_tx.fund:
                    parent_tx.fund.balance += float(amount_value)
                    if parent_tx.fund.account:
                        parent_tx.fund.account.balance += Decimal(str(amount_value))
            elif parent_tx.transaction_type == "expense":
                if parent_tx.account:
                    parent_tx.account.balance -= Decimal(str(amount_value))
                if parent_tx.fund:
                    parent_tx.fund.balance -= float(amount_value)
                    if parent_tx.fund.account:
                        parent_tx.fund.account.balance -= Decimal(str(amount_value))
            
            db.session.add(new_tx)
            created_instances.append(new_tx)
            
            # Update parent's next occurrence
            parent_tx.next_occurrence = parent_tx.calculate_next_occurrence(parent_tx.next_occurrence)
        
        db.session.commit()
        
        return jsonify({
            "message": f"Processed {len(created_instances)} recurring transactions",
            "transactions": [tx.to_dict() for tx in created_instances]
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

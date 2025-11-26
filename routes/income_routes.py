from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from backend.database import db
from backend.models.income import Income
from backend.utils.auth_helpers import get_current_household_id

income_bp = Blueprint('income', __name__)


@income_bp.route('/', methods=['GET'])
@jwt_required()
def get_income_entries():
    """Get all income entries for the logged-in user"""
    try:
        household_id = get_current_household_id()
        if not household_id:
            return jsonify({"error": "No household found for user"}), 404
        
        # Get query parameters for filtering/sorting
        sort_by = request.args.get('sort_by', 'date')
        order = request.args.get('order', 'desc')
        source_filter = request.args.get('source')
        
        # Build query
        query = Income.query.filter_by(household_id=household_id)
        
        # Apply source filter if provided
        if source_filter:
            query = query.filter(Income.source.ilike(f'%{source_filter}%'))
        
        # Apply sorting
        if sort_by == 'date':
            if order == 'desc':
                query = query.order_by(Income.date.desc())
            else:
                query = query.order_by(Income.date.asc())
        elif sort_by == 'amount':
            if order == 'desc':
                query = query.order_by(Income.amount.desc())
            else:
                query = query.order_by(Income.amount.asc())
        elif sort_by == 'source':
            if order == 'desc':
                query = query.order_by(Income.source.desc())
            else:
                query = query.order_by(Income.source.asc())
        
        income_entries = query.all()
        
        return jsonify({
            'success': True,
            'income_entries': [entry.to_dict() for entry in income_entries],
            'total_entries': len(income_entries),
            'total_amount': sum(entry.amount for entry in income_entries)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving income entries: {str(e)}'
        }), 500


@income_bp.route('/', methods=['POST'])
@jwt_required()
def create_income_entry():
    """Create a new income entry"""
    try:
        household_id = get_current_household_id()
        if not household_id:
            return jsonify({"error": "No household found for user"}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        required_fields = ['amount', 'source']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate amount
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({
                    'success': False,
                    'message': 'Amount must be greater than 0'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'Invalid amount format'
            }), 400
        
        # Parse date if provided, otherwise use today
        income_date = None
        if 'date' in data and data['date']:
            try:
                income_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        
        # Get account_id if provided
        account_id = data.get('account_id')
        
        # Validate account if provided
        account = None
        if account_id:
            from models import Account
            account = Account.query.filter_by(id=account_id, household_id=household_id).first()
            if not account:
                return jsonify({
                    'success': False,
                    'message': 'Account not found or access denied'
                }), 404
        
        # Create new income entry
        income_entry = Income(
            household_id=household_id,
            amount=amount,
            source=data['source'].strip(),
            category=data.get('category', 'Paycheck').strip(),
            description=data.get('description', '').strip(),
            date=income_date,  # Will use default (today) if None
            account_id=account_id
        )
        
        # Update account balance if account is linked
        if account:
            account.balance += amount
        
        db.session.add(income_entry)
        db.session.commit()
        
        response_data = {
            'success': True,
            'message': 'Income entry created successfully',
            'income_entry': income_entry.to_dict()
        }
        
        if account:
            response_data['updated_account_balance'] = float(account.balance)
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating income entry: {str(e)}'
        }), 500


@income_bp.route('/<int:income_id>', methods=['DELETE'])
@jwt_required()
def delete_income_entry(income_id):
    """Delete an income entry"""
    try:
        household_id = get_current_household_id()
        if not household_id:
            return jsonify({"error": "No household found for user"}), 404
        
        # Find the income entry
        income_entry = Income.query.filter_by(id=income_id, household_id=household_id).first()
        
        if not income_entry:
            return jsonify({
                'success': False,
                'message': 'Income entry not found'
            }), 404
        
        # Store entry data for response
        entry_data = income_entry.to_dict()
        
        # Delete the entry
        db.session.delete(income_entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Income entry deleted successfully',
            'deleted_entry': entry_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting income entry: {str(e)}'
        }), 500


@income_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_income_summary():
    """Get income summary breakdown by source type"""
    try:
        household_id = get_current_household_id()
        if not household_id:
            return jsonify({"error": "No household found for user"}), 404
        
        # Get date range parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build base query
        query = Income.query.filter_by(household_id=household_id)
        
        # Apply date filters if provided
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Income.date >= start_date_obj)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid start_date format. Use YYYY-MM-DD'
                }), 400
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Income.date <= end_date_obj)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid end_date format. Use YYYY-MM-DD'
                }), 400
        
        # Get all income entries
        income_entries = query.all()
        
        # Calculate summary by source
        source_summary = {}
        total_income = 0
        
        for entry in income_entries:
            source = entry.source
            amount = entry.amount
            
            if source not in source_summary:
                source_summary[source] = {
                    'total_amount': 0,
                    'count': 0,
                    'average_amount': 0
                }
            
            source_summary[source]['total_amount'] += amount
            source_summary[source]['count'] += 1
            total_income += amount
        
        # Calculate averages and percentages
        for source in source_summary:
            count = source_summary[source]['count']
            total = source_summary[source]['total_amount']
            source_summary[source]['average_amount'] = round(total / count, 2)
            source_summary[source]['percentage'] = round((total / total_income * 100), 2) if total_income > 0 else 0
        
        # Sort by total amount (descending)
        sorted_sources = dict(sorted(source_summary.items(), 
                                   key=lambda x: x[1]['total_amount'], 
                                   reverse=True))
        
        return jsonify({
            'success': True,
            'summary': {
                'total_income': round(total_income, 2),
                'total_entries': len(income_entries),
                'unique_sources': len(source_summary),
                'by_source': sorted_sources,
                'date_range': {
                    'start_date': start_date,
                    'end_date': end_date
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating income summary: {str(e)}'
        }), 500
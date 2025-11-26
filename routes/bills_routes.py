# backend/routes/bills_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from backend.models.bill import Bill
from backend.utils.forecasting import generate_forecast, get_bill_schedule_summary
from backend.utils.auth_helpers import get_current_household_id
from backend.database import db

bills_bp = Blueprint('bills', __name__)


@bills_bp.route('/', methods=['GET'])
@jwt_required()
def get_bills():
    """Get all bills for the current household"""
    household_id = get_current_household_id()
    
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    bills = Bill.query.filter_by(household_id=household_id, is_active=True).all()
    
    return jsonify({
        'bills': [bill.to_dict() for bill in bills],
        'total': len(bills)
    }), 200


@bills_bp.route('/', methods=['POST'])
@jwt_required()
def create_bill():
    """Create a new bill"""
    household_id = get_current_household_id()
    
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'amount', 'due_date', 'category']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        # Parse due_date
        due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        
        # Create new bill
        bill = Bill(
            household_id=household_id,
            name=data['name'],
            description=data.get('description', ''),
            amount=float(data['amount']),
            due_date=due_date,
            frequency=data.get('frequency', 'monthly'),
            category=data['category'],
            is_autopay=data.get('is_autopay', False)
        )
        
        # Calculate and set next due date
        bill.update_next_due_date()
        
        db.session.add(bill)
        db.session.commit()
        
        return jsonify({
            'message': 'Bill created successfully',
            'bill': bill.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create bill: {str(e)}'}), 500


@bills_bp.route('/<int:bill_id>', methods=['PUT'])
@jwt_required()
def update_bill(bill_id):
    """Update an existing bill"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    bill = Bill.query.filter_by(id=bill_id, household_id=household_id).first()
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    data = request.get_json()
    
    try:
        # Update fields if provided
        if 'name' in data:
            bill.name = data['name']
        if 'description' in data:
            bill.description = data['description']
        if 'amount' in data:
            bill.amount = float(data['amount'])
        if 'due_date' in data:
            bill.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        if 'frequency' in data:
            bill.frequency = data['frequency']
        if 'category' in data:
            bill.category = data['category']
        if 'is_autopay' in data:
            bill.is_autopay = data['is_autopay']
        if 'is_active' in data:
            bill.is_active = data['is_active']
        
        # Recalculate next due date if due_date or frequency changed
        if 'due_date' in data or 'frequency' in data:
            bill.update_next_due_date()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Bill updated successfully',
            'bill': bill.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update bill: {str(e)}'}), 500


@bills_bp.route('/<int:bill_id>', methods=['DELETE'])
@jwt_required()
def delete_bill(bill_id):
    """Delete a bill (soft delete by setting is_active=False)"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    bill = Bill.query.filter_by(id=bill_id, household_id=household_id).first()
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    try:
        bill.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Bill deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete bill: {str(e)}'}), 500


@bills_bp.route('/<int:bill_id>/pay', methods=['POST'])
@jwt_required()
def mark_bill_paid(bill_id):
    """Mark a bill as paid and update next due date"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    bill = Bill.query.filter_by(id=bill_id, household_id=household_id).first()
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    try:
        bill.mark_as_paid()
        
        return jsonify({
            'message': 'Bill marked as paid',
            'bill': bill.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to mark bill as paid: {str(e)}'}), 500


@bills_bp.route('/schedule', methods=['GET'])
@jwt_required()
def get_bill_schedule():
    """
    Returns a projected schedule of all bills, deposits, and balances for the given user.
    Accepts optional query params: start_date, months_to_project, buffer.
    """
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    # Parse query parameters
    start_date_str = request.args.get('start_date')
    months_to_project = int(request.args.get('months_to_project', 3))
    buffer = float(request.args.get('buffer', 100))
    
    try:
        # Parse start date or use today
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = date.today()
        
        # Generate comprehensive forecast
        forecast_data = generate_forecast(
            household_id=household_id,
            start_date=start_date,
            months_to_project=months_to_project,
            buffer=buffer
        )
        
        return jsonify(forecast_data), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to generate bill schedule: {str(e)}'}), 500


@bills_bp.route('/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming_bills():
    """Get bills due in the next N days (default: 7 days)"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    days = int(request.args.get('days', 7))
    
    try:
        start_date = date.today()
        bills_schedule = get_bill_schedule_summary(household_id, start_date, days)
        
        return jsonify({
            'upcoming_bills': bills_schedule,
            'total': len(bills_schedule),
            'period_days': days
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get upcoming bills: {str(e)}'}), 500


@bills_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_bill_categories():
    """Get all unique bill categories for the user"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    try:
        categories = db.session.query(Bill.category).filter_by(
            household_id=household_id, 
            is_active=True
        ).distinct().all()
        
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify({
            'categories': category_list,
            'total': len(category_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get categories: {str(e)}'}), 500


@bills_bp.route('/schedule', methods=['GET'])
@jwt_required()
def get_schedule():
    """Get saved bills schedule for the current user"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    try:
        # For now, we'll store schedule data in localStorage on frontend
        # This endpoint returns empty to allow frontend to initialize
        return jsonify({
            'schedule': None,
            'startingBalance': None
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get schedule: {str(e)}'}), 500


@bills_bp.route('/schedule/update', methods=['POST'])
@jwt_required()
def update_schedule():
    """Save bills schedule for the current user"""
    household_id = get_current_household_id()
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    data = request.get_json()
    
    try:
        # For now, just acknowledge the save
        # In future, could store in database
        starting_balance = data.get('startingBalance', 0)
        schedule = data.get('schedule', [])
        
        # Could save to database here with a Schedule model
        # For now, returning success
        
        return jsonify({
            'message': 'Schedule saved successfully',
            'startingBalance': starting_balance,
            'rowCount': len(schedule)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to save schedule: {str(e)}'}), 500

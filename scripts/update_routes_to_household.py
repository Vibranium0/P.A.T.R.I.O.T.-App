#!/usr/bin/env python3
"""
Script to update all route files to use household_id instead of user_id
This updates queries for complete household transparency
"""

import re
import os

# Routes that need to be updated
ROUTE_FILES = [
    'backend/routes/bills_routes.py',
    'backend/routes/income_routes.py',
    'backend/routes/accounts_routes.py',
    'backend/routes/transactions_routes.py',
    'backend/routes/debts_routes.py',
    'backend/routes/dashboard_routes.py',
    'backend/routes/reports_routes.py',
]

def update_route_file(filepath):
    """Update a single route file to use household_id"""
    print(f"Updating {filepath}...")
    
    with open(filepath, 'r') as f:
        content = f.content()
    
    original = content
    
    # Add auth_helpers import if not present
    if 'from utils.auth_helpers import' not in content:
        # Find the imports section and add after other imports
        import_pattern = r'(from flask_jwt_extended import[^\n]+\n)'
        replacement = r'\1from utils.auth_helpers import get_current_household_id, get_current_user_id\n'
        content = re.sub(import_pattern, replacement, content)
    
    # Replace user_id queries with household_id
    patterns = [
        # Filter by user_id
        (r'filter_by\(user_id=current_user_id\)', r'filter_by(household_id=household_id)'),
        (r'\.filter_by\(id=(\w+), user_id=current_user_id\)', r'.filter_by(id=\1, household_id=household_id)'),
        
        # Setting user_id
        (r'user_id=current_user_id', r'household_id=household_id'),
        
        # Comments
        (r'for the current user', r'for the current household'),
        (r'Get all \w+ for the current user', lambda m: m.group(0).replace('user', 'household')),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Add household_id retrieval at start of functions
    # Look for functions that use current_user_id
    function_pattern = r'(@\w+_bp\.route\([^\)]+\)\s+@jwt_required\(\)\s+def \w+\([^\)]*\):.*?)(current_user_id = get_jwt_identity\(\))'
    
    def add_household_check(match):
        route_def = match.group(1)
        user_id_line = match.group(2)
        
        # Add household_id retrieval
        household_code = '''household_id = get_current_household_id()
    
    if not household_id:
        return jsonify({"error": "No household found for user"}), 404
    
    '''
        return route_def + household_code + user_id_line
    
    content = re.sub(function_pattern, add_household_check, content, flags=re.DOTALL)
    
    # Write back if changed
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Updated {filepath}")
        return True
    else:
        print(f"⏭️  No changes needed for {filepath}")
        return False

def main():
    """Update all route files"""
    print("=" * 60)
    print("HOUSEHOLD MIGRATION: Updating API routes")
    print("=" * 60)
    
    updated_count = 0
    for filepath in ROUTE_FILES:
        if os.path.exists(filepath):
            if update_route_file(filepath):
                updated_count += 1
        else:
            print(f"⚠️  File not found: {filepath}")
    
    print("=" * 60)
    print(f"✅ Migration complete! Updated {updated_count} files.")
    print("=" * 60)

if __name__ == '__main__':
    main()

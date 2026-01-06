#!/usr/bin/env python3
"""
Simple test runner that validates code structure without requiring database
"""
import os
import sys
import py_compile
from pathlib import Path

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓ {msg}{NC}")

def print_error(msg):
    print(f"{RED}✗ {msg}{NC}")

def print_info(msg):
    print(f"{YELLOW}→ {msg}{NC}")

def check_syntax(file_path):
    """Check if a Python file has valid syntax"""
    try:
        py_compile.compile(file_path, doraise=True)
        return True
    except py_compile.PyCompileError as e:
        print(f"  Error: {e}")
        return False

def main():
    print("=" * 60)
    print("P.A.T.R.I.O.T. Backend Test Suite")
    print("=" * 60)
    print()
    
    base_dir = Path(__file__).parent
    
    # Test 1: Model Syntax
    print("-" * 60)
    print("Test 1: Model Syntax Validation")
    print("-" * 60)
    
    models = [
        "patriot/backend/models/category.py",
        "patriot/backend/models/expense.py",
        "patriot/backend/models/goal.py",
        "patriot/backend/models/saving.py",
        "patriot/backend/models/income.py",
        "patriot/backend/models/account.py",
    ]
    
    model_errors = 0
    for model_path in models:
        full_path = base_dir / model_path
        model_name = Path(model_path).name
        
        if full_path.exists():
            if check_syntax(str(full_path)):
                print_success(f"{model_name} syntax OK")
            else:
                print_error(f"{model_name} has syntax errors")
                model_errors += 1
        else:
            print_error(f"{model_name} not found")
            model_errors += 1
    
    if model_errors > 0:
        print_error(f"Found {model_errors} errors in models")
        return False
    else:
        print_success("All models passed syntax validation")
    
    print()
    
    # Test 2: Route Syntax
    print("-" * 60)
    print("Test 2: Route Syntax Validation")
    print("-" * 60)
    
    routes = [
        "patriot/backend/routes/categories_routes.py",
        "patriot/backend/routes/expenses_routes.py",
        "patriot/backend/routes/goals_routes.py",
        "patriot/backend/routes/savings_routes.py",
        "patriot/backend/routes/income_routes.py",
        "patriot/backend/routes/financial_accounts_routes.py",
    ]
    
    route_errors = 0
    for route_path in routes:
        full_path = base_dir / route_path
        route_name = Path(route_path).name
        
        if full_path.exists():
            if check_syntax(str(full_path)):
                print_success(f"{route_name} syntax OK")
            else:
                print_error(f"{route_name} has syntax errors")
                route_errors += 1
        else:
            print_error(f"{route_name} not found")
            route_errors += 1
    
    if route_errors > 0:
        print_error(f"Found {route_errors} errors in routes")
        return False
    else:
        print_success("All routes passed syntax validation")
    
    print()
    
    # Test 3: Endpoint Count
    print("-" * 60)
    print("Test 3: API Endpoint Structure")
    print("-" * 60)
    
    endpoint_count = 0
    for route_path in routes:
        full_path = base_dir / route_path
        if full_path.exists():
            with open(full_path, 'r') as f:
                content = f.read()
                # Count route decorators
                count = content.count('@') - content.count('@@')
                # Rough estimate of endpoints
                routes_in_file = content.count('.route(')
                endpoint_count += routes_in_file
    
    print_success(f"Found {endpoint_count} total API endpoints")
    
    # Test 4: Blueprint Registration
    app_py = base_dir / "patriot/backend/app.py"
    if app_py.exists():
        with open(app_py, 'r') as f:
            content = f.read()
            
        blueprints = ['categories_bp', 'expenses_bp', 'goals_bp', 'savings_bp']
        missing = []
        
        for bp in blueprints:
            if bp not in content:
                missing.append(bp)
        
        if missing:
            print_error(f"Missing blueprints in app.py: {', '.join(missing)}")
            return False
        else:
            print_success("All new blueprints registered in app.py")
    else:
        print_error("app.py not found")
        return False
    
    print()
    
    # Test 5: File Structure
    print("-" * 60)
    print("Test 4: File Structure Check")
    print("-" * 60)
    
    required_files = [
        "patriot/backend/app.py",
        "patriot/backend/models/__init__.py",
        "patriot/backend/routes/__init__.py",
        "patriot/backend/docs/API_ENDPOINTS.md",
        "API_QUICK_REFERENCE.md",
        "ENDPOINTS_COMPLETE.md",
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print_success(f"{file_path} exists")
        else:
            print_error(f"{file_path} not found")
            missing_files.append(file_path)
    
    if missing_files:
        print_error(f"Missing {len(missing_files)} required files")
        return False
    
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print_success("✓ Syntax Validation: PASSED")
    print_success("✓ Endpoint Registration: PASSED")
    print_success("✓ File Structure: PASSED")
    print()
    print_info("Next Steps:")
    print("  1. Install dependencies: pip install -r patriot/backend/requirements.txt")
    print("  2. Start database and run migrations: ./run_migrations.py")
    print("  3. Run full model tests: python test_new_models.py")
    print("  4. Start backend: cd patriot/backend && python app.py")
    print("  5. Test endpoints using API_QUICK_REFERENCE.md")
    print()
    print_success("✓ All basic tests PASSED!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

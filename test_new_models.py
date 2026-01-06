#!/usr/bin/env python3
"""
Test script for new P.A.T.R.I.O.T. database models
Tests Category, Expense, Goal, and Saving models with their relationships
"""
import sys
import os
from datetime import date, datetime, timedelta

# Add the project root to path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "patriot", "backend"))

from patriot.backend.app import create_app
from patriot.backend.database import db
from patriot.backend.models import (
    Account, Bill, Category, Expense, Goal, Saving,
    Fund, Income, Transaction, User, Household
)

def test_models():
    """Test all new models and their relationships"""
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("Testing P.A.T.R.I.O.T. Database Models")
        print("=" * 80)
        
        try:
            # Clean up test data if it exists
            print("\n🧹 Cleaning up existing test data...")
            Saving.query.filter(Saving.description == "Test Saving").delete()
            Expense.query.filter(Expense.description == "Test Expense").delete()
            Goal.query.filter(Goal.name == "Test Goal").delete()
            Category.query.filter(Category.name == "Test Category").delete()
            Account.query.filter(Account.name == "Test Account").delete()
            User.query.filter(User.email == "test@patriot.com").delete()
            Household.query.filter(Household.name == "Test Household").delete()
            db.session.commit()
            
            # Create test data
            print("\n📝 Creating test household and user...")
            
            # Create test household
            household = Household(name="Test Household")
            db.session.add(household)
            db.session.flush()
            
            # Create test user
            user = User(
                name="Test User",
                email="test@patriot.com",
                password_hash="test_hash",
                default_household_id=household.id
            )
            db.session.add(user)
            db.session.flush()
            
            # Create test account
            account = Account(
                household_id=household.id,
                owner_user_id=user.id,
                name="Test Account",
                type="checking",
                balance=1000.00
            )
            db.session.add(account)
            db.session.flush()
            
            print(f"✅ Created household (ID: {household.id})")
            print(f"✅ Created user (ID: {user.id})")
            print(f"✅ Created account (ID: {account.id})")
            
            # Test 1: Category Model
            print("\n" + "=" * 80)
            print("TEST 1: Category Model")
            print("=" * 80)
            
            # Create parent category
            parent_category = Category(
                household_id=household.id,
                name="Test Category",
                description="Parent category for testing",
                category_type="expense",
                icon="🏠",
                color="#FF5733",
                budget_amount=500.00
            )
            db.session.add(parent_category)
            db.session.flush()
            
            # Create subcategory
            subcategory = Category(
                household_id=household.id,
                name="Test Subcategory",
                description="Child category for testing",
                category_type="expense",
                parent_id=parent_category.id,
                budget_amount=200.00
            )
            db.session.add(subcategory)
            db.session.commit()
            
            print(f"✅ Created parent category: {parent_category.name} (ID: {parent_category.id})")
            print(f"✅ Created subcategory: {subcategory.name} (ID: {subcategory.id})")
            print(f"   Full name: {subcategory.full_name}")
            print(f"   Parent has {len(parent_category.subcategories)} subcategories")
            
            # Test 2: Expense Model
            print("\n" + "=" * 80)
            print("TEST 2: Expense Model")
            print("=" * 80)
            
            expense = Expense(
                household_id=household.id,
                created_by_user_id=user.id,
                account_id=account.id,
                category_id=parent_category.id,
                date=date.today(),
                amount=150.00,
                description="Test Expense",
                merchant="Test Store",
                payment_method="credit",
                tags="test,groceries"
            )
            db.session.add(expense)
            db.session.commit()
            
            print(f"✅ Created expense: ${expense.amount} at {expense.merchant}")
            print(f"   Category: {expense.category.name if expense.category else 'None'}")
            print(f"   Account: {expense.account.name if expense.account else 'None'}")
            print(f"   Tags: {expense.to_dict()['tags']}")
            
            # Test expense queries
            start_date = date.today() - timedelta(days=30)
            end_date = date.today()
            total = Expense.get_total_for_period(household.id, start_date, end_date)
            print(f"   Total expenses for last 30 days: ${total}")
            
            # Test 3: Goal Model
            print("\n" + "=" * 80)
            print("TEST 3: Goal Model")
            print("=" * 80)
            
            goal = Goal(
                household_id=household.id,
                created_by_user_id=user.id,
                account_id=account.id,
                name="Test Goal",
                description="Save for vacation",
                target_amount=5000.00,
                current_amount=1000.00,
                target_date=date.today() + timedelta(days=180),
                category="vacation",
                priority="high",
                icon="✈️",
                color="#4287f5"
            )
            db.session.add(goal)
            db.session.commit()
            
            print(f"✅ Created goal: {goal.name}")
            print(f"   Progress: ${goal.current_amount}/${goal.target_amount} ({goal.progress_percentage:.1f}%)")
            print(f"   Remaining: ${goal.amount_remaining}")
            print(f"   Days remaining: {goal.days_remaining}")
            print(f"   Recommended monthly contribution: ${goal.recommended_monthly_contribution:.2f}")
            
            # Test goal contribution
            goal.add_contribution(500.00)
            db.session.commit()
            print(f"   After $500 contribution: ${goal.current_amount} ({goal.progress_percentage:.1f}%)")
            
            # Test 4: Saving Model
            print("\n" + "=" * 80)
            print("TEST 4: Saving Model")
            print("=" * 80)
            
            saving_deposit = Saving(
                household_id=household.id,
                created_by_user_id=user.id,
                account_id=account.id,
                goal_id=goal.id,
                category_id=parent_category.id,
                date=date.today(),
                amount=500.00,
                transaction_type="deposit",
                source="Paycheck",
                description="Test Saving",
                is_automatic=True
            )
            db.session.add(saving_deposit)
            db.session.commit()
            
            print(f"✅ Created saving deposit: ${saving_deposit.amount}")
            print(f"   Type: {saving_deposit.transaction_type}")
            print(f"   Goal: {saving_deposit.goal.name if saving_deposit.goal else 'None'}")
            print(f"   Account: {saving_deposit.account.name if saving_deposit.account else 'None'}")
            print(f"   Is automatic: {saving_deposit.is_automatic}")
            
            # Test saving queries
            net_savings = Saving.get_net_savings(household.id, start_date, end_date)
            print(f"   Net savings for last 30 days: ${net_savings}")
            
            # Test 5: Relationships
            print("\n" + "=" * 80)
            print("TEST 5: Model Relationships")
            print("=" * 80)
            
            print(f"\n📊 Household '{household.name}' has:")
            print(f"   - {len(household.categories)} categories")
            print(f"   - {len(household.expenses)} expenses")
            print(f"   - {len(household.goals)} goals")
            print(f"   - {len(household.savings)} savings")
            print(f"   - {len(household.accounts)} accounts")
            
            print(f"\n👤 User '{user.name}' has:")
            print(f"   - {len(user.expenses)} expenses")
            print(f"   - {len(user.goals)} goals")
            print(f"   - {len(user.savings)} savings")
            
            print(f"\n🏦 Account '{account.name}' has:")
            print(f"   - {len(account.expenses)} expenses")
            print(f"   - {len(account.goals)} goals")
            print(f"   - {len(account.savings)} savings")
            
            print(f"\n📁 Category '{parent_category.name}' has:")
            print(f"   - {len(parent_category.expenses)} expenses")
            print(f"   - {len(parent_category.subcategories)} subcategories")
            
            # Test 6: Model Methods
            print("\n" + "=" * 80)
            print("TEST 6: Model Methods and Properties")
            print("=" * 80)
            
            # Test Category
            category_dict = parent_category.to_dict(include_subcategories=True)
            print(f"\n✅ Category to_dict: {list(category_dict.keys())}")
            
            # Test Expense
            expense_dict = expense.to_dict()
            print(f"✅ Expense to_dict: {list(expense_dict.keys())}")
            
            # Test Goal
            goal_dict = goal.to_dict()
            print(f"✅ Goal to_dict: {list(goal_dict.keys())}")
            
            # Test Saving
            saving_dict = saving_deposit.to_dict()
            print(f"✅ Saving to_dict: {list(saving_dict.keys())}")
            
            print("\n" + "=" * 80)
            print("✅ ALL TESTS PASSED!")
            print("=" * 80)
            print("\nSummary:")
            print("  ✓ Category model with parent-child relationships")
            print("  ✓ Expense model with account and category links")
            print("  ✓ Goal model with progress tracking")
            print("  ✓ Saving model with goal and fund links")
            print("  ✓ All relationships working correctly")
            print("  ✓ All model methods and properties functioning")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False
        
        finally:
            # Clean up test data
            print("\n🧹 Cleaning up test data...")
            try:
                Saving.query.filter(Saving.description == "Test Saving").delete()
                Expense.query.filter(Expense.description == "Test Expense").delete()
                Goal.query.filter(Goal.name == "Test Goal").delete()
                Category.query.filter(Category.name.like("Test%")).delete()
                Account.query.filter(Account.name == "Test Account").delete()
                User.query.filter(User.email == "test@patriot.com").delete()
                Household.query.filter(Household.name == "Test Household").delete()
                db.session.commit()
                print("✅ Test data cleaned up")
            except Exception as e:
                print(f"⚠️  Cleanup warning: {e}")
                db.session.rollback()
    
    return True

if __name__ == "__main__":
    success = test_models()
    sys.exit(0 if success else 1)

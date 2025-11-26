#!/usr/bin/env python3
"""
Database seed script for the Patriot App backend.

This script provides sample data for development and testing.
"""

import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add the backend directory to Python path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from backend.app import create_app
from backend.database import db
from backend.models.user import User
from backend.models.fund import Fund
from backend.models.bill import Bill
from backend.models.transaction import Transaction
from backend.models.income import Income
from backend.models.debt import Debt
from flask_bcrypt import Bcrypt


def seed_database():
    """Seed the database with sample data for development and testing."""
    app = create_app()
    with app.app_context():
        bcrypt = Bcrypt(app)
        print("🌱 Seeding database with sample data...")

        # Create test users
        print("Creating test users...")
        # Test User 1
        user1_password = bcrypt.generate_password_hash("testpass123").decode("utf-8")
        user1 = User(
            username="testuser",
            email="test@example.com",
            password=user1_password,
            name="Test User",
            theme="light",
            is_verified=True,
        )

        # Test User 2
        user2_password = bcrypt.generate_password_hash("demo123").decode("utf-8")
        user2 = User(
            username="demouser",
            email="demo@example.com",
            password=user2_password,
            name="Demo User",
            theme="dark",
            is_verified=True,
        )

        db.session.add_all([user1, user2])
        db.session.commit()
        print(f"✅ Created users: {user1.username}, {user2.username}")

        # Create a shared household and add both users
        from backend.models.household import Household, user_household

        household = Household(name="Sample Household", created_by=user1.id)
        db.session.add(household)
        db.session.commit()
        # Add both users as members
        db.session.execute(
            user_household.insert().values(
                user_id=user1.id, household_id=household.id, role="owner"
            )
        )
        db.session.execute(
            user_household.insert().values(
                user_id=user2.id, household_id=household.id, role="member"
            )
        )
        db.session.commit()

        # Use shared household.id for all bills
        print("Creating sample bills...")
        bills = [
            Bill(
                household_id=household.id,
                name="Rent",
                description="Monthly apartment rent",
                amount=Decimal("1200.00"),
                due_date=date(2025, 11, 1),
                frequency="monthly",
                category="Housing",
                is_autopay=True,
            ),
            Bill(
                household_id=household.id,
                name="Electric Bill",
                description="Monthly electricity",
                amount=Decimal("120.00"),
                due_date=date(2025, 11, 15),
                frequency="monthly",
                category="Utilities",
                is_autopay=True,
            ),
            Bill(
                household_id=household.id,
                name="Internet",
                description="Monthly internet service",
                amount=Decimal("80.00"),
                due_date=date(2025, 11, 10),
                frequency="monthly",
                category="Utilities",
                is_autopay=False,
            ),
            Bill(
                household_id=household.id,
                name="Water & Sewer",
                description="Monthly water bill",
                amount=Decimal("65.00"),
                due_date=date(2025, 11, 20),
                frequency="monthly",
                category="Utilities",
                is_autopay=True,
            ),
            Bill(
                household_id=household.id,
                name="Phone Bill",
                description="Mobile phone service",
                amount=Decimal("95.00"),
                due_date=date(2025, 11, 8),
                frequency="monthly",
                category="Subscriptions",
                is_autopay=True,
            ),
            Bill(
                household_id=household.id,
                name="Gym Membership",
                description="Monthly gym membership",
                amount=Decimal("45.00"),
                due_date=date(2025, 11, 12),
                frequency="monthly",
                category="Health & Fitness",
                is_autopay=True,
            ),
            Bill(
                household_id=household.id,
                name="Streaming Services",
                description="Netflix, Spotify, etc.",
                amount=Decimal("35.00"),
                due_date=date(2025, 11, 3),
                frequency="monthly",
                category="Entertainment",
                is_autopay=True,
            ),
            Bill(
                household_id=household.id,
                name="Credit Card Payment",
                description="Minimum payment due",
                amount=Decimal("200.00"),
                due_date=date(2025, 11, 25),
                frequency="monthly",
                category="Debt",
                is_autopay=False,
            ),
            Bill(
                household_id=household.id,
                name="Mortgage",
                description="Monthly mortgage payment",
                amount=Decimal("2500.00"),
                due_date=date(2025, 11, 1),
                frequency="monthly",
                category="Housing",
                is_autopay=True,
            ),
            Bill(
                household_id=household.id,
                name="Car Insurance",
                description="Monthly car insurance",
                amount=Decimal("150.00"),
                due_date=date(2025, 11, 5),
                frequency="monthly",
                category="Insurance",
                is_autopay=True,
            ),
            Bill(
                household_id=household.id,
                name="Home Insurance",
                description="Monthly home insurance",
                amount=Decimal("180.00"),
                due_date=date(2025, 11, 1),
                frequency="monthly",
                category="Insurance",
                is_autopay=True,
            ),
            Bill(
                household_id=household.id,
                name="Gas Bill",
                description="Monthly natural gas",
                amount=Decimal("75.00"),
                due_date=date(2025, 11, 18),
                frequency="monthly",
                category="Utilities",
                is_autopay=True,
            ),
            Bill(
                household_id=household.id,
                name="HOA Fees",
                description="Homeowners association fees",
                amount=Decimal("120.00"),
                due_date=date(2025, 11, 1),
                frequency="monthly",
                category="Housing",
                is_autopay=True,
            ),
            Bill(
                household_id=household.id,
                name="Car Payment",
                description="Monthly car loan",
                amount=Decimal("425.00"),
                due_date=date(2025, 11, 10),
                frequency="monthly",
                category="Transportation",
                is_autopay=True,
            ),
        ]

        db.session.add_all(bills)
        db.session.commit()

        print(f"✅ Created {len(bills)} sample bills")

        # Create financial accounts for users
        print("Creating sample financial accounts...")

        from backend.models.account import Account

        accounts = [
            # User 1 accounts
            Account(
                household_id=household.id,
                owner_user_id=user1.id,
                name="Main Checking",
                type="checking",
                institution="Chase Bank",
                balance=Decimal("2450.75"),
                last_four="4321",
            ),
            Account(
                household_id=household.id,
                owner_user_id=user1.id,
                name="Emergency Savings",
                type="savings",
                institution="Ally Bank",
                balance=Decimal("8500.00"),
                last_four="7890",
            ),
            Account(
                household_id=household.id,
                owner_user_id=user1.id,
                name="Travel Credit Card",
                type="credit",
                institution="Capital One",
                balance=Decimal("-850.25"),
                last_four="5678",
            ),
            # User 2 accounts
            Account(
                household_id=household.id,
                owner_user_id=user2.id,
                name="Primary Checking",
                type="checking",
                institution="Bank of America",
                balance=Decimal("5200.00"),
                last_four="1234",
            ),
            Account(
                household_id=household.id,
                owner_user_id=user2.id,
                name="High-Yield Savings",
                type="savings",
                institution="Marcus by Goldman Sachs",
                balance=Decimal("25000.00"),
                last_four="5555",
            ),
            Account(
                household_id=household.id,
                owner_user_id=user2.id,
                name="Rewards Credit Card",
                type="credit",
                institution="American Express",
                balance=Decimal("-1250.00"),
                last_four="9999",
            ),
            Account(
                household_id=household.id,
                owner_user_id=user2.id,
                name="Brokerage Account",
                type="investment",
                institution="Fidelity",
                balance=Decimal("45000.00"),
                last_four="7777",
            ),
        ]

        db.session.add_all(accounts)
        db.session.commit()
        print(f"✅ Created {len(accounts)} sample financial accounts")

        # Get account references for linking funds
        user1_checking = Account.query.filter_by(
            owner_user_id=user1.id, name="Main Checking"
        ).first()
        user1_savings = Account.query.filter_by(
            owner_user_id=user1.id, name="Emergency Savings"
        ).first()
        user2_checking = Account.query.filter_by(
            owner_user_id=user2.id, name="Primary Checking"
        ).first()
        user2_savings = Account.query.filter_by(
            owner_user_id=user2.id, name="High-Yield Savings"
        ).first()
        user2_investment = Account.query.filter_by(
            owner_user_id=user2.id, name="Brokerage Account"
        ).first()

        # Create funds for users (now that accounts exist)
        print("Creating sample funds...")

        funds = [
            # User 1 funds - mix of account-based and cash
            Fund(
                household_id=household.id,
                name="Emergency Fund",
                balance=2500.0,
                goal=10000.0,
                fund_type="Savings",
                account_id=user1_savings.id,
                description="3-6 months of expenses for unexpected emergencies",
            ),
            Fund(
                household_id=household.id,
                name="Vacation Savings",
                balance=800.0,
                goal=5000.0,
                fund_type="Savings",
                account_id=user1_savings.id,
                description="Annual family vacation to Hawaii",
            ),
            Fund(
                household_id=household.id,
                name="Car Maintenance",
                balance=300.0,
                goal=1000.0,
                fund_type="Expenses",
                account_id=user1_checking.id,
                description="Routine maintenance, repairs, and registration",
            ),
            Fund(
                household_id=household.id,
                name="Grocery Budget",
                balance=450.0,
                goal=600.0,
                fund_type="Expenses",
                account_id=user1_checking.id,
                description="Monthly grocery and household essentials",
            ),
            Fund(
                household_id=household.id,
                name="Cash Wallet",
                balance=120.0,
                goal=200.0,
                fund_type="Cash",
                account_id=None,
                description="Physical cash for small purchases and tips",
            ),
            # User 2 funds - larger goals
            Fund(
                household_id=household.id,
                name="House Down Payment",
                balance=15000.0,
                goal=50000.0,
                fund_type="Savings",
                account_id=user2_savings.id,
                description="20% down payment for first home purchase",
            ),
            Fund(
                household_id=household.id,
                name="Investment Fund",
                balance=5000.0,
                goal=20000.0,
                fund_type="Savings",
                account_id=user2_investment.id,
                description="Long-term stock market investments",
            ),
            Fund(
                household_id=household.id,
                name="Monthly Bills",
                balance=2800.0,
                goal=3000.0,
                fund_type="Expenses",
                account_id=user2_checking.id,
                description="Rent, utilities, and recurring subscriptions",
            ),
        ]

        db.session.add_all(funds)
        db.session.commit()

        print(f"✅ Created {len(funds)} sample funds")

        # Create income entries
        print("Creating sample income entries...")

        income_entries = [
            # User 1 income
            Income(
                household_id=household.id,
                date=date(2025, 10, 1),
                amount=3000.0,
                source="Salary",
                description="Monthly salary",
            ),
            Income(
                household_id=household.id,
                date=date(2025, 10, 15),
                amount=500.0,
                source="Freelance",
                description="Side project payment",
            ),
            Income(
                household_id=household.id,
                date=date(2025, 9, 1),
                amount=3000.0,
                source="Salary",
                description="Monthly salary",
            ),
            # User 2 income
            Income(
                household_id=household.id,
                date=date(2025, 10, 1),
                amount=5000.0,
                source="Salary",
                description="Monthly salary",
            ),
            Income(
                household_id=household.id,
                date=date(2025, 10, 10),
                amount=1200.0,
                source="Bonus",
                description="Performance bonus",
            ),
            Income(
                household_id=household.id,
                date=date(2025, 9, 1),
                amount=5000.0,
                source="Salary",
                description="Monthly salary",
            ),
        ]

        db.session.add_all(income_entries)
        db.session.commit()

        print(f"✅ Created {len(income_entries)} sample income entries")

        # Create transactions
        print("Creating sample transactions...")

        # Get funds for transactions
        emergency_fund = Fund.query.filter_by(
            household_id=household.id, name="Emergency Fund"
        ).first()
        vacation_fund = Fund.query.filter_by(
            household_id=household.id, name="Vacation Savings"
        ).first()
        house_fund = Fund.query.filter_by(
            household_id=household.id, name="House Down Payment"
        ).first()

        # Get bills for autopay transactions
        rent_bill = Bill.query.filter_by(household_id=household.id, name="Rent").first()
        electric_bill = Bill.query.filter_by(
            household_id=household.id, name="Electric Bill"
        ).first()

        transactions = [
            # User 1 transactions
            Transaction(
                household_id=household.id,
                created_by_user_id=user1.id,
                date=date(2025, 10, 1),
                description="Emergency fund deposit",
                amount=Decimal("500.00"),
                category="Savings",
                fund_id=emergency_fund.id if emergency_fund else None,
                transaction_type="income",
            ),
            Transaction(
                household_id=household.id,
                created_by_user_id=user1.id,
                date=date(2025, 10, 5),
                description="Grocery shopping",
                amount=Decimal("75.50"),
                category="Food",
                transaction_type="expense",
            ),
            Transaction(
                household_id=household.id,
                created_by_user_id=user1.id,
                date=date(2025, 10, 10),
                description="Vacation savings",
                amount=Decimal("200.00"),
                category="Savings",
                fund_id=vacation_fund.id if vacation_fund else None,
                transaction_type="income",
            ),
            Transaction(
                household_id=household.id,
                created_by_user_id=user1.id,
                date=date(2025, 10, 1),
                description="Autopay: Rent",
                amount=Decimal("1200.00"),
                category="Housing",
                bill_id=rent_bill.id if rent_bill else None,
                transaction_type="expense",
                is_autopay=True,
            ),
            Transaction(
                household_id=household.id,
                created_by_user_id=user1.id,
                date=date(2025, 10, 15),
                description="Autopay: Electric Bill",
                amount=Decimal("120.00"),
                category="Utilities",
                bill_id=electric_bill.id if electric_bill else None,
                transaction_type="expense",
                is_autopay=True,
            ),
            # User 2 transactions
            Transaction(
                household_id=household.id,
                created_by_user_id=user2.id,
                date=date(2025, 10, 1),
                description="House fund deposit",
                amount=Decimal("1000.00"),
                category="Savings",
                fund_id=house_fund.id if house_fund else None,
                transaction_type="income",
            ),
            Transaction(
                household_id=household.id,
                created_by_user_id=user2.id,
                date=date(2025, 10, 3),
                description="Restaurant dinner",
                amount=Decimal("85.00"),
                category="Entertainment",
                transaction_type="expense",
            ),
            Transaction(
                household_id=household.id,
                created_by_user_id=user2.id,
                date=date(2025, 10, 8),
                description="Gas station",
                amount=Decimal("45.00"),
                category="Transportation",
                transaction_type="expense",
            ),
        ]

        db.session.add_all(transactions)
        db.session.commit()

        print(f"✅ Created {len(transactions)} sample transactions")

        # Create sample debts
        print("Creating sample debts...")

        debts = [
            Debt(
                household_id=household.id,
                owner_user_id=user1.id,
                name="Chase Freedom Credit Card",
                description="Main credit card for daily expenses",
                total_amount=Decimal("5000.00"),
                current_balance=Decimal("1200.50"),
                minimum_payment=Decimal("35.00"),
                interest_rate=18.99,
                due_date=date(2025, 11, 15),
                category="Credit Card",
                account_number="****1234",
            ),
            Debt(
                household_id=household.id,
                owner_user_id=user1.id,
                name="Student Loan - Federal",
                description="Federal student loan from college",
                total_amount=Decimal("25000.00"),
                current_balance=Decimal("18500.75"),
                minimum_payment=Decimal("285.00"),
                interest_rate=4.25,
                due_date=date(2025, 11, 5),
                category="Student Loan",
                account_number="****5678",
            ),
            Debt(
                household_id=household.id,
                owner_user_id=user1.id,
                name="Honda Civic Car Loan",
                description="Auto loan for 2022 Honda Civic",
                total_amount=Decimal("22000.00"),
                current_balance=Decimal("16800.25"),
                minimum_payment=Decimal("345.00"),
                interest_rate=3.99,
                due_date=date(2025, 11, 20),
                category="Auto Loan",
                account_number="****9012",
            ),
            Debt(
                household_id=household.id,
                owner_user_id=user2.id,
                name="Capital One Venture",
                description="Travel rewards credit card",
                total_amount=Decimal("3500.00"),
                current_balance=Decimal("890.25"),
                minimum_payment=Decimal("25.00"),
                interest_rate=21.24,
                due_date=date(2025, 11, 10),
                category="Credit Card",
                account_number="****3456",
            ),
            Debt(
                household_id=household.id,
                owner_user_id=user2.id,
                name="Personal Loan - Bank",
                description="Personal loan for home improvements",
                total_amount=Decimal("8000.00"),
                current_balance=Decimal("5200.80"),
                minimum_payment=Decimal("165.00"),
                interest_rate=7.99,
                due_date=date(2025, 11, 25),
                category="Personal Loan",
                account_number="****7890",
            ),
        ]

        db.session.add_all(debts)
        db.session.commit()

        print(f"✅ Created {len(debts)} sample debts")

        # Summary
        print("\n" + "=" * 60)
        print("🎉 DATABASE SEEDING COMPLETE!")
        print("=" * 60)
        print(f"👥 Users created: {len([user1, user2])}")
        print(f"💰 Funds created: {len(funds)}")
        print(f"📄 Bills created: {len(bills)}")
        print(f"💵 Income entries: {len(income_entries)}")
        print(f"📊 Transactions: {len(transactions)}")
        print(f"💳 Debts: {len(debts)}")
        print("\n📝 Test Login Credentials:")
        print("   Email: test@example.com | Password: testpass123")
        print("   Email: demo@example.com | Password: demo123")
        print("=" * 60)


def clear_and_seed():
    """Clear existing data and reseed database."""
    app = create_app()

    with app.app_context():
        print("🗑️  Clearing existing data...")
        db.drop_all()
        db.create_all()
        print("✅ Database reset complete.")

        seed_database()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed the database with sample data")
    parser.add_argument(
        "--clear", action="store_true", help="Clear existing data before seeding"
    )

    args = parser.parse_args()

    if args.clear:
        clear_and_seed()
    else:
        seed_database()

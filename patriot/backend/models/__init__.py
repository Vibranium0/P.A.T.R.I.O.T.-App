# backend/models/__init__.py
from backend.models.fund import Fund
from backend.models.transaction import Transaction
from backend.models.bill import Bill
from backend.models.income import Income
from backend.models.debt import Debt
from backend.models.account import Account
from shared.models.household import create_household_models

Household, HouseholdInvite, user_household = create_household_models(db)
from shared.models.user import User

__all__ = [
    "Fund",
    "Transaction",
    "Bill",
    "Income",
    "Debt",
    "Account",
    "User",
    "Household",
    "HouseholdInvite",
    "user_household",
]

# DIAGNOSTIC: Print file path when loaded
print(f"[DIAGNOSTIC] Loading patriot/backend/models/__init__.py from {__file__}")
# backend/models/__init__.py
from .fund import Fund
from .transaction import Transaction
from patriot.backend.database import db
from patriot.backend.models.transaction import Transaction
from patriot.backend.models.bill import Bill
from patriot.backend.models.income import Income
from patriot.backend.models.account import Account
from patriot.backend.models.debt import Debt
from patriot.backend.models.category import Category
from patriot.backend.models.expense import Expense
from patriot.backend.models.goal import Goal
from patriot.backend.models.saving import Saving

from shared.models.household import create_household_models

Household, HouseholdInvite, user_household = create_household_models(db)

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
    "Category",
    "Expense",
    "Goal",
    "Saving",
]

from patriot.backend.models.user import User

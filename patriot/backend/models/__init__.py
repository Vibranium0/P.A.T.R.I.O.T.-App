# backend/models/__init__.py
from .fund import Fund
from .transaction import Transaction
from patriot.backend.database import db
from patriot.backend.models.transaction import Transaction
from patriot.backend.models.bill import Bill
from patriot.backend.models.income import Income
from patriot.backend.models.account import Account
from shared.models.household import create_household_models

Household, HouseholdInvite, user_household = create_household_models(db)
from shared.models.user import create_user_model

User = create_user_model(db)

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

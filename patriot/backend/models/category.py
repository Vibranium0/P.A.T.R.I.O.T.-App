# patriot/backend/models/category.py
from datetime import datetime
from patriot.backend.database import db


class Category(db.Model):
    """
    Category model for organizing expenses, income, and other financial items.
    Supports hierarchical categories with parent-child relationships.
    """

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    category_type = db.Column(
        db.String(20), nullable=False
    )  # expense, income, savings, debt
    parent_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), nullable=True
    )  # For subcategories
    icon = db.Column(db.String(50))  # Icon name or emoji
    color = db.Column(db.String(20))  # Hex color code
    budget_amount = db.Column(
        db.Numeric(15, 2), nullable=True
    )  # Optional monthly budget
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    household = db.relationship("Household", backref=db.backref("categories", lazy=True))
    parent = db.relationship(
        "Category", remote_side=[id], backref=db.backref("subcategories", lazy=True)
    )

    def __repr__(self):
        return f"<Category {self.name} ({self.category_type})>"

    def to_dict(self, include_subcategories=False):
        """Convert category to dictionary for JSON serialization"""
        result = {
            "id": self.id,
            "household_id": self.household_id,
            "name": self.name,
            "description": self.description,
            "category_type": self.category_type,
            "parent_id": self.parent_id,
            "icon": self.icon,
            "color": self.color,
            "budget_amount": float(self.budget_amount) if self.budget_amount else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        if include_subcategories:
            result["subcategories"] = [
                sub.to_dict(include_subcategories=False)
                for sub in self.subcategories
                if sub.is_active
            ]

        return result

    @property
    def full_name(self):
        """Get full category name including parent"""
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    @staticmethod
    def get_default_categories():
        """Get list of default category structures"""
        return [
            # Expense categories
            {
                "name": "Housing",
                "type": "expense",
                "icon": "🏠",
                "subcategories": ["Rent/Mortgage", "Utilities", "Maintenance"],
            },
            {
                "name": "Transportation",
                "type": "expense",
                "icon": "🚗",
                "subcategories": ["Gas", "Insurance", "Maintenance", "Public Transit"],
            },
            {
                "name": "Food",
                "type": "expense",
                "icon": "🍔",
                "subcategories": ["Groceries", "Dining Out", "Coffee/Snacks"],
            },
            {
                "name": "Entertainment",
                "type": "expense",
                "icon": "🎬",
                "subcategories": ["Streaming Services", "Events", "Hobbies"],
            },
            {
                "name": "Healthcare",
                "type": "expense",
                "icon": "💊",
                "subcategories": ["Insurance", "Doctor Visits", "Medications"],
            },
            # Income categories
            {
                "name": "Employment",
                "type": "income",
                "icon": "💼",
                "subcategories": ["Salary", "Bonuses", "Tips"],
            },
            {
                "name": "Investments",
                "type": "income",
                "icon": "📈",
                "subcategories": ["Dividends", "Interest", "Capital Gains"],
            },
            # Savings categories
            {
                "name": "Emergency Fund",
                "type": "savings",
                "icon": "🛡️",
                "subcategories": [],
            },
            {
                "name": "Vacation",
                "type": "savings",
                "icon": "✈️",
                "subcategories": [],
            },
        ]

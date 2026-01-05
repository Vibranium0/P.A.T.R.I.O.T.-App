"""Add default_household_id to users table

Revision ID: add_default_household
Revises: add_security_question_to_user
Create Date: 2026-01-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_default_household'
down_revision = 'add_security_question_to_user'
branch_labels = None
depends_on = None


def upgrade():
    # Add default_household_id column
    op.add_column(
        "users", 
        sa.Column("default_household_id", sa.Integer(), nullable=True)
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        "fk_users_default_household_id",
        "users",
        "households",
        ["default_household_id"],
        ["id"]
    )


def downgrade():
    # Drop foreign key constraint first
    op.drop_constraint("fk_users_default_household_id", "users", type_="foreignkey")
    
    # Drop the column
    op.drop_column("users", "default_household_id")

"""Add household support for multi-user budgets

This migration adds household functionality to enable couples to share the same budget
while maintaining individual accounts.

Changes:
1. Create households table
2. Create user_household association table  
3. Create household_invites table
4. Add default_household_id to users table
5. Add household_id to funds, bills, and incomes tables (replacing user_id for shared resources)

Revision ID: household_multiuser_v1
Revises: 282e138cc91b
Create Date: 2025-11-05

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic
revision = 'household_multiuser_v1'
down_revision = '282e138cc91b'
branch_labels = None
depends_on = None


def upgrade():
    # Create households table
    op.create_table('households',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_household association table
    op.create_table('user_household',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('household_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=True, server_default='member'),
        sa.Column('joined_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['household_id'], ['households.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'household_id')
    )

    # Create household_invites table
    op.create_table('household_invites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('household_id', sa.Integer(), nullable=False),
        sa.Column('inviter_id', sa.Integer(), nullable=False),
        sa.Column('invitee_email', sa.String(length=120), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['household_id'], ['households.id'], ),
        sa.ForeignKeyConstraint(['inviter_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )

    # Add default_household_id to users table
    op.add_column('users', sa.Column('default_household_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_default_household', 'users', 'households', ['default_household_id'], ['id'])

    # DATA MIGRATION: Create default household for each existing user
    # This ensures backwards compatibility - single users get their own household
    connection = op.get_bind()
    
    # Get all existing users
    result = connection.execute(sa.text("SELECT id, username FROM users"))
    users = result.fetchall()
    
    for user in users:
        user_id = user[0]
        username = user[1]
        household_name = f"{username}'s Household"
        
        # Create household for this user
        connection.execute(
            sa.text("INSERT INTO households (name, created_by, created_at) VALUES (:name, :created_by, :created_at)"),
            {'name': household_name, 'created_by': user_id, 'created_at': datetime.utcnow()}
        )
        
        # Get the household ID we just created
        household_result = connection.execute(
            sa.text("SELECT id FROM households WHERE created_by = :user_id ORDER BY id DESC LIMIT 1"),
            {'user_id': user_id}
        )
        household_id = household_result.fetchone()[0]
        
        # Link user to their household as owner
        connection.execute(
            sa.text("INSERT INTO user_household (user_id, household_id, role, joined_at) VALUES (:user_id, :household_id, :role, :joined_at)"),
            {'user_id': user_id, 'household_id': household_id, 'role': 'owner', 'joined_at': datetime.utcnow()}
        )
        
        # Set as default household
        connection.execute(
            sa.text("UPDATE users SET default_household_id = :household_id WHERE id = :user_id"),
            {'household_id': household_id, 'user_id': user_id}
        )

    # Now update ALL tables to use household_id (complete transparency)
    # Add household_id columns (nullable initially)
    op.add_column('funds', sa.Column('household_id', sa.Integer(), nullable=True))
    op.add_column('bills', sa.Column('household_id', sa.Integer(), nullable=True))
    op.add_column('incomes', sa.Column('household_id', sa.Integer(), nullable=True))
    op.add_column('accounts', sa.Column('household_id', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column('household_id', sa.Integer(), nullable=True))
    op.add_column('debts', sa.Column('household_id', sa.Integer(), nullable=True))
    
    # Add owner tracking columns (to show which partner owns what)
    op.add_column('accounts', sa.Column('owner_user_id', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column('created_by_user_id', sa.Integer(), nullable=True))
    op.add_column('debts', sa.Column('owner_user_id', sa.Integer(), nullable=True))

    # Migrate existing data: set household_id based on user's default_household_id
    connection.execute(sa.text("""
        UPDATE funds SET household_id = (
            SELECT default_household_id FROM users WHERE users.id = funds.user_id
        )
    """))
    
    connection.execute(sa.text("""
        UPDATE bills SET household_id = (
            SELECT default_household_id FROM users WHERE users.id = bills.user_id
        )
    """))
    
    connection.execute(sa.text("""
        UPDATE incomes SET household_id = (
            SELECT default_household_id FROM users WHERE users.id = incomes.user_id
        )
    """))
    
    connection.execute(sa.text("""
        UPDATE accounts SET household_id = (
            SELECT default_household_id FROM users WHERE users.id = accounts.user_id
        ), owner_user_id = user_id
    """))
    
    connection.execute(sa.text("""
        UPDATE transactions SET household_id = (
            SELECT default_household_id FROM users WHERE users.id = transactions.user_id
        ), created_by_user_id = user_id
    """))
    
    connection.execute(sa.text("""
        UPDATE debts SET household_id = (
            SELECT default_household_id FROM users WHERE users.id = debts.user_id
        ), owner_user_id = user_id
    """))

    # Now make household_id NOT NULL and add foreign keys
    op.alter_column('funds', 'household_id', nullable=False)
    op.alter_column('bills', 'household_id', nullable=False)
    op.alter_column('incomes', 'household_id', nullable=False)
    op.alter_column('accounts', 'household_id', nullable=False)
    op.alter_column('transactions', 'household_id', nullable=False)
    op.alter_column('debts', 'household_id', nullable=False)

    op.create_foreign_key('fk_funds_household', 'funds', 'households', ['household_id'], ['id'])
    op.create_foreign_key('fk_bills_household', 'bills', 'households', ['household_id'], ['id'])
    op.create_foreign_key('fk_incomes_household', 'incomes', 'households', ['household_id'], ['id'])
    op.create_foreign_key('fk_accounts_household', 'accounts', 'households', ['household_id'], ['id'])
    op.create_foreign_key('fk_transactions_household', 'transactions', 'households', ['household_id'], ['id'])
    op.create_foreign_key('fk_debts_household', 'debts', 'households', ['household_id'], ['id'])
    
    # Add foreign keys for owner tracking
    op.create_foreign_key('fk_accounts_owner', 'accounts', 'users', ['owner_user_id'], ['id'])
    op.create_foreign_key('fk_transactions_creator', 'transactions', 'users', ['created_by_user_id'], ['id'])
    op.create_foreign_key('fk_debts_owner', 'debts', 'users', ['owner_user_id'], ['id'])

    # Drop old user_id columns from ALL tables
    op.drop_constraint('funds_user_id_fkey', 'funds', type_='foreignkey')
    op.drop_column('funds', 'user_id')
    
    op.drop_constraint('bills_user_id_fkey', 'bills', type_='foreignkey')
    op.drop_column('bills', 'user_id')
    
    op.drop_constraint('incomes_user_id_fkey', 'incomes', type_='foreignkey')
    op.drop_column('incomes', 'user_id')
    
    op.drop_constraint('accounts_user_id_fkey', 'accounts', type_='foreignkey')
    op.drop_column('accounts', 'user_id')
    
    op.drop_constraint('transactions_user_id_fkey', 'transactions', type_='foreignkey')
    op.drop_column('transactions', 'user_id')
    
    op.drop_constraint('debts_user_id_fkey', 'debts', type_='foreignkey')
    op.drop_column('debts', 'user_id')


def downgrade():
    # This is a complex migration - downgrade would require careful handling
    # For now, raise an error if someone tries to downgrade
    raise NotImplementedError("Downgrade from household multiuser is not supported. Please restore from backup if needed.")

# Add security question and answer columns to the User model in the database
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "users", sa.Column("security_question", sa.String(255), nullable=True)
    )
    op.add_column("users", sa.Column("security_answer", sa.String(255), nullable=True))


def downgrade():
    op.drop_column("users", "security_question")
    op.drop_column("users", "security_answer")

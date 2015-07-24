"""add method to requests table

Revision ID: 2a6588d61699
Revises: 1c262626e39e
Create Date: 2015-07-24 02:03:43.278658

"""

# revision identifiers, used by Alembic.
revision = '2a6588d61699'
down_revision = '1c262626e39e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('requests', sa.Column('method', sa.String(), nullable=True))


def downgrade():
    op.drop_column('requests', 'method')

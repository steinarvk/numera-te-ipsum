"""add comment field for events

Revision ID: 5a6cad53762
Revises: 214dffeaa6a8
Create Date: 2015-09-12 19:25:04.792718

"""

# revision identifiers, used by Alembic.
revision = '5a6cad53762'
down_revision = '214dffeaa6a8'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('event_record', sa.Column('comment', sa.String(), nullable=True))


def downgrade():
    op.drop_column('event_record', 'comment')

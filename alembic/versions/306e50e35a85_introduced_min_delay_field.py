"""introduced min_delay field

Revision ID: 306e50e35a85
Revises: 2a6588d61699
Create Date: 2015-07-24 03:08:06.714709

"""

# revision identifiers, used by Alembic.
revision = '306e50e35a85'
down_revision = '2a6588d61699'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('survey_questions', sa.Column('min_delay', sa.Interval(), nullable=True))


def downgrade():
    op.drop_column('survey_questions', 'min_delay')

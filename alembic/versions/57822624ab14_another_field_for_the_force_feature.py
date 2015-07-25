"""another field for the force feature

Revision ID: 57822624ab14
Revises: 306e50e35a85
Create Date: 2015-07-26 00:13:15.527600

"""

# revision identifiers, used by Alembic.
revision = '57822624ab14'
down_revision = '306e50e35a85'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('survey_questions', sa.Column('never_trigger_before', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('survey_questions', 'never_trigger_before')

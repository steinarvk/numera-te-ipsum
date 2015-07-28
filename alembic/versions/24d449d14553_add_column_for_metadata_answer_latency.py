"""add column for metadata answer latency

Revision ID: 24d449d14553
Revises: ff629752fe2
Create Date: 2015-07-28 01:49:54.567913

"""

# revision identifiers, used by Alembic.
revision = '24d449d14553'
down_revision = 'ff629752fe2'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('survey_answers', sa.Column('answer_latency', sa.Interval(), nullable=True))


def downgrade():
    op.drop_column('survey_answers', 'answer_latency')

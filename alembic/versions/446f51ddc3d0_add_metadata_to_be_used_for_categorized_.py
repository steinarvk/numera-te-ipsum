"""add metadata, to be used for categorized questions

Revision ID: 446f51ddc3d0
Revises: 43a2b49634d1
Create Date: 2015-08-28 19:48:41.403661

"""

# revision identifiers, used by Alembic.
revision = '446f51ddc3d0'
down_revision = '43a2b49634d1'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('survey_questions', sa.Column('metadata', sa.String(), nullable=True))


def downgrade():
    op.drop_column('survey_questions', 'metadata')

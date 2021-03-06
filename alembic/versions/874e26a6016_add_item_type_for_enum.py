"""add item type for enum

Revision ID: 874e26a6016
Revises: 1e22c2616ff4
Create Date: 2015-09-28 00:57:28.329712

"""

# revision identifiers, used by Alembic.
revision = '874e26a6016'
down_revision = '1e22c2616ff4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('items', 'trigger_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.execute('COMMIT')
    op.execute("ALTER TYPE query_type ADD VALUE 'item'")
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('items', 'trigger_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    ### end Alembic commands ###

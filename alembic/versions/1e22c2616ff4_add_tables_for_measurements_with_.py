"""add tables for measurements, with structure for general items table

Revision ID: 1e22c2616ff4
Revises: 58b4abd8149
Create Date: 2015-09-26 15:14:26.824136

"""

# revision identifiers, used by Alembic.
revision = '1e22c2616ff4'
down_revision = '58b4abd8149'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('items',
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('item_key', sa.String(), nullable=False),
    sa.Column('type', sa.Enum('measured_variable', name='item_type'), nullable=False),
    sa.Column('user_id_owner', sa.Integer(), nullable=False),
    sa.Column('trigger_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['trigger_id'], ['triggers.trigger_id'], ),
    sa.ForeignKeyConstraint(['user_id_owner'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('item_id')
    )
    op.create_index(op.f('ix_items_item_key'), 'items', ['item_key'], unique=False)
    op.create_table('measured_vars',
    sa.Column('measured_var_id', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['item_id'], ['items.item_id'], ),
    sa.PrimaryKeyConstraint('measured_var_id')
    )
    op.create_table('measured_var_units',
    sa.Column('measured_var_unit_id', sa.Integer(), nullable=False),
    sa.Column('measured_var_id', sa.Integer(), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=False),
    sa.Column('unit_key', sa.String(), nullable=False),
    sa.Column('singular', sa.String(), nullable=False),
    sa.Column('plural', sa.String(), nullable=False),
    sa.Column('precision', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['measured_var_id'], ['measured_vars.measured_var_id'], ),
    sa.PrimaryKeyConstraint('measured_var_unit_id')
    )
    op.create_table('measurements',
    sa.Column('measurement_id', sa.Integer(), nullable=False),
    sa.Column('measured_var_id', sa.Integer(), nullable=False),
    sa.Column('req_id_creator', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('value', sa.Numeric(), nullable=False),
    sa.Column('unit_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['measured_var_id'], ['measured_vars.measured_var_id'], ),
    sa.ForeignKeyConstraint(['req_id_creator'], ['requests.req_id'], ),
    sa.ForeignKeyConstraint(['unit_id'], ['measured_var_units.measured_var_unit_id'], ),
    sa.PrimaryKeyConstraint('measurement_id')
    )
    op.create_index(op.f('ix_measurements_timestamp'), 'measurements', ['timestamp'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_measurements_timestamp'), table_name='measurements')
    op.drop_table('measurements')
    op.drop_table('measured_var_units')
    op.drop_table('measured_vars')
    op.drop_index(op.f('ix_items_item_key'), table_name='items')
    op.drop_table('items')
    ### end Alembic commands ###

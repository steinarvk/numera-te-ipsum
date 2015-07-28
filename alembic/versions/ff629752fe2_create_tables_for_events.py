"""create tables for events

Revision ID: ff629752fe2
Revises: 57822624ab14
Create Date: 2015-07-28 01:33:38.772732

"""

# revision identifiers, used by Alembic.
revision = 'ff629752fe2'
down_revision = '57822624ab14'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('event_types',
    sa.Column('evt_id', sa.Integer(), nullable=False),
    sa.Column('req_id_creator', sa.Integer(), nullable=True),
    sa.Column('user_id_owner', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('use_duration', sa.Boolean(), nullable=False),
    sa.Column('mean_inactive_delay', sa.Interval(), nullable=False),
    sa.Column('next_trigger', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['req_id_creator'], ['requests.req_id'], ),
    sa.ForeignKeyConstraint(['user_id_owner'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('evt_id')
    )
    op.create_index(op.f('ix_event_types_next_trigger'), 'event_types', ['next_trigger'], unique=False)
    op.create_table('event_record',
    sa.Column('evr_id', sa.Integer(), nullable=False),
    sa.Column('req_id_creator', sa.Integer(), nullable=True),
    sa.Column('user_id_owner', sa.Integer(), nullable=True),
    sa.Column('evt_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('on', 'off', 'unknown', 'unreported', name="event_state"), nullable=False),
    sa.Column('start', sa.DateTime(), nullable=False),
    sa.Column('end', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['evt_id'], ['event_types.evt_id'], ),
    sa.ForeignKeyConstraint(['req_id_creator'], ['requests.req_id'], ),
    sa.ForeignKeyConstraint(['user_id_owner'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('evr_id')
    )
    op.create_index(op.f('ix_event_record_end'), 'event_record', ['end'], unique=False)
    op.create_index(op.f('ix_event_record_start'), 'event_record', ['start'], unique=False)
    op.create_index(op.f('ix_event_record_status'), 'event_record', ['status'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_event_record_status'), table_name='event_record')
    op.drop_index(op.f('ix_event_record_start'), table_name='event_record')
    op.drop_index(op.f('ix_event_record_end'), table_name='event_record')
    op.drop_table('event_record')
    op.drop_index(op.f('ix_event_types_next_trigger'), table_name='event_types')
    op.drop_table('event_types')
    conn = op.get_bind()
    conn.execute(sa.text("drop type event_state"))

"""add chess tables

Revision ID: 58b4abd8149
Revises: 5a6cad53762
Create Date: 2015-09-25 01:50:39.590970

"""

# revision identifiers, used by Alembic.
revision = '58b4abd8149'
down_revision = '5a6cad53762'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('chess_puzzles',
    sa.Column('chess_puzzle_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('req_id_creator', sa.Integer(), nullable=True),
    sa.Column('user_id_owner', sa.Integer(), nullable=True),
    sa.Column('fen', sa.String(), nullable=False),
    sa.Column('deadline', sa.Integer(), nullable=True),
    sa.Column('pgn', sa.String(), nullable=True),
    sa.Column('move_number', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['req_id_creator'], ['requests.req_id'], ),
    sa.ForeignKeyConstraint(['user_id_owner'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('chess_puzzle_id')
    )
    op.create_table('chess_answers',
    sa.Column('chess_answer_id', sa.Integer(), nullable=False),
    sa.Column('chess_puzzle_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('req_id_creator', sa.Integer(), nullable=True),
    sa.Column('user_id_owner', sa.Integer(), nullable=True),
    sa.Column('move', sa.String(), nullable=True),
    sa.Column('expired', sa.Boolean(), nullable=False),
    sa.Column('answer_latency', sa.Interval(), nullable=True),
    sa.ForeignKeyConstraint(['chess_puzzle_id'], ['chess_puzzles.chess_puzzle_id'], ),
    sa.ForeignKeyConstraint(['req_id_creator'], ['requests.req_id'], ),
    sa.ForeignKeyConstraint(['user_id_owner'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('chess_answer_id')
    )


def downgrade():
    op.drop_table('chess_answers')
    op.drop_table('chess_puzzles')

"""added survey questions and answers table

Revision ID: 1c262626e39e
Revises: 1ba7a70153e2
Create Date: 2015-07-18 20:31:22.597284

"""

# revision identifiers, used by Alembic.
revision = '1c262626e39e'
down_revision = '1ba7a70153e2'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('survey_questions',
    sa.Column('sq_id', sa.Integer(), nullable=False),
    sa.Column('req_id_creator', sa.Integer(), nullable=True),
    sa.Column('user_id_owner', sa.Integer(), nullable=True),
    sa.Column('question', sa.String(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('low_label', sa.String(), nullable=True),
    sa.Column('high_label', sa.String(), nullable=True),
    sa.Column('middle_label', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('mean_delay', sa.Interval(), nullable=False),
    sa.Column('next_trigger', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['req_id_creator'], ['requests.req_id'], ),
    sa.ForeignKeyConstraint(['user_id_owner'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('sq_id')
    )
    op.create_index(op.f('ix_survey_questions_next_trigger'), 'survey_questions', ['next_trigger'], unique=False)
    op.create_table('survey_answers',
    sa.Column('sa_id', sa.Integer(), nullable=False),
    sa.Column('req_id_creator', sa.Integer(), nullable=True),
    sa.Column('user_id_owner', sa.Integer(), nullable=True),
    sa.Column('sq_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('value', sa.Numeric(), nullable=False),
    sa.ForeignKeyConstraint(['req_id_creator'], ['requests.req_id'], ),
    sa.ForeignKeyConstraint(['sq_id'], ['survey_questions.sq_id'], ),
    sa.ForeignKeyConstraint(['user_id_owner'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('sa_id')
    )
    op.create_index(op.f('ix_survey_answers_timestamp'), 'survey_answers', ['timestamp'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_survey_answers_timestamp'), table_name='survey_answers')
    op.drop_table('survey_answers')
    op.drop_index(op.f('ix_survey_questions_next_trigger'), table_name='survey_questions')
    op.drop_table('survey_questions')
    ### end Alembic commands ###

"""add owner to triggers

Revision ID: 53046aa18bde
Revises: 88c7618da82
Create Date: 2015-08-08 01:06:58.748723

"""

# revision identifiers, used by Alembic.
revision = '53046aa18bde'
down_revision = '88c7618da82'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

import qs2.model as M


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('triggers', sa.Column('user_id_owner', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'triggers', 'users', ['user_id_owner'], ['user_id'])
    ### end Alembic commands ###
    conn = op.get_bind()
    op.execute("""
      UPDATE triggers SET user_id_owner = survey_questions.user_id_owner
      FROM survey_questions
      WHERE survey_questions.trigger_id = triggers.trigger_id
    """)

def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'triggers', type_='foreignkey')
    op.drop_column('triggers', 'user_id_owner')
    ### end Alembic commands ###

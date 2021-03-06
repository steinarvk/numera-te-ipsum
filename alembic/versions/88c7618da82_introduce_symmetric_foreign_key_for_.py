"""introduce symmetric foreign key for triggers

Revision ID: 88c7618da82
Revises: 48597efc947
Create Date: 2015-08-08 00:58:54.798328

"""

# revision identifiers, used by Alembic.
revision = '88c7618da82'
down_revision = '48597efc947'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

import qs2.model as M


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('triggers', sa.Column('survey_question_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'triggers', 'survey_questions', ['survey_question_id'], ['sq_id'])
    ### end Alembic commands ###
    conn = op.get_bind()
    with conn.begin() as trans:
      rows = conn.execute(sa.select([
        M.survey_questions.c.sq_id,
        M.survey_questions.c.trigger_id,
      ]))
      for row in rows:
        conn.execute(sa.update(M.triggers).where(
          M.triggers.c.trigger_id == row.trigger_id).values(
          survey_question_id=row.sq_id))

def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'triggers', type_='foreignkey')
    op.drop_column('triggers', 'survey_question_id')
    ### end Alembic commands ###

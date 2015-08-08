"""step 1 of factoring out triggers table

Revision ID: 4e053afee480
Revises: 24d449d14553
Create Date: 2015-08-07 22:39:26.685391

"""

# revision identifiers, used by Alembic.
revision = '4e053afee480'
down_revision = '24d449d14553'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

import qs2.model as M


def upgrade():
    ### Alembic autogenerated
    op.create_table('triggers',
    sa.Column('trigger_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('question', 'event', name='query_type'), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('min_delay', sa.Interval(), nullable=True),
    sa.Column('mean_delay', sa.Interval(), nullable=False),
    sa.Column('never_trigger_before', sa.DateTime(), nullable=True),
    sa.Column('next_trigger', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('trigger_id')
    )
    op.create_index(op.f('ix_triggers_next_trigger'), 'triggers', ['next_trigger'], unique=False)
    op.add_column(u'survey_questions', sa.Column('trigger_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'survey_questions', 'triggers', ['trigger_id'], ['trigger_id'])
    ### end Alembic autogenerated
    # Populate the table!
    # (from survey_questions only, the events are not implemented yet)
    conn = op.get_bind()
    with conn.begin() as trans:
      rows = conn.execute(sa.select([M.survey_questions]))
      for row in rows:
        trigger_id = conn.execute(M.triggers.insert().values(
          type="question",
          active=row.active,
          min_delay=row.min_delay,
          mean_delay=row.mean_delay,
          never_trigger_before=row.never_trigger_before,
          next_trigger=row.next_trigger,
        )).inserted_primary_key[0]
        query = sa.update(M.survey_questions)
        query = query.where(M.survey_questions.c.sq_id == row.sq_id)
        query = query.values(trigger_id = trigger_id)
        conn.execute(query)

def downgrade():
    # There's no need to be explicit about de-populating the table, since
    # this drops the relevant table and columns in any case.
    ### commands auto generated by Alembic
    op.drop_constraint(None, 'survey_questions', type_='foreignkey')
    op.drop_column(u'survey_questions', 'trigger_id')
    op.drop_index(op.f('ix_triggers_next_trigger'), table_name='triggers')
    op.drop_table('triggers')
    ### end Alembic commands ###
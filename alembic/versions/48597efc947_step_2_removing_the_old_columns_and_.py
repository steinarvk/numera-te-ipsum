"""step 2, removing the old columns and making foreign key non-nullable

Revision ID: 48597efc947
Revises: 4e053afee480
Create Date: 2015-08-07 23:20:41.723749

"""

# revision identifiers, used by Alembic.
revision = '48597efc947'
down_revision = '4e053afee480'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

import qs2.model as M

from sqlalchemy import (
  Table, Column, MetaData, ForeignKey,
  UniqueConstraint,
  Integer, String, DateTime, Numeric, Interval, Boolean, Enum,
)

old_metadata = MetaData()
old_survey_questions = Table("survey_questions", old_metadata,
  Column("sq_id", Integer, primary_key=True),
  Column("req_id_creator", Integer, ForeignKey("requests.req_id")),
  Column("user_id_owner", Integer, ForeignKey("users.user_id")),
  Column("trigger_id", Integer, ForeignKey("triggers.trigger_id"), nullable=False),
  Column("question", String, nullable=False),
  Column("timestamp", DateTime),
  Column("low_label", String),
  Column("high_label", String),
  Column("middle_label", String),
  Column("active", Boolean, nullable=False),
  Column("min_delay", Interval),
  Column("mean_delay", Interval, nullable=False),
  Column("never_trigger_before", DateTime),
  Column("next_trigger", DateTime, index=True),
)


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('survey_questions', 'trigger_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_index('ix_survey_questions_next_trigger', table_name='survey_questions')
    op.drop_column('survey_questions', 'active')
    op.drop_column('survey_questions', 'next_trigger')
    op.drop_column('survey_questions', 'never_trigger_before')
    op.drop_column('survey_questions', 'min_delay')
    op.drop_column('survey_questions', 'mean_delay')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('survey_questions', sa.Column('mean_delay', postgresql.INTERVAL(), autoincrement=False, nullable=True)) # to be set as NOT NULL later
    op.add_column('survey_questions', sa.Column('min_delay', postgresql.INTERVAL(), autoincrement=False, nullable=True))
    op.add_column('survey_questions', sa.Column('never_trigger_before', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('survey_questions', sa.Column('next_trigger', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('survey_questions', sa.Column('active', sa.BOOLEAN(), autoincrement=False, nullable=True)) # to be set as NOT NULL later
    op.create_index('ix_survey_questions_next_trigger', 'survey_questions', ['next_trigger'], unique=False)
    op.alter_column('survey_questions', 'trigger_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    ### end Alembic commands ###
    # Populate survey_questions from triggers
    conn = op.get_bind()
    with conn.begin() as trans:
      rows = conn.execute(sa.select([
        old_survey_questions.c.sq_id,
        M.triggers.c.mean_delay,
        M.triggers.c.min_delay,
        M.triggers.c.never_trigger_before,
        M.triggers.c.next_trigger,
        M.triggers.c.active,
      ]).where(old_survey_questions.c.trigger_id == M.triggers.c.trigger_id))
      rows = list(rows)
      for row in rows:
        query = sa.update(old_survey_questions)
        query = query.where(old_survey_questions.c.sq_id == row.sq_id)
        query = query.values(
          mean_delay=row.mean_delay,
          min_delay=row.min_delay,
          never_trigger_before=row.never_trigger_before,
          next_trigger=row.next_trigger,
          active=row.active,
        )
        conn.execute(query)
    # Now we can mark the new columns as non-null
    op.alter_column('survey_questions', 'mean_delay',
               existing_type=postgresql.INTERVAL(),
               nullable=True)
    op.alter_column('survey_questions', 'active',
               existing_type=postgresql.BOOLEAN(),
               nullable=True)

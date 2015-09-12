"""update all datetimes to have time zones

Revision ID: 214dffeaa6a8
Revises: 446f51ddc3d0
Create Date: 2015-09-12 16:40:22.499090

"""

# revision identifiers, used by Alembic.
revision = '214dffeaa6a8'
down_revision = '446f51ddc3d0'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

_table_columns = [
  ("requests", "timestamp"),
  ("users", "timestamp"),
  ("survey_questions", "timestamp"),
  ("survey_answers", "timestamp"),
  ("triggers", "never_trigger_before"),
  ("triggers", "next_trigger"),
  ("event_types", "timestamp"),
  ("event_record", "start"),
  ("event_record", "end"),
]

def upgrade():
    for table, column in _table_columns:
      op.alter_column(table, column,
        existing_type = sa.DateTime(timezone=False),
        type_ = sa.DateTime(timezone=True),
      )


def downgrade():
    for table, column in _table_columns:
      op.alter_column(table, column,
        type_ = sa.DateTime(timezone=False),
        existing_type = sa.DateTime(timezone=True),
      )

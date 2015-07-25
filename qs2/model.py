from sqlalchemy import (
  Table, Column, MetaData, ForeignKey,
  UniqueConstraint,
  Integer, String, ForeignKey, DateTime, Numeric, Interval, Boolean,
)

metadata = MetaData()

requests = Table("requests", metadata,
  Column("req_id", Integer, primary_key=True),
  Column("timestamp", DateTime),
  Column("server_version", String),
  Column("client_ip", String),
  Column("url", String),
  Column("referer", String),
  Column("user_agent", String),
  Column("method", String),
)

users = Table("users", metadata,
  Column("user_id", Integer, primary_key=True),
  Column("req_id_creator", Integer, ForeignKey("requests.req_id")),
  Column("timestamp", DateTime),
  Column("username", String, nullable=False, index=True),
  Column("password_hash", String, nullable=False),
  UniqueConstraint("username", name="username_is_unique"),
)

survey_questions = Table("survey_questions", metadata,
  Column("sq_id", Integer, primary_key=True),
  Column("req_id_creator", Integer, ForeignKey("requests.req_id")),
  Column("user_id_owner", Integer, ForeignKey("users.user_id")),
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

survey_answers = Table("survey_answers", metadata,
  Column("sa_id", Integer, primary_key=True),
  Column("req_id_creator", Integer, ForeignKey("requests.req_id")),
  Column("user_id_owner", Integer, ForeignKey("users.user_id")),
  Column("sq_id", Integer, ForeignKey("survey_questions.sq_id"),
    nullable=False),
  Column("timestamp", DateTime, nullable=False, index=True),
  Column("value", Numeric, nullable=False),
)

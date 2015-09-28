from sqlalchemy import (
  Table, Column, MetaData, ForeignKey,
  UniqueConstraint,
  Integer, String, Numeric, Interval, Boolean, Enum,
)
import sqlalchemy
DateTimeTz = sqlalchemy.DateTime(timezone=True)

metadata = MetaData()

requests = Table("requests", metadata,
  Column("req_id", Integer, primary_key=True),
  Column("timestamp", DateTimeTz),
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
  Column("timestamp", DateTimeTz),
  Column("username", String, nullable=False, index=True),
  Column("password_hash", String, nullable=False),
  UniqueConstraint("username", name="username_is_unique"),
)

survey_questions = Table("survey_questions", metadata,
  Column("sq_id", Integer, primary_key=True),
  Column("req_id_creator", Integer, ForeignKey("requests.req_id")),
  Column("user_id_owner", Integer, ForeignKey("users.user_id")),
  Column("trigger_id", Integer, ForeignKey("triggers.trigger_id"), nullable=False),
  Column("question", String, nullable=False),
  Column("metadata", String, nullable=True),
  Column("timestamp", DateTimeTz),
  Column("low_label", String),
  Column("high_label", String),
  Column("middle_label", String),
)

survey_answers = Table("survey_answers", metadata,
  Column("sa_id", Integer, primary_key=True),
  Column("req_id_creator", Integer, ForeignKey("requests.req_id")),
  Column("user_id_owner", Integer, ForeignKey("users.user_id")),
  Column("sq_id", Integer, ForeignKey("survey_questions.sq_id"),
    nullable=False),
  Column("timestamp", DateTimeTz, nullable=False, index=True),
  Column("value", Numeric, nullable=False),
  Column("answer_latency", Interval, nullable=True),
)

query_type = Enum("question", "event", "item",
  name="query_type")

triggers = Table("triggers", metadata,
  Column("trigger_id", Integer, primary_key=True),
  Column("type", query_type, nullable=False),
  Column("user_id_owner", Integer, ForeignKey("users.user_id")),
  Column("active", Boolean, nullable=False),
  Column("min_delay", Interval),
  Column("mean_delay", Interval, nullable=False),
  Column("never_trigger_before", DateTimeTz),
  Column("next_trigger", DateTimeTz, index=True),
)

event_types = Table("event_types", metadata,
  Column("evt_id", Integer, primary_key=True),
  Column("req_id_creator", Integer, ForeignKey("requests.req_id")),
  Column("user_id_owner", Integer, ForeignKey("users.user_id")),
  Column("trigger_id", Integer, ForeignKey("triggers.trigger_id")),
  Column("name", String, nullable=False),
  Column("use_duration", Boolean, nullable=False),
  Column("timestamp", DateTimeTz),
)

event_record = Table("event_record", metadata,
  Column("evr_id", Integer, primary_key=True),
  Column("req_id_creator", Integer, ForeignKey("requests.req_id")),
  Column("user_id_owner", Integer, ForeignKey("users.user_id")),
  Column("evt_id", Integer, ForeignKey("event_types.evt_id")),
  Column("status", Enum("on", "off", "unknown", "unreported"),
    nullable=False, index=True),
  Column("start", DateTimeTz, nullable=False, index=True),
  Column("end", DateTimeTz, nullable=False, index=True),
  Column("comment", String),
)

chess_puzzles = Table("chess_puzzles", metadata,
  Column("chess_puzzle_id", Integer, primary_key=True),
  Column("timestamp", DateTimeTz, nullable=False),
  Column("req_id_creator", Integer, ForeignKey("requests.req_id")),
  Column("user_id_owner", Integer, ForeignKey("users.user_id")),
  Column("fen", String, nullable=False),
  Column("deadline", Integer),
  Column("pgn", String, nullable=True),
  Column("move_number", Integer, nullable=True),
)

chess_answers = Table("chess_answers", metadata,
  Column("chess_answer_id", Integer, primary_key=True),
  Column("chess_puzzle_id", Integer, ForeignKey("chess_puzzles.chess_puzzle_id")),
  Column("timestamp", DateTimeTz, nullable=False),
  Column("req_id_creator", Integer, ForeignKey("requests.req_id")),
  Column("user_id_owner", Integer, ForeignKey("users.user_id")),
  Column("move", String, nullable=True),
  Column("expired", Boolean, nullable=False),
  Column("answer_latency", Interval, nullable=True),
)

item_type = Enum("measured_variable",
  name="item_type")

items = Table("items", metadata,
  Column("item_id", Integer, primary_key=True),
  Column("item_key", String, nullable=False, index=True),
  Column("type", item_type, nullable=False),
  Column("user_id_owner", Integer, ForeignKey("users.user_id"), nullable=False),
  Column("trigger_id", Integer, ForeignKey("triggers.trigger_id"), nullable=True),
)

measured_vars = Table("measured_vars", metadata,
  Column("measured_var_id", Integer, primary_key=True),
  Column("item_id", Integer, ForeignKey("items.item_id"), nullable=False),
  Column("name", String, nullable=False),
)

measurements = Table("measurements", metadata,
  Column("measurement_id", Integer, primary_key=True),
  Column("measured_var_id", Integer, ForeignKey("measured_vars.measured_var_id"), nullable=False),
  Column("req_id_creator", Integer, ForeignKey("requests.req_id")),
  Column("timestamp", DateTimeTz, nullable=False, index=True),
  Column("value", Numeric, nullable=False),
  Column("unit_id", Integer, ForeignKey("measured_var_units.measured_var_unit_id"), nullable=False),
)

measured_var_units = Table("measured_var_units", metadata,
  Column("measured_var_unit_id", Integer, primary_key=True),
  Column("measured_var_id", Integer, ForeignKey("measured_vars.measured_var_id"), nullable=False),
  Column("priority", Integer, nullable=False, default=0),
  Column("unit_key", String, nullable=False, index=True),
  Column("singular", String, nullable=False),
  Column("plural", String, nullable=False),
  Column("precision", Integer, nullable=False, default=0),
  UniqueConstraint("measured_var_id", "unit_key",
    name="key_is_unique_within_measured_var"),
)

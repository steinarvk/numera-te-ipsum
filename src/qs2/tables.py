from sqlalchemy import (
  Table, Column, MetaData, ForeignKey,
  Integer, String, ForeignKey, DateTime, Numeric,
)

metadata = MetaData()

requests = Table("requests", metadata,
  Column("req_id", Integer, primary_key=True),
  Column("timestamp", DateTime),
  Column("server_version", String),
  Column("client_ip", String),
  Column("url", String),
  Column("referer", String),
  Column("user_agent", String)
)

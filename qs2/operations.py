from qs2 import model
import qs2.users
import qs2.validation
import getpass
import datetime
import users
import logging
import time
import qs2.logutil
import sqlalchemy

from sqlalchemy import sql

from qs2.error import OperationFailed

def sql_op(name, func):
  with qs2.logutil.lowlevel_section("SQL operation ({})".format(name)):
    try:
      result = func()
    except sqlalchemy.exc.SQLAlchemyError as e:
      logging.exception(e)
      raise OperationFailed("SQL operation failed: {}".format(name))
    return result

def full_reset():
  message = "Really delete the entire database, losing all data?"
  confirm = raw_input("{} ['yes' to continue] ".format(message))
  if confirm.strip() != "yes":
    raise OperationFailed("user aborted")
  with qs2.logutil.section("deleting the database"):
    model.metadata.delete_all()
  initialize()

def initialize():
  with qs2.logutil.section("initializing the database"):
    model.metadata.create_all()

def add_user(username, password):
  qs2.validation.check("username", username)
  qs2.validation.check("password", password, secret=True)
  query = model.users.insert().values(
    timestamp=datetime.datetime.now(),
    username=username,
    password_hash=users.hash_password(password)
  )
  (user_id,) = sql_op("create user", query.execute).inserted_primary_key
  logging.info("created user '%s' (%d)", username, user_id)

def authenticate_user(username, password):
  query = sql.select(
    [model.users.c.user_id,
     model.users.c.password_hash]).where(
      model.users.c.username == username
  )
  row = sql_op("fetch user", query.execute).fetchone()
  ok = users.verify_password(password, row["password_hash"])
  if ok:
    return row["user_id"]

def verify_user_interactive(username):
  password = getpass.getpass("Password: ")
  user_id = authenticate_user(username, password)
  if not user_id:
    raise OperationFailed("authentication failed")
  logging.info("verified as user %d/%s", user_id, username)

def add_user_interactive(username):
  qs2.validation.check("username", username)
  password = getpass.getpass("Password: ")
  repeat_password = getpass.getpass("Confirm password: ")
  if password != repeat_password:
    raise OperationFailed("user input error -- passwords did not match")
  add_user(username, password)

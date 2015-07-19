from qs2 import model
import qs2.users
import qs2.validation
import datetime
import users
import decimal
import logging
import time
import qs2.logutil
import sqlalchemy
import random

from qs2 import ui

from sqlalchemy import sql

from qs2.error import OperationFailed

def sql_op(conn, name, query):
  with qs2.logutil.lowlevel_section("SQL operation ({})".format(name)):
    try:
      result = conn.execute(query)
    except sqlalchemy.exc.SQLAlchemyError as e:
      logging.exception(e)
      raise OperationFailed("SQL operation failed: {}".format(name))
    return result

def strict_confirm(message):
  confirm = ui.UI.raw_input("{} ['yes' to continue] ".format(message))
  if confirm.strip() != "yes":
    raise OperationFailed("user aborted")

def confirm(message):
  while True:
    letter = ui.UI.raw_input("{} [Yn] ".format(message)).lower()
    if letter in ("", "y"):
      return
    if letter == "n":
      raise OperationFailed("user aborted")

def drop_all(conn):
  strict_confirm("Really delete the entire database, losing all data?")
  with qs2.logutil.section("dropping the database"):
    model.metadata.reflect(conn)
    model.metadata.drop_all(conn)

def initialize(conn):
  with qs2.logutil.section("initializing the database"):
    model.metadata.create_all(conn)

def add_user(conn, username, password):
  qs2.validation.check("username", username)
  qs2.validation.check("password", password, secret=True)
  query = model.users.insert().values(
    timestamp=datetime.datetime.now(),
    username=username,
    password_hash=users.hash_password(password)
  )
  (user_id,) = sql_op(conn, "create user", query).inserted_primary_key
  logging.info("created user '%s' (%d)", username, user_id)
  return user_id

def get_user_id(conn, username):
  query = sql.select([model.users.c.user_id]).where(
    model.users.c.username == username
  )
  row = sql_op(conn, "fetch user", query).fetchone()
  if not row:
    raise OperationFailed("user ('{}') not found".format(username))
  return row["user_id"]

def authenticate_user(conn, username, password):
  query = sql.select(
    [model.users.c.user_id,
     model.users.c.password_hash]).where(
      model.users.c.username == username
  )
  row = sql_op(conn, "fetch user", query).fetchone()
  ok = users.verify_password(password, row["password_hash"])
  if ok:
    return row["user_id"]

def verify_user_interactive(conn, username):
  password = ui.UI.getpass("Password for {}: ".format(username))
  user_id = authenticate_user(conn, username, password)
  if not user_id:
    raise OperationFailed("authentication failed")
  logging.info("verified as user %d/%s", user_id, username)
  return user_id

def add_user_interactive(conn, username):
  qs2.validation.check("username", username)
  password = ui.UI.getpass("Password: ")
  repeat_password = ui.UI.getpass("Confirm password: ")
  if password != repeat_password:
    raise OperationFailed("user input error -- passwords did not match")
  add_user(conn, username, password)

def cli_query_form(*fields):
  rv = {}
  for field_key, field_name, required, convert in fields:
    text = ui.UI.raw_input("Enter {}: ".format(field_name)).strip()
    if not required and not text:
      print "{}: skipped".format(field_name)
      continue
    rv[field_key] = convert(text)
    print "{}: '{}'".format(field_name, rv[field_key])
  return rv

def add_question(conn, user_id, question, low_label, high_label,
                 middle_label=None,
                 req_id_creator=None,
                 active=True,
                 delay_s=3600):
  qs2.validation.check("question", question, secret=True)
  qs2.validation.check("label", low_label, secret=True)
  qs2.validation.check("label", high_label, secret=True)
  if middle_label:
    qs2.validation.check("label", middle_label, secret=True)
  now = datetime.datetime.now()
  query = model.survey_questions.insert().values(
    timestamp=now,
    user_id_owner=user_id,
    question=question,
    low_label=low_label,
    high_label=high_label,
    middle_label=middle_label,
    active=active,
    mean_delay=datetime.timedelta(seconds=delay_s),
    next_trigger=now,
    req_id_creator=req_id_creator,
  )
  (sq_id,) = sql_op(conn, "create question", query).inserted_primary_key
  logging.info("created question #%d", sq_id)
  return sq_id
  
def maybe_auth(conn, username, skip_auth):
  if skip_auth:
    return get_user_id(conn, username)
  else:
    return verify_user_interactive(conn, username)

def question_queue_query(user_id):
  return sql.select([model.survey_questions]).where(
    (model.survey_questions.c.user_id_owner == user_id) &
    (model.survey_questions.c.active)
  ).order_by(model.survey_questions.c.next_trigger.asc())

def get_all_questions(conn, user_id, *columns):
  if not columns:
    columns = [model.survey_questions]
  query = sql.select(columns).where(
    (model.survey_questions.c.user_id_owner == user_id)
  ).order_by(model.survey_questions.c.timestamp.asc())
  return map(dict, sql_op(conn, "fetch questions", query).fetchall())

def get_pending_questions(conn, user_id, *columns):
  if not columns:
    columns = [model.survey_questions]
  now = datetime.datetime.now()
  query = sql.select(columns).where(
    (model.survey_questions.c.user_id_owner == user_id) &
    (model.survey_questions.c.active) &
    (model.survey_questions.c.next_trigger < now)
  ).order_by(model.survey_questions.c.next_trigger.asc())
  return map(dict, sql_op(conn, "fetch pending questions", query).fetchall())


def peek_question(conn, user_id):
  query = question_queue_query(user_id)
  row = sql_op(conn, "fetch question", query).fetchone()
  return dict(row)

def fetch_question(conn, user_id, question_id, *columns):
  if not columns:
    columns = [model.survey_questions]
  query = sql.select(columns).where(
    (model.survey_questions.c.user_id_owner == user_id) &
    (model.survey_questions.c.sq_id == question_id)
  )
  row = sql_op(conn, "fetch question by ID", query).fetchone()
  if row:
    return dict(row)

def peek_question_interactive(conn, username, skip_auth=False):
  user_id = maybe_auth(conn, username, skip_auth)
  row = peek_question(conn, user_id)
  for key, value in row.items():
    print key, "\t", value

def symmetric_truncated_gauss(sigma, clip):
  assert clip > 0
  while True:
    rv = random.gauss(0, sigma)
    if abs(rv) < clip:
      return rv

def randomize_next_delay(mean_delay):
  k = 1 + symmetric_truncated_gauss(0.5, 1)
  return datetime.timedelta(seconds=k * mean_delay.total_seconds())

def post_answer(conn, user_id, question_id, value, req_id_creator=None):
  now = datetime.datetime.now()
  qs2.validation.check("survey_value", value)
  with conn.begin() as trans:
    question = fetch_question(conn, user_id, question_id,
      model.survey_questions.c.mean_delay,
      model.survey_questions.c.next_trigger)
    delay = randomize_next_delay(question["mean_delay"])
    logging.info("delaying for %s", delay)
    query = model.survey_answers.insert().values(
      timestamp=now,
      user_id_owner=user_id,
      sq_id=question_id,
      value=value,
      req_id_creator=req_id_creator,
    )
    (answer_id,) = sql_op(conn, "create answer", query).inserted_primary_key
    query = model.survey_questions.update().values(
      next_trigger = now + delay,
    ).where(model.survey_questions.c.sq_id == question_id)
    sql_op(conn, "update next question trigger", query)
    return answer_id

def post_answer_interactive(conn, username, question_id, value, skip_auth=False):
  qs2.validation.check("survey_value", value)
  user_id = maybe_auth(conn, username, skip_auth)
  question = fetch_question(conn, user_id, question_id)
  confirm("Answer {} to question '{}'? (0 = {}, 1 = {})".format(
    value, question["question"], question["low_label"], question["high_label"],
  ))
  post_answer(conn, user_id, question_id, value)

def add_question_interactive(conn, username, skip_auth=False):
  user_id = maybe_auth(conn, username, skip_auth)
  data = cli_query_form(
    ("question", "question", True, str),
    ("low_label", "lower/left label", True, str),
    ("high_label", "upper/right label", True, str),
    ("middle_label", "middle label", False, str),
    ("delay_s", "mean delay (seconds)", False, int),
  )
  for key, value in data.items():
    print key, "\t", value
  confirm("Add this question?")
  add_question(conn, user_id=user_id, **data)

def format_scale(q):
  rv = []
  for key, value in zip(("low_label", "middle_label", "high_label"),
                        (0, 50, 100)):
    if key in q:
      rv.append("{} ({}%)".format(q[key], value))
  return " ... ".join(rv)

def display_question(q):
  print "Question:", q["question"]
  print "Trigger time:", q["next_trigger"]
  print format_scale(q)

def survey_interactive(conn, username, accept_stale=False):
  user_id = verify_user_interactive(conn, username)
  while True:
    now = datetime.datetime.now()
    q = peek_question(conn, user_id)
    stale = q["next_trigger"] > now
    if stale and not accept_stale:
      break
    display_question(q)
    value = qs2.validation.ask("survey_value", decimal.Decimal,
                               ui.UI.raw_input, logging.error)
    now = datetime.datetime.now()
    post_answer(conn, user_id, q["sq_id"], value)

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
import csv
import json
import pytz

from qs2 import ui
import qs2.csvexport

from qs2.timeutil import (hacky_force_timezone, truncate_to_second_resolution)

from sqlalchemy import sql

from qs2.error import OperationFailed, ValidationFailed
from qs2.dbutil import sql_op
from qs2.dbutil import create_trigger

PRIORITY_NORMAL = 0
PRIORITY_CORRECTION = -10

class DbFetch(object):
  def __init__(self, conn, columns=[], **kwargs):
    self.conn = conn
    self.columns = columns
    self.option = kwargs

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

def fetch_chess_puzzle(conn, user_id, chess_puzzle_id):
  logging.info("attempting to fetch chess puzzle %d for user %d", chess_puzzle_id, user_id)
  columns = [model.chess_puzzles]
  query = sql.select(columns).where(
    (model.chess_puzzles.c.user_id_owner == user_id) &
    (model.chess_puzzles.c.chess_puzzle_id == chess_puzzle_id)
  )
  row = sql_op(conn, "fetch chess puzzle by ID", query).fetchone()
  if row:
    return dict(row)

def post_chess_puzzle_answer(conn, user_id, req_id, chess_puzzle_id, timestamp, move, expired, answer_latency):
  with conn.begin() as trans:
    query = sql.select([model.chess_answers.c.chess_answer_id]).where(
      (model.chess_answers.c.user_id_owner == user_id) &
      (model.chess_answers.c.chess_puzzle_id == chess_puzzle_id)
    ).limit(1)
    rows = sql_op(conn, "looking for prior answers", query).fetchall()
    if len(rows) > 0:
      raise OperationFailed("puzzle already answered")
    query = model.chess_answers.insert().values(
      timestamp=timestamp,
      user_id_owner=user_id,
      req_id_creator=req_id,
      chess_puzzle_id=chess_puzzle_id,
      move=move,
      expired=expired,
      answer_latency=answer_latency,
    )
    (answer_id,) = sql_op(conn, "post chess type", query).inserted_primary_key
    return answer_id

def register_chess_puzzle(conn, user_id, req_id, fen, deadline, pgn=None, move_number=None):
  query = model.chess_puzzles.insert().values(
    timestamp=datetime.datetime.now(tz=pytz.utc),
    req_id_creator=req_id,
    user_id_owner=user_id,
    fen=fen,
    deadline=deadline,
    pgn=str(pgn),
    move_number=move_number,
  )
  (chess_puzzle_id,) = sql_op(conn, "create chess puzzle", query).inserted_primary_key
  return {
    "chess_puzzle_id": chess_puzzle_id,
    "fen": fen,
    "deadline": deadline,
  }


def add_question(conn, user_id, question, low_label, high_label,
                 middle_label=None,
                 metadata=None,
                 req_id_creator=None,
                 trigger_spec=None):
  qs2.validation.check("question", question, secret=True)
  qs2.validation.check("label", low_label, secret=True)
  qs2.validation.check("label", high_label, secret=True)
  if middle_label:
    qs2.validation.check("label", middle_label, secret=True)
  if metadata:
    metadata = json.dumps(metadata)
  with conn.begin() as trans:
    trigger_id = create_trigger(conn, user_id, "question", trigger_spec)
    now = datetime.datetime.now()
    query = model.survey_questions.insert().values(
      timestamp=now,
      user_id_owner=user_id,
      question=question,
      low_label=low_label,
      high_label=high_label,
      middle_label=middle_label,
      metadata=metadata,
      trigger_id=trigger_id,
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

_implicit_trigger_columns = [
    model.triggers.c.mean_delay,
    model.triggers.c.min_delay,
    model.triggers.c.next_trigger,
    model.triggers.c.never_trigger_before,
    model.triggers.c.active,
]

@qs2.logutil.profiled("get_all_event_types")
def get_all_event_types(conn, user_id):
  columns = [model.event_types] + _implicit_trigger_columns
  query = sql.select(columns).\
    select_from(model.event_types.join(model.triggers)).\
    where(
      (model.event_types.c.user_id_owner == user_id)
    ).order_by(model.event_types.c.timestamp.asc())
  return sql_op(conn, "fetch event types", query).fetchall()

@qs2.logutil.profiled("get_all_questions")
def get_all_questions(conn, user_id):
  columns = [model.survey_questions] + _implicit_trigger_columns
  query = sql.select(columns).\
    select_from(model.survey_questions.join(model.triggers)).\
    where(
      (model.survey_questions.c.user_id_owner == user_id)
    ).order_by(model.survey_questions.c.timestamp.asc())
  return map(dict, sql_op(conn, "fetch questions", query).fetchall())

@qs2.logutil.profiled("get_pending_corrections")
def get_pending_events_corrections(conn, user_id, limit=None):
  query = sql.select([model.event_record]).where(
    (model.event_record.c.user_id_owner == user_id) &
    (model.event_record.c.status == "unreported")
  ).order_by(model.event_record.c.start.asc()).limit(limit)
  results = sql_op(conn, "fetch unreported events", query).fetchall()
  evt_id_to_names_memo = {}
  def taskify(row):
    start = hacky_force_timezone(row.start)
    end = hacky_force_timezone(row.end)
    # TODO oh no, horrible, fix to use a join (late night!)
    try:
      evt_name = evt_id_to_names_memo[row.evt_id]
    except KeyError:
      evt_name = fetch_event_type(conn, user_id, row.evt_id).name
      evt_id_to_names_memo[row.evt_id] = evt_name
    return {
      "type": "event",
      "subtype": "correct",
      "event_correct": {
        "event_type_id": row.evt_id,
        "name": evt_name,
        "start": qs2.qsjson.json_string_datetime(start),
        "end": qs2.qsjson.json_string_datetime(end),
      }
    }
  count = 0 # TODO
  earliest = None # TODO
  return [(PRIORITY_CORRECTION, row.start, taskify(row))
          for row in results], count, earliest

def make_trigger_conditions(conn, user_id, force):
  now = datetime.datetime.now()
  condition = base_condition = (
    (model.triggers.c.user_id_owner == user_id) &
    (model.triggers.c.active) &
    ((model.triggers.c.never_trigger_before == None) |
     (model.triggers.c.never_trigger_before < now))
  )
  if not force:
    condition = base_condition & (model.triggers.c.next_trigger < now)
  return condition, base_condition

def get_question_challenge(question):
  return {
    "type": "question",
    "question": qs2.qsjson.survey_question_json(dict(question)),
  }

@qs2.logutil.profiled("get_pending_append")
def get_pending_event_append(conn, user_id, event_type):
  # TODO, this is horrible, optimize query! (written very late at night)
  tail = fetch_event_report_tail(conn, user_id, event_type)
  return {
    "type": "event",
    "subtype": "append",
    "event_append": {
      "event_type_id": event_type.evt_id,
      "name": event_type.name,
      "use_duration": event_type.use_duration,
      "start": qs2.qsjson.json_string_datetime(tail),
      "end": "now",
    },
  }

@qs2.logutil.profiled("get_pending_appends")
def get_pending_events_appends(conn, user_id, force=False, limit=None):
  columns = [model.event_types] + _implicit_trigger_columns
  joined = model.triggers.join(model.event_types)
  condition, base_condition = make_trigger_conditions(conn, user_id, force=force)
  query = sql.select(columns).select_from(joined).where(condition)
  query = query.order_by(model.triggers.c.next_trigger.asc()).limit(limit)
  results = sql_op(conn, "fetch pending events", query)
  rv = []
  for row in results:
    rv.append((PRIORITY_NORMAL,
               row.next_trigger,
               get_pending_event_append(conn, user_id, row)))
  count = 0 # TODO
  earliest = None # TODO
  return rv, count, earliest

@qs2.logutil.profiled("get_pending_events")
def get_pending_events(conn, user_id, force=False, limit=None):
  crv, cc, cea = get_pending_events_corrections(conn, user_id, limit=limit)
  prv, pc, pea = get_pending_events_appends(conn, user_id, force=force, limit=limit)
  earliest = cea
  if pea is not None:
    if earliest is None or pea < earliest:
      earliest = pea
  return crv + prv, cc + pc, earliest

@qs2.logutil.profiled("get_pending_questions")
def get_pending_questions(conn, user_id, columns=[], force=False, limit=None):
  if not columns:
    columns = [model.survey_questions] + _implicit_trigger_columns
  condition, base_condition = make_trigger_conditions(conn, user_id, force=force)
  joined = model.triggers.join(model.survey_questions,
    model.triggers.c.trigger_id == model.survey_questions.c.trigger_id)
  query = sql.select(columns).where(condition).select_from(joined)
  query = query.order_by(model.triggers.c.next_trigger.asc())
  if limit:
    query = query.limit(limit)
  results = sql_op(conn, "fetch pending questions", query).fetchall()
  data = [(PRIORITY_NORMAL, row.next_trigger, get_question_challenge(row))
          for row in results]
  count_query = sql.select([sql.func.count()]).select_from(joined).where(condition)
  count = sql_op(conn, "fetch query count", count_query).scalar()
  logging.info("fetched count %d", count)
  first_trigger_query = sql.select([model.triggers.c.next_trigger]).\
    select_from(joined).\
    where(base_condition).\
    order_by(model.triggers.c.next_trigger.asc()).limit(1)
  first_trigger = sql_op(conn, "fetch next trigger", first_trigger_query).scalar()
  logging.info("fetched trigger %s", repr(first_trigger))
  return {
    "results": data,
    "count": count,
    "first_trigger": first_trigger,
  }

def peek_question(conn, user_id):
  query = question_queue_query(user_id)
  row = sql_op(conn, "fetch question", query).fetchone()
  return dict(row)

def fetch_event_type(conn, user_id, evt_id):
  columns = [qs2.model.event_types]
  query = sql.select(columns).where(
    (model.event_types.c.user_id_owner == user_id) &
    (model.event_types.c.evt_id == evt_id)
  )
  return sql_op(conn, "fetch event type by ID", query).fetchone()

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

@qs2.logutil.profiled("fetch_survey_question_answers")
def fetch_survey_question_answers(conn, user_id, question_id, t0=None, t1=None):
  condition = (
      (model.survey_answers.c.user_id_owner == user_id)
    & (model.survey_answers.c.sq_id == question_id)
  )
  if t0 is not None:
    condition = condition & (model.survey_answers.c.timestamp >= t0)
  if t1 is not None:
    # Note, exclusive. This makes it easy to request distinct batches.
    condition = condition & (model.survey_answers.c.timestamp < t1)
  query = sql.select([model.survey_answers]).where(
    condition).order_by(model.survey_answers.c.timestamp.asc())
  return sql_op(conn, "fetch question answers", query).fetchall()

def fetch_csv_export(conn, user_id, querystring, out):
  terms = qs2.csvexport.parse_csv_query(querystring)
  rawstreams = [map(lambda row: (qs2.qsjson.json_datetime(row.timestamp),
                                 row.value),
                    fetch_var(conn, user_id, term.var_type, term.var_id))
                for term in terms]
  streams = [qs2.csvexport.DataStream(stream) for stream in rawstreams]
  tabulated = qs2.csvexport.interpolate_streams(streams)
  writer = csv.writer(out)
  for row in tabulated:
    writer.writerow(row)

def fetch_var(conn, user_id, var_type, var_id):
  if var_type != "question":
    raise OperationFailed("unsupported var_type '{}'".format(var_type))
  return fetch_question_answers(conn, user_id, var_id)

def fetch_question_answers(conn, user_id, question_id):
  query = sql.select([
    model.survey_answers.c.timestamp, 
    model.survey_answers.c.value,
  ]).where(
    (model.survey_answers.c.user_id_owner == user_id) &
    (model.survey_answers.c.sq_id == question_id)
  ).order_by(model.survey_answers.c.timestamp.asc())
  rows = sql_op(conn, "fetch question answers", query).fetchall()
  return rows

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
  result = datetime.timedelta(seconds=k * mean_delay.total_seconds())
  logging.debug("randomizing %s with factor %lf: %s", mean_delay, k, result)
  return result

def fetch_trigger(conn, trigger_id):
  query = sql.select([model.triggers]).\
    where(model.triggers.c.trigger_id == trigger_id)
  return sql_op(conn, "fetch trigger", query).fetchone()

def reset_trigger(conn, trigger_id):
  id_match = model.triggers.c.trigger_id == trigger_id
  row = fetch_trigger(conn, trigger_id)
  now = datetime.datetime.now()
  if row.min_delay:
    never_trigger_before = now + randomize_next_delay(row.min_delay)
  else:
    never_trigger_before = None
  next_trigger = now + randomize_next_delay(row.mean_delay)
  query = model.triggers.update().where(id_match).values(
    next_trigger = next_trigger,
    never_trigger_before = never_trigger_before,
  )
  sql_op(conn, "update trigger for reset", query)

def fetch_question_trigger_id(conn, user_id, question_id):
  rv = fetch_question(conn, user_id, question_id,
    model.survey_questions.c.trigger_id)
  return rv["trigger_id"]

def skip_question(conn, user_id, question_id):
  now = datetime.datetime.now()
  with conn.begin() as trans:
    reset_trigger(conn, fetch_question_trigger_id(conn, user_id, question_id))

def fetch_all_question_keys(conn, user_id):
  return [("question", q["sq_id"]) for q in get_all_questions(conn, user_id)]

def fetch_all_measurement_keys(conn, user_id):
  # TODO events
  return fetch_all_question_keys(conn, user_id)

def log_request(conn, url, referer, user_agent, method, client_ip):
  now = datetime.datetime.now()
  query = model.requests.insert().values(
    timestamp=now,
    client_ip=client_ip,
    url=url,
    referer=referer,
    user_agent=user_agent,
    method=method,
  )
  (req_id,) = sql_op(conn, "log request", query).inserted_primary_key
  return req_id

def fetch_event_report_tail(conn, user_id, event_type):
  query = sql.select([qs2.model.event_record.c.end]).\
    where(
      (qs2.model.event_record.c.evt_id == event_type.evt_id) &
      (qs2.model.event_record.c.user_id_owner == user_id)
    ).order_by(qs2.model.event_record.c.end.desc()).limit(1)
  results = sql_op(conn, "fetch tail of event record", query).fetchall()
  backdating = datetime.timedelta(days=1)  # TODO: make configurable somehow
  if results:
    rv = hacky_force_timezone(results[0].end)
  else:
    rv = hacky_force_timezone(event_type.timestamp - backdating)
  return truncate_to_second_resolution(rv)

def append_to_event_record(conn, event_type, start, end, state, req_id, comment=None):
  query = qs2.model.event_record.insert().values(
    req_id_creator=req_id,
    user_id_owner=event_type.user_id_owner,
    evt_id=event_type.evt_id,
    status=state,
    start=start,
    end=end,
    comment=comment,
  )
  (evr_id,) = sql_op(conn, "append to event record", query).inserted_primary_key
  return evr_id

def try_correct_event_report(conn, user_id, event_type, start, end, state, req_id):
  # Note: this does not support _splitting_ events for now, but this could
  # be implemented in the future. Until this is implemented, events (within one
  # event type) must be reported _in order_. Their absence can be reported out of
  # order.
  t = qs2.model.event_record
  query = sql.select([t.c.evr_id, t.c.status]).\
    where(
      (t.c.user_id_owner == user_id) &
      (t.c.evt_id == event_type.evt_id) &
      (t.c.start == start) &
      (t.c.end == end)
    )
  results = sql_op(conn, "fetch event record for change", query).fetchall()
  if len(results) == 0:
    raise OperationFailed("no matching event records found")
  if len(results) > 1:
    raise OperationFailed("too many matching event records found")
  status = results[0].status
  if status != "unreported":
    raise OperationFailed("status already reported (as: '{}')".format(status))
  evr_id = results[0].evr_id
  query = t.update().where(t.c.evr_id == evr_id).values(status=state)
  sql_op(conn, "updating old event record", query)
  return { "corrected_event_record_id": evr_id }

def post_event_report(conn, user_id, event_type, start, end, state, req_id, comment=None):
  # query to see:
  #  - whether there is an interval between [last_end, start]
  #  - whether start < last_end (reject)
  logging.info("posting %s for event #%d", state, event_type.evt_id)
  if end < start:
    raise ValidationFailed("event ends before it starts")
  if state not in ("on", "off", "unknown"):
    raise ValidationFailed("invalid state: {}".format(state))
  tail = fetch_event_report_tail(conn, user_id, event_type)
  logging.info("tail for event #%d reported as: %s", event_type.evt_id, tail)
  logging.info("start was: %s", start)
  if start < tail:
    if comment is not None:
      raise ValidationFailed("did not expect comment on correction")
    logging.info("start was before tail, trying to correct")
    try:
      return try_correct_event_report(conn, user_id,
        event_type, start, end, state, req_id)
    except OperationFailed as e:
      logging.info("failed to correct, denying retroactive change")
      message = "retroactive change to event record, invalid update: " + e.message
      raise OperationFailed(message)
  rv = {}
  if tail < start:
    logging.info("tail was before start, appending extra")
    evr_id_gap = append_to_event_record(conn, event_type,
      start=tail, end=start, state="unreported", req_id=req_id)
    rv["missing_report"] = {
      "start": hacky_force_timezone(tail),
      "end": hacky_force_timezone(start),
      "event_report_id": evr_id_gap,
    }
  rv["event_report_id"] = append_to_event_record(conn, event_type,
    start=start, end=end, state=state, req_id=req_id, comment=comment)
  reset_trigger(conn, event_type.trigger_id)
  return rv

def post_answer(conn, user_id, question_id, value,
                answer_latency=None,
                req_id_creator=None):
  now = datetime.datetime.now()
  qs2.validation.check("survey_value", value)
  with conn.begin() as trans:
    reset_trigger(conn, fetch_question_trigger_id(conn, user_id, question_id))
    query = model.survey_answers.insert().values(
      timestamp=now,
      user_id_owner=user_id,
      sq_id=question_id,
      value=value,
      req_id_creator=req_id_creator,
      answer_latency=answer_latency,
    )
    (answer_id,) = sql_op(conn, "create answer", query).inserted_primary_key
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

def add_event_type(conn, user_id, name,
                   use_duration, trigger_spec, req_id_creator):
  qs2.validation.check("question", name, secret=True)
  qs2.validation.check("bool", use_duration)
  qs2.validation.check("trigger_spec", trigger_spec)
  now = datetime.datetime.now()
  with conn.begin() as trans:
    trigger_id = create_trigger(conn, user_id, "event", trigger_spec)
    query = qs2.model.event_types.insert().values(
      timestamp=now,
      req_id_creator=req_id_creator,
      user_id_owner=user_id,
      name=name,
      use_duration=use_duration,
      trigger_id=trigger_id,
    )
    (evt_id,) = sql_op(conn, "create event type", query).inserted_primary_key
    logging.info("created event #%d", evt_id)
    return evt_id

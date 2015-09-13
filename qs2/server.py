from flask import Flask, request
import flask

import functools
import decimal
import StringIO
import time

import sqlalchemy
import qs2.operations
import qs2.qsjson

import qs2.flaskutil
import qs2.logutil
import qs2.captcha

import qs2.configutil
import logging
import os
import qs2.parsing
import operator
import datetime

config = qs2.configutil.Config(os.environ["QS_CONFIG_FILE"])
qs2.logutil._config = config
qs2.logutil.setup_logging(filename=config["logging.filename"],
                          level=config.get("logging.level", "info"))
app = Flask("qs2")
engine = sqlalchemy.create_engine(config["database.url"])

def user_page(*args, **kwargs):
  return qs2.flaskutil.user_page(app, engine, *args, **kwargs)

@app.errorhandler(qs2.flaskutil.AccessDenied)
def forbidden(*args, **kwargs):
  return flask.Response(
    "Papers please.",
    401,
    {"WWW-Authenticate": "Basic realm=qs2"})

def oops(message, code=404):
  rv = flask.jsonify(status="error", message=message)
  rv.status_code = code
  return rv

@app.route("/u/", methods=["POST"])
def register_new_user():
  with engine.connect() as conn:
    with conn.begin() as trans:
      arg = request.get_json()
      if config["captcha.require_for_user_creation"] or "captcha" in arg:
        answer = arg.get("captcha")
        key = config["captcha.recaptcha_secret_key"]
        ok = qs2.captcha.verify_recaptcha(key, answer, request.remote_addr)
        if not ok:
          return flask.jsonify(status="error", reason="CAPTCHA failure")
      user_id = qs2.operations.add_user(conn, arg["username"], arg["password"])
      return flask.jsonify(status="ok", user_id=user_id)

@user_page("questions", "GET")
def get_questions(conn, user_id):
  return {
    "questions": map(qs2.qsjson.survey_question_json,
                     qs2.operations.get_all_questions(conn, user_id)),
  }

@user_page("events", "GET")
def get_events(conn, user_id):
  return {
    "events": map(qs2.qsjson.event_type_json,
                  qs2.operations.get_all_event_types(conn, user_id)),
  }

@user_page("events", "POST", write=True)
def post_new_event_type(conn, user_id, data, req_id):
  event_type_id = qs2.operations.add_event_type(conn, user_id,
    name=data["name"],
    req_id_creator=req_id,
    use_duration=data["use_duration"],
    trigger_spec=data["trigger"],
  )
  return {"event_type_id": event_type_id}

@user_page("events/<int:evt_id>/tail", "GET")
def get_event_tail(conn, user_id, evt_id):
  with conn.begin() as trans:
    event_type = qs2.operations.fetch_event_type(conn, user_id, evt_id)
    if not event_type:
      return oops("no such event")
    return {
      "tail": qs2.qsjson.json_string_datetime(
        qs2.operations.fetch_event_report_tail(conn, user_id, event_type)
      ),
    }

@user_page("events/<int:evt_id>/report", "GET")
def get_event_report(conn, user_id, evt_id):
  with conn.begin() as trans:
    event_type = qs2.operations.fetch_event_type(conn, user_id, evt_id)
    if not event_type:
      return oops("no such event")
    return {
      "report": qs2.operations.get_pending_event_append(conn, user_id, event_type),
    }

@user_page("events/<int:evt_id>/report", "POST", write=True)
def post_event_report(conn, user_id, evt_id, data, req_id):
  with conn.begin() as trans:
    evt = qs2.operations.fetch_event_type(conn, user_id, evt_id)
    if not evt:
      return oops("event not found")
    start = qs2.validation.parse_as("datetime",
      qs2.qsjson.parse_json_string_datetime, data["start"])
    end = qs2.validation.parse_as("datetime",
      qs2.qsjson.parse_json_string_datetime, data["end"])
    rv = qs2.operations.post_event_report(conn, user_id, evt,
      start=start,
      end=end,
      state=data["state"],
      req_id=req_id,
      comment=data.get("comment"),
    )
    def transform(d, k, f):
      d[k] = f(d[k])
    if "missing_report" in rv:
      transform(rv["missing_report"], "start", qs2.qsjson.json_string_datetime)
      transform(rv["missing_report"], "end", qs2.qsjson.json_string_datetime)
    return rv

@user_page("questions", "POST", write=True)
def post_new_question(conn, user_id, data, req_id):
  delay_s = qs2.validation.parse_as("duration_seconds",
    qs2.parsing.parse_duration, data.get("delay", "1h"))
  return {
    "question_id": qs2.operations.add_question(conn, user_id,
      req_id_creator=req_id,
      question=data["question"],
      low_label=data["low"],
      middle_label=data.get("middle"),
      high_label=data["high"],
      metadata=data.get("metadata"),
      trigger_spec={
        "delay_s": delay_s,
      },
    )
  }

@user_page("export/csv/<query>", "GET")
def export_csv(conn, user_id, query):
  stream = StringIO.StringIO()
  qs2.operations.fetch_csv_export(conn, user_id, query, stream)
  csv_data = stream.getvalue()
  csv_filename = "export-{}.csv".format(int(time.time()))
  return flask.Response(csv_data, 200, mimetype="text/plain")

@user_page("questions/<int:sq_id>", "GET")
def get_question(conn, user_id, sq_id):
  q = qs2.operations.fetch_question(conn, user_id, sq_id)
  if not q:
    return oops("no such question")
  return {"question": qs2.qsjson.survey_question_json(q)}

@user_page("questions/<int:sq_id>/skip", "POST", write=True)
def skip_question(conn, user_id, sq_id, data, req_id):
  qs2.operations.skip_question(conn, user_id, sq_id)
  return {"question_skipped": sq_id}

@user_page("questions/<int:sq_id>/answer", "POST", write=True)
def post_answer(conn, user_id, sq_id, data, req_id):
  q = qs2.operations.fetch_question(conn, user_id, sq_id)
  if not q:
    return oops("question not found")
  v = qs2.validation.parse_as("survey_value",
    lambda n: decimal.Decimal(str(n)), data["value"])
  latency = None
  if "latency_ms" in data:
    latency = datetime.timedelta(milliseconds=int(data["latency_ms"]))
  return {
    "answer_id": qs2.operations.post_answer(conn,
      req_id_creator=req_id,
      user_id=user_id,
      question_id=sq_id,
      value=v,
      answer_latency=latency,
    )
  }

@user_page("pending", "GET")
def get_pending(conn, user_id):
  force = request.args.get("force", type=qs2.flaskutil.parse_bool)
  limit = request.args.get("limit", type=int)
  filter_types = request.args.get("types", type=qs2.flaskutil.set_parser())
  def accept(t):
    return filter_types is None or t in filter_types
  rv = {
    "pending": [],
    "queue_size": 0,
  }
  def update(items, count, earliest):
    rv["pending"].extend(items)
    rv["queue_size"] += count
    if earliest is not None:
      if "first_trigger" not in rv or rv["first_trigger"] < earliest:
        rv["first_trigger"] = earliest
  if accept("question"):
    qres = qs2.operations.get_pending_questions(
      conn, user_id, force=force, limit=limit)
    update(qres["results"], qres["count"], qres["first_trigger"])
  if accept("event"):
    items, n, earliest = qs2.operations.get_pending_events(
      conn, user_id, force=force, limit=limit)
    update(items, n, earliest)
  rv["pending"].sort()
  if limit:
    rv["pending"] = rv["pending"][:limit]
  rv["pending"] = [v for (k,v) in rv["pending"]]
  if "first_trigger" in rv:
    rv["first_trigger"] = qs2.qsjson.json_datetime(rv["first_trigger"])
  return rv

if __name__ == '__main__':
  app.run(debug=True)


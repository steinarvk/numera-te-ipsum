from flask import Flask, request
import flask

import functools
import decimal

import sqlalchemy
import qs2.operations
import qs2.qsjson

import qs2.flaskutil
import qs2.logutil

import qs2.configutil
import logging
import os
import qs2.parsing
import operator
import datetime

config = qs2.configutil.Config(os.environ["QS_CONFIG_FILE"])
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
      user_id = qs2.operations.add_user(conn, arg["username"], arg["password"])
      return flask.jsonify(status="ok", user_id=user_id)

@user_page("questions", "GET")
def get_questions(conn, user_id):
  return {
    "questions": map(qs2.qsjson.survey_question_json,
                     qs2.operations.get_all_questions(conn, user_id)),
  }

@user_page("questions", "POST", write=True)
def post_new_question(conn, user_id, data, req_id):
  delay_s = qs2.validation.parse_as("duration_seconds",
    qs2.parsing.parse_duration, data.get("delay", "1h"))
  return {
    "question_id": qs2.operations.add_question(conn, user_id,
      req_id_creator=req_id,
      question=data["question"],
      low_label=data["low"],
      high_label=data["high"],
      delay_s=delay_s,
    )
  }

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

@user_page("questions/pending", "GET")
def get_pending(conn, user_id):
  force = request.args.get("force", type=qs2.flaskutil.parse_bool)
  limit = request.args.get("limit", type=int)
  filter_types = request.args.get("types", type=qs2.flaskutil.set_parser())
  def accept(t):
    return filter_types is None or t in filter_types
  results = qs2.operations.get_pending_questions(
    conn, user_id, force=force, limit=limit)
  questions = results["results"]
  pending = []
  if accept("question"):
    pending.extend(map(qs2.qsjson.survey_question_json, questions))
  pending.sort(key=operator.itemgetter("trigger"))
  if limit:
    pending = pending[:limit]
  rv = {
    "pending": pending,
    "queue_size": results["count"],
  }
  if results.get("first_trigger"):
    rv["first_trigger"] = qs2.qsjson.json_datetime(results["first_trigger"])
  return rv

if __name__ == '__main__':
  app.run(debug=True)


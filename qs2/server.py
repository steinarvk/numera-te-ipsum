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
  return {
    "question_id": qs2.operations.add_question(conn, user_id,
      req_id_creator=req_id,
      question=data["question"],
      low_label=data["low"],
      high_label=data["high"],
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
  return {
    "answer_id": qs2.operations.post_answer(conn,
      req_id_creator=req_id,
      user_id=user_id,
      question_id=sq_id,
      value=v,
    )
  }

@user_page("questions/pending", "GET")
def get_pending(conn, user_id):
  return {
    "pending": map(qs2.qsjson.survey_question_json,
                   qs2.operations.get_pending_questions(conn, user_id))
  }

if __name__ == '__main__':
  app.run(debug=True)


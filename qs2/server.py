from flask import Flask, request
import flask

import functools
import decimal

import sqlalchemy
import qs2.operations
import qs2.qsjson

import qs2.flaskutil

app = Flask("qs2")
engine = sqlalchemy.create_engine("postgresql:///quantifiedself")

def user_page(url, method):
  return qs2.flaskutil.user_page(app, engine, url, method)

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
  conn = engine.connect()
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

@user_page("questions", "POST")
def post_new_question(conn, user_id, data):
  return {
    "question_id": qs2.operations.add_question(conn, user_id,
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

@user_page("questions/<int:sq_id>/skip", "POST")
def skip_answer(conn, user_id, sq_id, data):
  skip_question(conn, user_id, sq_id)
  return {"question_skipped": sq_id}

@user_page("questions/<int:sq_id>/answer", "POST")
def post_answer(conn, user_id, sq_id, data):
  q = qs2.operations.fetch_question(conn, user_id, sq_id)
  if not q:
    return oops("question not found")
  v = qs2.validation.parse_as("survey_value",
    lambda n: decimal.Decimal(str(n)), data["value"])
  return {
    "answer_id": qs2.operations.post_answer(conn,
      user_id=user_id,
      question_id=question_id,
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

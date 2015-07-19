from flask import Flask, request
import flask

import functools
import decimal

import sqlalchemy
import qs2.operations
import qs2.qsjson

app = Flask("qs2")
engine = sqlalchemy.create_engine("postgresql:///quantifiedself")

def secure(f):
  @functools.wraps(f)
  def wrapper(*args, **kwargs):
    with engine.begin() as conn:
      auth = request.authorization
      if auth:
        user_id = qs2.operations.authenticate_user(conn,
                                                   auth.username,
                                                   auth.password)
        if user_id:
          return f(login_id=user_id, *args, **kwargs)
      return forbidden()
  return wrapper

class AccessDenied(Exception):
  pass

@app.errorhandler(AccessDenied)
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

def check_user(conn, login_id, username):
  try:
    user_id = qs2.operations.get_user_id(conn, username)
  except Exception as e:
    raise AccessDenied()
  if user_id != login_id:
    raise AccessDenied()

@app.route("/u/<username>/questions", methods=["GET"])
@secure
def get_questions(login_id, username):
  conn = engine.connect()
  with conn.begin() as trans:
    check_user(conn, login_id, username)
    qs = qs2.operations.get_all_questions(conn, login_id)
    qjsons = map(qs2.qsjson.survey_question_json, qs)
    return flask.jsonify(questions=qjsons)
    
@app.route("/u/<username>/questions", methods=["POST"])
@secure
def post_new_question(login_id, username):
  conn = engine.connect()
  with conn.begin() as trans:
    check_user(conn, login_id, username)
    arg = request.get_json()
    question_id = qs2.operations.add_question(conn,
      user_id=login_id,
      question=arg["question"],
      low_label=arg["low"],
      high_label=arg["high"])
    return flask.jsonify(status="ok", question_id=question_id)

@app.route("/u/<username>/questions/<int:sq_id>", methods=["GET"])
@secure
def get_question(login_id, username, sq_id):
  conn = engine.connect()
  with conn.begin() as trans:
    try:
      user_id = qs2.operations.get_user_id(conn, username)
    except Exception as e:
      return forbidden()
    if user_id != login_id:
      return forbidden()
    q = qs2.operations.fetch_question(conn, login_id, sq_id)
    if not q:
      return oops("no such question")
    qjson = qs2.qsjson.survey_question_json(q)
    return flask.jsonify(question=qjson)

@app.route("/u/<username>/questions/<int:sq_id>/answer", methods=["POST"])
@secure
def post_answer(login_id, username, sq_id):
  conn = engine.connect()
  with conn.begin() as trans:
    check_user(conn, login_id, username)
    arg = request.get_json()
    q = qs2.operations.fetch_question(conn, login_id, sq_id)
    if not q:
      return oops("not found")
    v = qs2.validation.parse_as("survey_value",
      lambda n : decimal.Decimal(str(n)), arg["value"])
    answer_id = qs2.operations.post_answer(conn,
      user_id=login_id,
      question_id=sq_id,
      value=v,
    )
    return flask.jsonify(status="ok", answer_id=answer_id)

@app.route("/u/<username>/questions/pending", methods=["GET"])
@secure
def get_queue(login_id, username):
  conn = engine.connect()
  with conn.begin() as trans:
    try:
      user_id = qs2.operations.get_user_id(conn, username)
    except Exception as e:
      return forbidden()
    if user_id != login_id:
      return forbidden()
    qs = qs2.operations.get_pending_questions(conn, login_id)
    qjsons = map(qs2.qsjson.survey_question_json, qs)
    return flask.jsonify(questions=qjsons)

if __name__ == '__main__':
  app.run(debug=True)


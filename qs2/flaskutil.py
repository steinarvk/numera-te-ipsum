from flask import Flask, request
import flask
import functools
import logging

import qs2.operations
import qs2.error

class AccessDenied(Exception):
  pass

def auth_user(conn):
  auth = request.authorization
  if not auth:
    raise AccessDenied()
  return qs2.operations.authenticate_user(conn,
                                          auth.username,
                                          auth.password)

def check_user(conn, login_id, username):
  try:
    user_id = qs2.operations.get_user_id(conn, username)
  except Exception as e:
    logging.exception(e)
    raise AccessDenied()
  if user_id != login_id:
    logging.info("user IDs do not match: %d != %d", user_id, login_id)
    raise AccessDenied()

def user_page(app, engine, url, method, write=False):
  def wrap(f):
    @app.route("/u/<username>/" + url, methods=[method])
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
      username = kwargs["username"]
      with engine.connect() as conn:
        login_id = auth_user(conn)
        with conn.begin() as trans:
          params = {
            "url": request.url,
            "referer": request.headers.get("Referer"),
            "user_agent": request.headers.get("User-Agent"),
            "method": request.method,
            "client_ip": request.environ.get("REMOTE_ADDR"),
          }
          req_id = qs2.operations.log_request(conn, **params)
        with conn.begin() as trans:
          check_user(conn, login_id, username)
          del kwargs["username"]
          try:
            kwargs["user_id"] = qs2.operations.get_user_id(conn, username)
          except Exception as e:
            logging.error("request %d failed:", req_id)
            logging.exception(e)
            return forbidden()
          if method == "POST":
            kwargs["data"] = request.get_json()
          if write:
            kwargs["req_id"] = req_id
          try:
            rv = f(conn=conn, *args, **kwargs)
          except (qs2.error.ValidationFailed, qs2.error.OperationFailed) as e:
            return flask.jsonify(
              status="error",
              reason=e.message,
            )
          if isinstance(rv, dict):
            if "status" not in rv:
              rv["status"] = "ok"
            return flask.jsonify(**rv)
          return rv
  return wrap

def parse_bool(s):
  if s.lower() in ("false", "no", "0", "f"):
    return False
  if s.lower() in ("true", "yes", "1", "t"):
    return True
  raise ValueError("invalid bool value '{}'".format(s))

def list_parser(subparser=str):
  def f(s):
    return [subparser(x) for x in s.split(",")]
  return f

def set_parser(subparser=str):
  f = list_parser(subparser)
  def g(s):
    return set(f(s))
  return g

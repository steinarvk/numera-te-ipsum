from flask import Flask, request
import flask
import functools

import qs2.operations

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
    raise AccessDenied()
  if user_id != login_id:
    raise AccessDenied()

def user_page(app, engine, url, method):
  def wrap(f):
    @app.route("/u/<username>/" + url, methods=[method])
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
      username = kwargs["username"]
      conn = engine.connect()
      login_id = auth_user(conn) 
      with conn.begin() as trans:
        check_user(conn, login_id, username)
        del kwargs["username"]
        try:
          kwargs["user_id"] = qs2.operations.get_user_id(conn, username)
        except Exception as e:
          return forbidden()
        if method == "POST":
          kwargs["data"] = request.get_json()
        rv = f(conn=conn, *args, **kwargs)
        if isinstance(rv, dict):
          if "status" not in rv:
            rv["status"] = "ok"
          return flask.jsonify(**rv)
        return rv
  return wrap


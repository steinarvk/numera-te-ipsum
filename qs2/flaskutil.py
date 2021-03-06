from flask import Flask, request
import flask
import functools
import logging
import time

import qs2.operations
import qs2.error
import qs2.logutil

from prometheus_client import (Counter, Histogram)

metric_user_pages_requested = Counter(
    "qs_user_pages_requested",
    "User pages begun processing by page",
    ["page"])
metric_user_pages_finished = Counter(
    "qs_user_pages_finished",
    "User pages served by page",
    ["page", "status"])
metric_user_pages_latency = Histogram(
    "qs_user_pages_latency",
    "User page latency by page and status",
    ["page", "status"])

class AccessDenied(Exception):
  pass

@qs2.logutil.profiled("auth_user")
def auth_user(conn):
  auth = request.authorization
  if not auth:
    raise AccessDenied()
  return qs2.operations.authenticate_user(conn,
                                          auth.username,
                                          auth.password)

@qs2.logutil.profiled("check_user")
def check_user(conn, login_id, username):
  try:
    user_id = qs2.operations.get_user_id(conn, username)
  except Exception as e:
    logging.exception(e)
    raise AccessDenied()
  if user_id != login_id:
    logging.info("user IDs do not match: %d != %d", user_id, login_id)
    raise AccessDenied()

def record_metrics_for_request(page):
  def decorator(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      metric_user_pages_requested.labels(page).inc()
      t0 = time.time()
      rv = function(*args, **kwargs)
      t1 = time.time()
      dur = t1 - t0
      try:
          status = str(rv.status_code)
      except Exception as e:
          logging.exception(e)
          status = "unknown"
      metric_user_pages_finished.labels(page, status).inc()
      metric_user_pages_latency.labels(page, status).observe(dur)
      logging.info("served %s with status %s after %f", page, status, dur)
      return rv
    return wrapper
  return decorator

def user_page(app, engine, url, method, write=False):
  def wrap(f):
    @app.route("/u/<username>/" + url, methods=[method])
    @qs2.logutil.profiled(method + ":/u/<username>/" + url)
    @record_metrics_for_request(url)
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
      username = kwargs["username"]
      t0 = time.time()
      def report_stage(status):
        t = time.time()
        logging.info("serving %s %s to user %s: %s (after %f)", method, url, username, status, (t-t0))
      report_stage("connecting")
      with engine.connect() as conn:
        report_stage("authenticating")
        login_id = auth_user(conn)
        report_stage("logging")
        with conn.begin() as trans:
          params = {
            "url": request.url,
            "referer": request.headers.get("Referer"),
            "user_agent": request.headers.get("User-Agent"),
            "method": request.method,
            "client_ip": request.environ.get("REMOTE_ADDR"),
          }
          req_id = qs2.operations.log_request(conn, **params)
        report_stage("transacting")
        with conn.begin() as trans:
          check_user(conn, login_id, username)
          del kwargs["username"]
          try:
            report_stage("getting user_id")
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
            report_stage("performing operation core")
            rv = f(conn=conn, *args, **kwargs)
            report_stage("performed operation core")
          except (qs2.error.ValidationFailed, qs2.error.OperationFailed) as e:
            response = flask.jsonify(
              status="error",
              reason=e.message,
            )
            response.status_code = 500
            return response
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

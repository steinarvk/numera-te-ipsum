import logging
import contextlib
import time
import threading
import functools
import json

_thread_context = threading.local()
_config = None

def setup_logging(level, filename=None):
  level_code = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
  }[level]
  kwargs = {
    "format": "[%(asctime)s] %(message)s",
    "level": level_code,
    "datefmt": "%Y-%m-%d %H:%M:%S",
  }
  if filename:
    kwargs["filename"] = filename
  logging.basicConfig(**kwargs)
  logging.info("began logging")

@contextlib.contextmanager
def section(name):
  if not _config["profiling.enable"]:
    yield
    return
  tid = threading.current_thread().name
  _thread_context.stack = getattr(_thread_context, "stack", [])
  depth = len(_thread_context.stack)
  indent = ". " * depth
  t0 = time.time()
  ctx = {
    "name": name,
    "t0": t0,
    "t1": None,
    "duration": None,
    "unaccounted": None,
    "depth": depth,
    "children": [],
  }
  if _thread_context.stack:
    _thread_context.stack[-1]["children"].append(ctx)
  _thread_context.stack.append(ctx)
  logging.info("[profile-stack %s] %s-> %s at %lf", tid, indent, name, t0)
  try:
    yield
  finally:
    _thread_context.stack.pop()
    t1 = ctx["t1"] = time.time()
    dt = ctx["duration"] = t1 - t0
    ctx["unaccounted"] = dt - sum(c["duration"] for c in ctx["children"])
    dt = t1 - t0
    logging.info("[profile-stack %s] %s<- %s at %lf after %lf",
      tid, indent, name, t1, dt)
    if depth == 0:
      logging.info("[profile-json] %s", json.dumps(ctx))

def profiled(name):
  def decorator(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      with section(name):
        return function(*args, **kwargs)
    return wrapper
  return decorator

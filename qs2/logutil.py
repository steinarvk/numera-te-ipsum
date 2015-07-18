import logging
import contextlib
import time

def setup_logging(log_level_name):
  log_fmt = "[%(asctime)s] %(message)s"
  datefmt = "%Y-%m-%d %H:%M:%S"
  level = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
  }[log_level_name]
  logging.basicConfig(format=log_fmt, level=level, datefmt=datefmt)

@contextlib.contextmanager
def section(name):
  t0 = time.time()
  logging.info("%s", name)
  try:
    yield
  finally:
    t1 = time.time()
    logging.debug("<- %s (%.3lfs)", name, t1 - t0)

@contextlib.contextmanager
def lowlevel_section(name):
  t0 = time.time()
  logging.debug("%s", name)
  try:
    yield
  finally:
    t1 = time.time()
    logging.debug("<- %s (%.3lfs)", name, t1 - t0)

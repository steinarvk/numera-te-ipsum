import logging
import contextlib
import time

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

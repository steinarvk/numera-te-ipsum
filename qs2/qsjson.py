import time
import pytz
import dateutil.parser
import tzlocal
import logging
import re

def parse_json_string_datetime(s):
  # dateutil is nice, but a little too forgiving.
  # detect if we weren't even given a year..
  parsed = dateutil.parser.parse(s)
  if not parsed.tzinfo:
    message = "expected a time specifier with a time zone, got '{}'".format(s)
    raise ValueError(message)
  return parsed.astimezone(pytz.utc)

def json_string_datetime(dt_with_tz):
  dt_utc = dt_with_tz.astimezone(pytz.utc)
  return dt_utc.isoformat()

def json_datetime(dt_localtime): # deprecated, to be retired
  assert not dt_localtime.tzinfo
  return time.mktime(dt_localtime.timetuple())

def json_duration(td):
  return td.total_seconds()

def survey_question_json(q):
  return {
    "id": q["sq_id"],
    "text": q["question"],
    "labels": {
      "low": q["low_label"],
      "middle": q["middle_label"],
      "high": q["high_label"],
    },
    "trigger": json_datetime(q["next_trigger"]),
    "timestamp": json_datetime(q["timestamp"]),
    "interval": json_duration(q["mean_delay"]),
  }

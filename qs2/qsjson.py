import time
import pytz
import dateutil.parser
import calendar
import tzlocal
import logging
import re

import qs2.timeutil

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

def json_datetime(dt): # deprecated, to be retired
  dt_utc = qs2.timeutil.hacky_force_timezone(dt)
  return calendar.timegm(dt_utc.timetuple())

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
    "active": q["active"],
  }

def event_type_json(ev):
  # TODO fix the inconsistency here, with dict/obj
  return {
    "id": ev.evt_id,
    "name": ev.name,
    "use_duration": ev.use_duration,
    "trigger": json_datetime(ev.next_trigger),
    "timestamp": json_datetime(ev.timestamp),
    "interval": json_duration(ev.mean_delay),
    "active": ev.active,
  }


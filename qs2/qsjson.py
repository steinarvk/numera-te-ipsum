import time
import pytz
import dateutil.parser
import calendar
import tzlocal
import logging
import re
import slugify

import qs2.timeutil

STOP_WORDS = set("""
  the be to of and a an in that have i it for
  on with he she as you your do at this but his
  her by from they their we our say said or will
  my mine one all would there what so up out if
  about who get which go me when make can like
  time just him know take into year some could
  them than then now right look come only its
  it's over think also back after use two how why
  where when work first well way even new want
  because any these give day today most us

  much are feeling moment

  during last waking hours often felt few
""".split())

def question_slugify(q):
  if ":" in q:
    _, q = q.split(":", 1)
  words = slugify.slugify(q.lower()).split("-")
  words = [w for w in words if w not in STOP_WORDS]
  return "sq-" + slugify.slugify(" ".join(words))

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
  rv = {
    "id": q["sq_id"],
    "text": q["question"],
    "_slug": question_slugify(q["question"]),
    "labels": {
      "low": q["low_label"],
      "middle": q["middle_label"],
      "high": q["high_label"],
    },
    "timestamp": json_datetime(q["timestamp"]),
  }
  if "next_trigger" in q:
    rv["trigger"] = json_datetime(q["next_trigger"])
  if "mean_delay" in q:
    rv["interval"] = json_duration(q["mean_delay"])
  if "active" in q:
    rv["active"] = q["active"],
  return rv

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


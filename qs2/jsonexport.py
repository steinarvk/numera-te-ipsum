import datetime

import qs2.operations
import qs2.qsjson

from qs2.error import OperationFailed

def parse_query(query):
  rv = []
  for var in query.split(","):
    kind, id_ = var.split("/")
    id_ = int(id_)
    rv.append((kind.strip(), id_))
  return rv

def format_optional_datetime(dt):
  if dt is not None:
    return qs2.qsjson.json_string_datetime(dt)

def format_value(t, **kwargs):
  return {
    "time": qs2.qsjson.json_string_datetime(t),
    "value": kwargs,
  }

def typedesc_survey_question(q):
  return {
    "survey": {
      "question": q["question"],
      "low_label": q["low_label"],
      "high_label": q["high_label"],
      "middle_label": q["middle_label"],
    },
    "types": {
      "answer": {
        "type": "float",
        "unit": "unit-interval-rating",
      },
      "latency": {
        "type": "integer",
        "unit": "milliseconds",
      },
    },
  }

def export_survey_question(conn, user_id, question_id, t0, t1):
  q = qs2.operations.fetch_question(conn, user_id, question_id)
  if not q:
    raise OperationFailed("no such question: {}".format(question_id))
  rows = qs2.operations.fetch_survey_question_answers(
    conn, user_id, question_id, t0, t1)
  typedesc = typedesc_survey_question(q)
  def fmt(row):
    rv = {"answer": float(row.value)}
    if row.answer_latency:
      rv["latency"] = int(round(row.answer_latency.total_seconds() * 1000))
    return format_value(row.timestamp, **rv)
  return typedesc, [fmt(row) for row in rows]

def export_event(conn, user_id, evt_id, t0, t1):
  raise OperationFailed("TODO: export event not supported yet")
  
def export(conn, user_id, key, t0, t1):
  rv = {}
  type_, id_ = key
  rv["query"] = {
    "start": format_optional_datetime(t0),
    "end": format_optional_datetime(t1),
  }
  rv["key"] = {
    "type": type_,
    "id": id_,
  }
  try:
    exporter = {
      "question": export_survey_question,
      "event": export_event,
    }[type_]
  except KeyError:
    raise OperationFailed("no exporter for '{}'".format(type_))
  rv["value_type"], rv["values"] = exporter(conn, user_id, id_, t0, t1)
  return rv

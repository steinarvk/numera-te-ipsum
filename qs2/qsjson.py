import time

def json_datetime(dt):
  return time.mktime(dt.timetuple())

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

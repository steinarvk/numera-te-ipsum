import pytz
import dateutil.parser
import datetime
import tzlocal

def hacky_force_timezone(dt_naive_assumed_local):
  if dt_naive_assumed_local.tzinfo:
    return dt_naive_assumed_local.astimezone(pytz.utc)
  dt_local = tzlocal.get_localzone().localize(dt_naive_assumed_local)
  return dt_local.astimezone(pytz.utc)

def truncate_to_second_resolution(dt):
  return datetime.datetime(
    year=dt.year,
    month=dt.month,
    day=dt.day,
    hour=dt.hour,
    minute=dt.minute,
    second=dt.second,
    microsecond=0,
    tzinfo=dt.tzinfo,
  )

import pytz
import dateutil.parser
import tzlocal

def hacky_force_timezone(dt_naive_assumed_local):
  if dt_naive_assumed_local.tzinfo:
    return dt_naive_assumed_local.astimezone(pytz.utc)
  dt_local = tzlocal.get_localzone().localize(dt_naive_assumed_local)
  return dt_local.astimezone(pytz.utc)


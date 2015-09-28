import logging
import sqlalchemy
import datetime
import random

import qs2.logutil

from qs2 import model

from qs2.error import OperationFailed, ValidationFailed

def sql_op(conn, name, query):
  with qs2.logutil.section("SQL operation ({})".format(name)):
    logging.debug("Executing SQL query: %s", str(query))
    try:
      result = conn.execute(query)
    except sqlalchemy.exc.SQLAlchemyError as e:
      logging.exception(e)
      raise OperationFailed("SQL operation failed: {}".format(name))
    return result

def create_trigger(conn, user_id, trigger_type, spec):
  spec = spec or {}
  active = spec.get("active", True)
  mean_delay = datetime.timedelta(seconds=spec.get("delay_s", 3600))
  min_delay = datetime.timedelta(seconds=spec.get("min_delay_s", 300))
  now = datetime.datetime.now()
  # There's a good reason to have this be uniform rather than
  # using normal delays -- this way we get a good spread of
  # when the questions are first asked. (Consider very long
  # delays for questions to be asked infrequently, e.g.
  # once every year.)
  until_first_trigger = datetime.timedelta(
    seconds=random.random()*mean_delay.total_seconds())
  next_trigger = now + until_first_trigger
  query = model.triggers.insert().values(
    type=trigger_type,
    user_id_owner=user_id,
    active=active,
    min_delay=min_delay,
    mean_delay=mean_delay,
    never_trigger_before=now,
    next_trigger=next_trigger,
  )
  (trigger_id,) = sql_op(conn, "create new trigger", query).inserted_primary_key
  return trigger_id

def create_item(conn, user_id, key, item_type, trigger_spec):
  trigger_id = create_trigger(conn, user_id, "item", spec=trigger_spec)
  query = model.triggers.insert().values(
    item_key=key,
    type=item_type,
    user_id_owner=user_id,
    trigger_id=trigger_id,
  )
  (item_id,) = sql_op(conn, "create item", query).inserted_primary_key
  return item_id

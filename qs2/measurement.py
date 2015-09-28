from qs2 import model

import qs2.logutil

from sqlalchemy import sql

from qs2.error import OperationFailed, ValidationFailed
from qs2.dbutil import sql_op
from qs2.dbutil import create_item

@qs2.logutil.profiled("create_measured_var")
def create_measured_var(conn, user_id, req_id, key, name, units, trigger_spec):
  with conn.begin() as trans:
    item_type = "measured_variable"
    item_id = create_item(conn, user_id, key, item_type, trigger_spec)
    query = model.measured_vars.insert().values(
      item_id=item_id,
      name=name,
    )
    (measured_var_id,) = sql_op(conn, "create measured var", query).inserted_primary_key
    units = [(int(unit.get("priority", 0)), unit) for unit in units]
    units.sort()
    for i, (_, unit) in enumerate(units):
      priority = i * 10
      precision = int(unit.get("precision", 0))
      query = model.measured_var_units.insert().values(
        measured_var_id=measured_var_id,
        priority=priority,
        unit_key=unit["key"],
        singular=unit["singular"],
        plural=unit["plural"],
        precision=precision,
      )
      sql_op(conn, "create measured var ID", query)
    return measured_var_id

@qs2.logutil.profiled("check_owned_measured_var")
def check_owned_measured_var(conn, user_id, meas_id):
  """Check the existence of a measured variable owned by a specific user (else return False)."""
  query = sql.select([model.measured_vars.c.measured_var_id]).select_from(
    model.measured_vars.join(model.items),
  ).where(
    (model.measured_vars.c.measured_var_id == meas_id) &
    (model.items.c.user_id_owner == user_id)
  ).limit(1)
  rows = sql_op(conn, "check measured var", query).fetchall()
  return len(rows) == 1

@qs2.logutil.profiled("fetch_unit_id_by_key")
def fetch_unit_id_by_key(conn, meas_id, unit_key):
  """Fetch the ID of a particular unit by its key."""
  query = sql.select([model.measured_var_units.c.measured_var_unit_id]).where(
    (model.measured_var_units.c.unit_key == unit_key) &
    (model.measured_var_units.c.measured_var_id == meas_id)
  )
  (unit_id,) = sql_op(conn, "get unit by key", query).fetchone()
  return unit_id

@qs2.logutil.profiled("add_measurement")
def add_measurement(conn, req_id,
                    measured_var_id, timestamp, unit_id, value, comment):
  """Add a measurement (one datapoint) to the database."""
  query = model.measurements.insert().values(
    measured_var_id=measured_var_id,
    req_id_creator=req_id,
    timestamp=timestamp,
    value=value,
    unit_id=unit_id,
    comment=comment,
  )
  (measurement_id,) = sql_op(conn, "insert measurement", query).inserted_primary_key
  return measurement_id

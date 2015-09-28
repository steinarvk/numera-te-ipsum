from qs2 import model

import qs2.logutil

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

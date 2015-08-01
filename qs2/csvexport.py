class Term(object):
  def __init__(self, var_type, var_id, options):
    self.var_type = var_type
    self.var_id = var_id
    self.options = options

class DataStream(object):
  def __init__(self, stream, horizon=None):
    self.horizon = horizon
    self.stream = iter(stream)
    self.t0, self.v0 = self.next_value()
    self.t1, self.v1 = self.next_value()
    self.tm = self.tv = None

  @property
  def finished(self):
    return self.t0 is None

  def pop(self):
    rv = self.tm, self.vm = self.t0, self.v0
    self.t0, self.v0 = self.t1, self.v1
    self.t1, self.v1 = self.next_value()
    return rv

  def interpolating(self):
    if None in (self.t0,self.tm):
      return False
    if self.horizon is None:
      return True
    return (self.t0 - self.tm) < self.horizon

  def at(self, t):
    if not self.interpolating():
      return None
    if t < self.tm:
      return None
    assert self.tm <= t <= self.t0
    p = (t - self.tm) / (self.t0 - self.tm)
    v = p * float(self.v0 - self.vm) + float(self.vm)
    return v

  def next_value(self):
    try:
      return next(self.stream)
    except StopIteration:
      return None, None

def parse_csv_term(termstring):
  words = termstring.split(":")
  var_type, var_id_string = words[0].split("=")
  var_id = int(var_id_string)
  options = {}
  for option in words[1:]:
    if "=" in option:
      key, value = option.split("=")
    else:
      key = option
      value = True
    options[key] = value
  return Term(var_type, var_id, options)

def parse_csv_query(querystring):
  return [parse_csv_term(x) for x in querystring.split(",")]

def argmin(f, xs):
  champion = None
  for x in xs:
    score = f(x)
    if champion is None or score < champion_score:
      champion = x
      champion_score = score
  return champion

def interpolate_streams(streams):
  while True:
    active_streams = [(i, stream) for (i,stream) in enumerate(streams)
                      if not stream.finished]
    if not active_streams:
      break
    chosen_index, chosen = min(active_streams, key=lambda (i,s): s.t0)
    t, v = chosen.pop()
    values = [(v if i == chosen_index else stream.at(t))
              for (i,stream) in enumerate(streams)]
    yield [t] + values
  

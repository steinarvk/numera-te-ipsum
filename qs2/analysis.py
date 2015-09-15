import qs2.qsjson
import sys
import bisect
import datetime
import json
import pytz

Epoch = datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)

def epoch_seconds(t):
  return (t - Epoch).total_seconds()

def epoch_nanoseconds(t):
  return int(epoch_seconds(t) * 1000000000)

def lerp(t, t0, v0, t1, v1):
  u = (t - t0) / float(t1 - t0)
  return u * v1 + (1 - u) * v0

class MemoryStream(object):
  def __init__(self, data, func=None, key=None):
    self.data = data
    if key is not None:
      assert not func
      self.func = lambda e: e[key]
    elif func is not None:
      assert not key
      self.func = func
    else:
      assert False
    self.t0 = self[0]
    self.t1 = self[-1]

  def eval_at(self, t):
    i = bisect.bisect_right(self, t)
    assert i
    i -= 1
    assert self[i] <= t <= self[i+1]
    return lerp(epoch_seconds(t),
      epoch_seconds(self[i]), self.value(i),
      epoch_seconds(self[i+1]), self.value(i+1))

  def __iter__(self):
    for i in range(len(self)):
      yield self[i]

  def __len__(self):
    return len(self.data["values"])

  def value(self, i):
    e = self.data["values"][i]
    return self.func(e["value"])
    
  def __getitem__(self, i):
    e = self.data["values"][i]
    return qs2.qsjson.parse_json_string_datetime(e["time"])

def load_answer_streams(data):
  return [MemoryStream(x, key="answer") for x in data["exported"]]

def common_bounds(streams):
  t0 = max(x.t0 for x in streams)
  t1 = min(x.t1 for x in streams)
  return t0, t1

def accumulate_value_streams(streams, function, resolution):
  t, t1 = common_bounds(streams)
  while t <= t1:
    yield t, function([x.eval_at(t) for x in streams])
    t += resolution

def write_influxdb(f, name, seq):
  for t, v in seq:
    print >>f, name, "value={}".format(v), epoch_nanoseconds(t) 

if __name__ == '__main__':
  filename = sys.argv[1]
  measurement_name = sys.argv[2]
  with open(filename, "r") as f:
    data = json.load(f)
  streams = load_answer_streams(data)
  res = datetime.timedelta(minutes=5)
  seq = accumulate_value_streams(streams, sum, res)
  write_influxdb(sys.stdout, measurement_name, seq)

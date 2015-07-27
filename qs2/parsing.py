import re

DurationRegex = re.compile("([0-9]+)([dhms])")
DurationSeconds = {
  "s": 1,
  "m": 60,
  "h": 60 * 60,
  "d": 60 * 60 * 24,
}

def parse_duration(s):
  m = DurationRegex.match(s)
  if not m:
    raise ValueError("not a valid duration: '{}'".format(s))
  return int(m.group(1)) * DurationSeconds[m.group(2)]


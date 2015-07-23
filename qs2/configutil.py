import yaml

class Config(object):
  def __init__(self, filename):
    self.load_file(filename)
  
  def load_file(self, filename):
    with open(filename, "r") as f:
      self.root = yaml.safe_load(f)

  def __getitem__(self, key):
    subkeys = key.split(".")
    data = self.root
    for subkey in subkeys:
      try:
        data = data[subkey]
      except (KeyError, TypeError) as e:
        raise KeyError("no such key: {} (in {})".format(subkey, key))
    return data

  def get(self, key, default=None):
    try:
      return self[key]
    except KeyError:
      return default

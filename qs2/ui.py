import getpass

class CliInterface(object):
  @property
  def getpass(self):
    return getpass.getpass

  @property
  def raw_input(self):
    return raw_input

UI = None

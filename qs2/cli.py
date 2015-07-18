import sqlalchemy
import argparse
import getpass
import sys
import inspect
import logging

import qs2.operations
import qs2.logutil

from qs2.error import (OperationFailed, ValidationFailed)

def main(args):
  qs2.logutil.setup_logging(args.log_level)
  try:
    with qs2.logutil.section("handling command-line operation"):
      with open(args.db) as credentials_file:
        engine = sqlalchemy.engine.create_engine(credentials_file.readline())
      qs2.model.metadata.bind = engine
      argnames = set(inspect.getargspec(args.main).args)
      filtered_args = {k: v for k, v in vars(args).items() if k in argnames}
      args.main(**filtered_args)
  except (OperationFailed, ValidationFailed) as e:
    logging.error("operation failed: %s", e.message)
    sys.exit(1)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="QS2 management tool.")
  parser.add_argument("--db", required=True,
                      help="file with database specifier")
  parser.add_argument("--log_level", default="info",
                      choices=["error", "warning", "info", "debug"],
                      help="verbosity level")
  subparsers = parser.add_subparsers()
  def mkparser(name, func, desc, *args):
    rv = subparsers.add_parser(name, help=desc)
    rv.set_defaults(main=func)
    for arg_name, arg_type, arg_help in args:
      rv.add_argument(arg_name, type=arg_type, help=arg_help)
    return rv
    
  mkparser("init", qs2.operations.initialize,
    "(re-)initialize the database")
  mkparser("full_reset", qs2.operations.full_reset,
    "drop all data and recreate the database")
  add_user_parser = mkparser("add_user", qs2.operations.add_user_interactive,
    "add a user",
    ("username", str, "username of user"),
  )
  mkparser("verify_user", qs2.operations.verify_user_interactive,
    "check the password of a user on the CLI",
    ("username", str, "username of user"),
  )

  main(parser.parse_args())

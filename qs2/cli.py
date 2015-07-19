import sqlalchemy
import argparse
import getpass
import sys
import inspect
import logging
import getpass
import decimal

import qs2.operations
import qs2.logutil
import qs2.ui

from qs2.error import (OperationFailed, ValidationFailed)

def engine_from_url_in_file(arg):
  with open(arg) as credentials_file:
    return sqlalchemy.engine.create_engine(credentials_file.readline())

def main(args, engine):
  qs2.logutil.setup_logging(args.log_level)
  try:
    with qs2.logutil.section("handling command-line operation"):
      argnames = set(inspect.getargspec(args.main).args)
      filtered_args = {k: v for k, v in vars(args).items() if k in argnames}
      conn = engine.connect()
      args.main(conn=conn, **filtered_args)
    return 0
  except (OperationFailed, ValidationFailed) as e:
    logging.error("operation failed: %s", e.message)
    return 1

def parse_args(argv):
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
      if arg_type == bool:
        rv.add_argument(arg_name, action="store_true", help=arg_help)
      else:
        rv.add_argument(arg_name, type=arg_type, help=arg_help)
    return rv
    
  mkparser("init", qs2.operations.initialize,
    "(re-)initialize the database")
  mkparser("drop_all", qs2.operations.drop_all,
    "drop all data")
  add_user_parser = mkparser("add_user", qs2.operations.add_user_interactive,
    "add a user",
    ("username", str, "username of user"),
  )
  mkparser("verify_user", qs2.operations.verify_user_interactive,
    "check the password of a user on the CLI",
    ("username", str, "username of user"),
  )
  mkparser("add_question", qs2.operations.add_question_interactive,
    "add a question interactively",
    ("username", str, "username of user"),
    ("--skip_auth", bool, "skip authentication check"),
  )
  mkparser("peek_question", qs2.operations.peek_question_interactive,
    "peek at the next question in the queue",
    ("username", str, "username of user"),
    ("--skip_auth", bool, "skip authentication check"),
  )
  mkparser("post_answer", qs2.operations.post_answer_interactive,
    "post an answer to a question",
    ("username", str, "username of user"),
    ("question_id", int, "question ID"),
    ("value", decimal.Decimal, "answer value (between 0 and 1)"),
    ("--skip_auth", bool, "skip authentication check"),
  )
  mkparser("survey", qs2.operations.survey_interactive,
    "post an answer to a question",
    ("username", str, "username of user"),
    ("--accept_stale", bool, "include questions that were recently answered"),
  )

  return parser.parse_args(argv)

def run_main(argv, engine=None, ui=None):
  args = parse_args(argv)
  engine = engine or engine_from_url_in_file(args.db)
  qs2.ui.UI = ui or qs2.ui.CliInterface()
  return main(parse_args(argv), engine)

if __name__ == '__main__':
  sys.exit(run_main(sys.argv[1:]))

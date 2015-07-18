import sqlalchemy
import argparse
import qs2.tables

def init_main(engine):
  qs2.tables.metadata.create_all(engine)

def main(args):
  with open(args.db) as credentials_file:
    engine = sqlalchemy.engine.create_engine(credentials_file.readline())
  {
    "init": lambda: init_main(engine),
  }[args.operation]()

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="QS2 management tool.")
  parser.add_argument("operation",
                      help="Operation to perform.")
  parser.add_argument("--db", required=True,
                      help="File with database specifier.")
  main(parser.parse_args())

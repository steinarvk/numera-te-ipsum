import cli
import contextlib
import qs2.model
import sqlalchemy

from sqlalchemy import sql

TestDbUrl = "postgresql:///quantifiedself_test"

class FakeUI(object):
  def __init__(self):
    self.passwords = []
    self.raws = []
    
  def inject_raw_input(self, line):
    self.raws.append(line)
    return self

  def inject_getpass(self, line):
    self.passwords.append(line)
    return self

  def getpass(self, *args_unused, **kwargs_unused):
    return self.passwords.pop(0)

  def raw_input(self, *args_unused, **kwargs_unused):
    return self.raws.pop(0)

@contextlib.contextmanager
def fake_db():
  engine = sqlalchemy.engine.create_engine(TestDbUrl)
  qs2.model.metadata.reflect(engine)
  qs2.model.metadata.drop_all(engine)
  qs2.model.metadata.create_all(engine)
  try:
    yield engine
  finally:
    qs2.model.metadata.reflect(engine)
    qs2.model.metadata.drop_all(engine)

def run_fake_main(engine, interface, argv, fail=False):
  interface = interface or FakeUI()
  full_argv = ["--db", "unused"] + list(argv)
  rv = cli.run_main(full_argv, engine=engine, ui=interface)
  if fail:
    assert rv != 0
  else:
    assert rv == 0
  

def test_cli_init_and_drop():
  with fake_db() as engine:
    run_fake_main(engine, None, ["init"])
    meta = sqlalchemy.MetaData()
    meta.reflect(engine)
    tableset = set(meta.tables)
    assert "requests" in tableset
    assert "survey_answers" in tableset
    assert "survey_questions" in tableset
    assert "users" in tableset
    run_fake_main(engine,
                  FakeUI().inject_raw_input("nope"),
                  ["drop_all"], fail=True)
    meta = sqlalchemy.MetaData()
    meta.reflect(engine)
    assert len(meta.tables) > 0
    run_fake_main(engine,
                  FakeUI().inject_raw_input("yes"),
                  ["drop_all"])
    meta = sqlalchemy.MetaData()
    meta.reflect(engine)
    assert len(meta.tables) == 0

def test_cli_add_user_failure_invalid_password():
  ui = FakeUI()
  ui.inject_getpass("x")
  ui.inject_getpass("x")
  with fake_db() as engine:
    run_fake_main(engine, ui, ["add_user", "peter"], fail=True)
    rows = engine.execute(sql.select([qs2.model.users])).fetchall()
    assert len(rows) == 0

def test_cli_add_user_failure_invalid_name():
  ui = FakeUI()
  ui.inject_getpass("password")
  ui.inject_getpass("password")
  with fake_db() as engine:
    run_fake_main(engine, ui, ["add_user", "x%"], fail=True)
    rows = engine.execute(sql.select([qs2.model.users])).fetchall()
    assert len(rows) == 0
    run_fake_main(engine, ui, ["add_user", "x" * 2048], fail=True)
    rows = engine.execute(sql.select([qs2.model.users])).fetchall()
    assert len(rows) == 0

def test_cli_add_user_failure_duplicate_name():
  ui = FakeUI()
  ui.inject_getpass("toomanysecrets")
  ui.inject_getpass("toomanysecrets")
  ui.inject_getpass("secretive")
  ui.inject_getpass("secretive")
  with fake_db() as engine:
    run_fake_main(engine, ui, ["add_user", "peter"], fail=False)
    rows = engine.execute(sql.select([qs2.model.users])).fetchall()
    assert len(rows) == 1
    run_fake_main(engine, ui, ["add_user", "peter"], fail=True)
    rows = engine.execute(sql.select([qs2.model.users])).fetchall()
    assert len(rows) == 1

def test_cli_add_user():
  ui = FakeUI()
  ui.inject_getpass("toomanysecrets")
  ui.inject_getpass("toomanysecrets")
  with fake_db() as engine:
    run_fake_main(engine, ui, ["add_user", "peter"])
    rows = engine.execute(sql.select([qs2.model.users])).fetchall()
    assert len(rows) == 1
    row = rows[0]
    assert row["username"] == "peter"

def test_cli_add_question():
  ui = FakeUI()
  ui.inject_getpass("toomanysecrets")
  ui.inject_getpass("toomanysecrets")
  ui.inject_getpass("toomanysecrets")
  ui.inject_raw_input("Do you like dogs?")
  ui.inject_raw_input("No")
  ui.inject_raw_input("Yes")
  ui.inject_raw_input("Kind of")
  ui.inject_raw_input("600")
  ui.inject_raw_input("y")
  with fake_db() as engine:
    run_fake_main(engine, ui, ["add_user", "peter"])
    run_fake_main(engine, ui, ["add_question", "peter"])
    rows = engine.execute(sql.select([qs2.model.survey_questions])).fetchall()
    assert len(rows) == 1
    row = rows[0]
    assert row["question"] == "Do you like dogs?"

def test_cli_add_question_aborted():
  ui = FakeUI()
  ui.inject_getpass("toomanysecrets")
  ui.inject_getpass("toomanysecrets")
  ui.inject_getpass("toomanysecrets")
  ui.inject_raw_input("Do you like dogs?")
  ui.inject_raw_input("No")
  ui.inject_raw_input("Yes")
  ui.inject_raw_input("Kind of")
  ui.inject_raw_input("")
  ui.inject_raw_input("n")
  with fake_db() as engine:
    run_fake_main(engine, ui, ["add_user", "peter"])
    run_fake_main(engine, ui, ["add_question", "peter"], fail=True)
    rows = engine.execute(sql.select([qs2.model.survey_questions])).fetchall()
    assert len(rows) == 0

def test_cli_add_question_failure_wrong_password():
  ui = FakeUI()
  ui.inject_getpass("toomanysecrets")
  ui.inject_getpass("toomanysecrets")
  ui.inject_getpass("to0manysecrets")
  with fake_db() as engine:
    run_fake_main(engine, ui, ["add_user", "peter"])
    run_fake_main(engine, ui, ["add_question", "peter"], fail=True)

def test_cli_add_question_skip_auth():
  ui = FakeUI()
  ui.inject_getpass("toomanysecrets")
  ui.inject_getpass("toomanysecrets")
  ui.inject_raw_input("Do you like dogs?")
  ui.inject_raw_input("No")
  ui.inject_raw_input("Yes")
  ui.inject_raw_input("Kind of")
  ui.inject_raw_input("600")
  ui.inject_raw_input("y")
  with fake_db() as engine:
    run_fake_main(engine, ui, ["add_user", "peter"])
    run_fake_main(engine, ui, ["add_question", "peter", "--skip_auth"])
    rows = engine.execute(sql.select([qs2.model.survey_questions])).fetchall()
    assert len(rows) == 1
    row = rows[0]
    assert row["question"] == "Do you like dogs?"
    run_fake_main(engine, ui, ["add_question", "ivan", "--skip_auth"],
                  fail=True)

import chess.pgn
import chess
import logging
import glob
import os.path
import random
import sys
import time
import json

class MiddlegameCriteria(object):
  def __init__(self):
    self.opening_percentile = 0.2
    self.opening_moves = 20
    self.endgame_percentile = 0.2
    self.endgame_moves = 10
    self.minimum_branching = 10

  def satisfies(self, i, n, board):
    x = float(i) / n
    if x < self.opening_percentile:
      return False
    if x > (1 - self.endgame_percentile):
      return False
    if i < self.opening_moves:
      return False
    if i > (n - self.endgame_moves):
      return False
    k = len(list(board.generate_legal_moves()))
    if k < self.minimum_branching:
      return False
    return True

def states_of_game(game):
  node = game
  while True:
    yield node.board().fen()
    if not node.variations:
      return
    node = node.variation(0)

def games_in_file(f):
  while True:
    pos = f.tell()
    try:
      game = chess.pgn.read_game(f)
    except Exception as e:
      logging.exception(e)
      logging.error("error processing '{}' at '{}'".format(f.name, pos))
      return
    if game is None:
      return
    yield pos, game

def generate_pgn_index(directory, pattern="*.pgn"):
  absdir = os.path.abspath(directory)
  for filename in glob.glob(os.path.join(absdir, pattern)):
    assert filename.startswith(absdir)
    fn = filename[len(absdir):]
    with open(filename, "r") as f:
      for pos, _ in games_in_file(f):
        yield fn, pos

def save_index(seq, output_filename):
  with open(output_filename, "w") as f:
    json.dump(list(seq), f)

def load_index(filename):
  with open(filename, "r") as f:
    return json.load(f)

def random_game(index, directory):
  name, pos = random.choice(index)
  if name.startswith("/"):
    name = name[1:]
  filename = os.path.join(directory, name)
  with open(filename, "r") as f:
    f.seek(pos)
    return chess.pgn.read_game(f)

def random_challenge(index, directory, criteria):
  while True:
    game = random_game(index, directory)
    states = list(states_of_game(game))
    white_indices = range(0, len(states), 2)
    for i in range(10):
      n = random.choice(white_indices)
      if not criteria.satisfies(n, len(states), chess.Board(states[n])):
        continue
      return game, n, states[n]

class IndexedGameCollection(object):
  def __init__(self, filename):
    self.directory, _ = os.path.split(filename)
    with open(filename, "r") as f:
      self.index = json.load(f)
    self.selector = MiddlegameCriteria()

  def get(self):
    return random_challenge(self.index, self.directory, self.selector)

if __name__ == '__main__':
  filename = sys.argv[1]
  games = IndexedGameCollection(filename)
  t0 = time.time()
  deadline = t0 + 30
  while time.time() < deadline:
    pgn, n, state = games.get()
    moves = list(chess.Board(state).generate_legal_moves())
    rv = {
      "headers": dict(pgn.headers),
      "moveno": n,
      "fen": state,
    }
    print rv

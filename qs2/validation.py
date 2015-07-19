import users
import logging
from qs2.error import ValidationFailed

def parse_as(name, parser, string, secret=False, loglevel=logging.DEBUG):
  try:
    v = parser(string)
  except Exception as e:
    if secret:
      message = "parsing failed"
    else:
      message = "parsing failed: {}".format(e.message)
    raise ValidationFailed(message)
  check(name, v, secret=secret, loglevel=loglevel)
  return v

def ask(name, parser, query, complain, secret=False, loglevel=logging.DEBUG):
  while True:
    try:
      return parse_as(name, parser, query(), secret=secret, loglevel=loglevel)
    except ValidationFailed as e:
      complain("invalid value: {}".format(e.message))

def check(name, value, secret=False, loglevel=logging.DEBUG):
  try:
    checker = Invalidators[name]
  except KeyError:
    raise ValidationFailed("unknown validator type {}".format(name))
  reason = checker(value)
  if reason:
    if secret:
      template = "invalid {name}: {reason}"
    else:
      template = "invalid {name} '{value}' ({reason})"
    message = template.format(name=name, value=value, reason=reason)
    logging.log(loglevel, message)
    raise ValidationFailed(message)

def invalidate_length(s, span):
  min_, max_ = span
  if len(s) < min_:
    return "too short"
  if len(s) > max_:
    return "too long"

def invalidate_chars(s, legal):
  for ch in s:
    if ch not in legal:
      return "illegal character '{}'".format(ch)

def number_invalidator(min_, max_):
  def f(x):
    if x < min_:
      return "{} is below minimal allowed value {}".format(x, min_)
    if x > max_:
      return "{} is above maximal allowed value {}".format(x, max_)
  return f

Invalidators = {
  "username": users.invalidate_username,
  "password": users.invalidate_password,
  "question": lambda s: invalidate_length(s, (1, 1024)),
  "label": lambda s: invalidate_length(s, (1, 128)),
  "survey_value": number_invalidator(0, 1),
}

import users
import logging
from qs2.error import ValidationFailed

Invalidators = {
  "username": users.invalidate_username,
  "password": users.invalidate_password,
  "question": lambda s: invalidate_length(s, (1, 1024)),
  "label": lambda s: invalidate_length(s, (1, 128)),
}

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


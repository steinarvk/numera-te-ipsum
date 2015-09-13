import requests
import logging

import qs2.logutil

@qs2.logutil.profiled("verify_captcha")
def verify_recaptcha(secret, response, remote_addr=None):
  url = "https://www.google.com/recaptcha/api/siteverify"
  args = {
    "secret": secret,
    "response": response,
  }
  if remote_addr:
    args["remoteip"] = remote_addr
  logging.info("validating CAPTCHA: response=%s, remote_addr=%s", response, remote_addr)
  try:
    server_response = requests.post(url, args).json()
  except (IOError, ValueError) as e:
    logging.error("recaptcha validation failed")
    logging.exception(e)
  return server_response["success"]

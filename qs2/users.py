import passlib.hash
import re
import string
import qs2

ValidUsernameChars = string.letters + string.digits
ValidUsernameLength = 2, 64
ValidPasswordLength = 3, 1024

def invalidate_username(username):
  return (
    qs2.validation.invalidate_length(username, ValidUsernameLength)
    or
    qs2.validation.invalidate_chars(username, ValidUsernameChars)
  )
  
def invalidate_password(password):
  return qs2.validation.invalidate_length(password, ValidPasswordLength)
    
def hash_password(password):
  return passlib.hash.sha256_crypt.encrypt(password)

def verify_password(password, hashed):
  return passlib.hash.sha256_crypt.verify(password, hashed)
  

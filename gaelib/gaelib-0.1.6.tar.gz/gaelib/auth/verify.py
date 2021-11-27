from flask import g, render_template, request, session
from gaelib.auth.models import User
import constants
import random
import string


def generate_user_token(length):
  letters = string.ascii_lowercase
  token = ''.join(random.choice(letters) for i in range(length))
  g.app.logger.info("Token of length " + str(length) + " is: " + token)
  return token


def get_user_token():
  token = request.headers.get('token')
  return token


def verify_request(token):
  g.app.logger.info("Verifying request")
  token_filter = ('token', '=', token)
  try:
    user = User.retrieve(filters=[token_filter])[0]
  except IndexError:
    return None
  return user

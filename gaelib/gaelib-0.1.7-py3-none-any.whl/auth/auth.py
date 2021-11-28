import sys
import requests
import google.oauth2.id_token

from flask import g, request, session
from google.auth.transport import requests as grequests
from gaelib.env import (get_dashboard_url_prefix,
                        get_app_or_default_prop,
                        is_dashboard_url)
from jose import jwt


def configure_login_callback(callback):
  setattr(sys.modules[__name__], 'login_callback', callback)


def get_user_id_and_token():

  auth_creds = request.authorization

  if auth_creds:
    user_id = auth_creds.username
    id_token = auth_creds.password
  else:
    user_id = session.get('gae_uid')
    id_token = session.get('gae_token')

  # Overriding id_token if firebaseaccesstoken is found in the browser cookie
  if is_dashboard_url() and 'firebaseAccessToken' in request.cookies:
    id_token = str(request.cookies.get('firebaseAccessToken'))

  return user_id, id_token


def get_auth_type():
  auth_type = ''
  try:
    auth_type = request.json.get('auth_type')
  except (AttributeError, KeyError):
    auth_type = ''

  if not auth_type:
    try:
      auth_type = request.form.get('auth_type')
    except (AttributeError, KeyError):
      auth_type = ''

  if not auth_type:
    try:
      auth_type = request.args.get('auth_type')
    except (AttributeError, KeyError):
      auth_type = ''

  if not auth_type:
    try:
      auth_type = request.params.get('auth_type')
    except (AttributeError, KeyError):
      auth_type = ''

  if not auth_type:
    auth_type = 'firebase'

  return auth_type


class Auth(object):
  """
      Class that implements methods to authenticate requests.
  """
  firebase_request_adapter = grequests.Request()

  def __init__(self, id_token, user_id=None):
    self.user_id = user_id
    self.id_token = id_token
    self.logger = g.app.logger

  def firebase_authorize(self):
    '''
        Authorize id_token with firebase,
        and return associated claims.
    '''
    self.logger.info("Authorizing ID token with Firebase")
    claims = google.oauth2.id_token.verify_firebase_token(
        self.id_token,
        Auth.firebase_request_adapter
    )
    return claims

  def auth0_authorize(self):
    '''
        Authorize id_token with firebase,
        and return associated claims.
    '''
    token = self.id_token
    jwks = requests.get(get_app_or_default_prop('AUTH0_JKWS_DOMAIN')).json()
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    for key in jwks["keys"]:
      if key["kid"] == unverified_header["kid"]:
        rsa_key = {
            "kty": key["kty"],
            "kid": key["kid"],
            "use": key["use"],
            "n": key["n"],
            "e": key["e"]
        }
    if rsa_key:
      try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=get_app_or_default_prop('AUTH0_API_AUDIENCE'),
            issuer="https://"+get_app_or_default_prop('AUTH0_DOMAIN')+"/"
        )
      except jwt.ExpiredSignatureError:
        self.logger.error('Expired Signature for %s', self.id_token)
        payload = {}
      except jwt.JWTClaimsError:
        self.logger.error('Wrong claims for %s', self.id_token)
        payload = {}
      except Exception as e:
        self.logger.error('Other Exception %s for %s', e, self.id_token)
        payload = {}

      self.logger.info("Auth0 payload received %s" % payload)
      return payload
    return {}

  def authorize_login_request(self, auth_type='firebase'):
    self.logger.info('Authorizing login request')
    if auth_type == 'firebase':
      claims = self.firebase_authorize()
    elif auth_type == 'auth0':
      self.logger.info('Auth0 login request for %s', self.id_token)
      claims = self.auth0_authorize()
    if claims:
      self.user_id = claims['sub']

    return claims

  def authorize_request(self, auth_type='firebase'):
    self.logger.info("Authorizing request")

    if auth_type == 'firebase':
      claims = self.firebase_authorize()
    elif auth_type == 'auth0':
      self.logger.info('Auth0 login request for %s', self.id_token)
      claims = self.auth0_authorize()

    if claims is None:
      return {}
    else:
      claimed_user_id = claims['sub']

    if claimed_user_id == self.user_id:
      return claims

    # claimed_user_id doesn't match request user_id
    return {}

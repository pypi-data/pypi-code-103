import json
import jwt
import time
from firebase_admin import credentials, initialize_app, messaging
from flask import g
from hyper import HTTPConnection

from gaelib.env import get_env, get_app_or_default_prop



ALGORITHM = 'ES256'

if get_env() == 'staging':
  APNS_KEY_ID = get_app_or_default_prop('STAGING_APNS_KEY_ID') # 'PVQ627R278'
  APNS_TEAM_ID = get_app_or_default_prop('STAGING_APNS_TEAM_ID') #'DH5NSA4U89'
  APNS_AUTH_KEY = get_app_or_default_prop('STAGING_APNS_AUTH_KEY')
  conn = HTTPConnection('api.sandbox.push.apple.com:443')
else:
  APNS_KEY_ID = get_app_or_default_prop('PROD_APNS_KEY_ID') # 'PVQ627R278'
  APNS_TEAM_ID = get_app_or_default_prop('PROD_APNS_TEAM_ID') #'DH5NSA4U89'
  APNS_AUTH_KEY = get_app_or_default_prop('PROD_APNS_AUTH_KEY')
  conn = HTTPConnection('api.sandbox.push.apple.com:443')

IOS_BUNDLE_ID = get_app_or_default_prop('IOS_BUNDLE_ID') # 'com.codejedi.crypticcup1'

f = open(APNS_AUTH_KEY)
secret = f.read()

def send_apns_notification(token_id, title, message):
  token = jwt.encode(
    {
        'iss': APNS_TEAM_ID,
        'iat': time.time()
    },
    secret,
    algorithm= ALGORITHM,
    headers={
        'alg': ALGORITHM,
        'kid': APNS_KEY_ID,
    }
  )
  request_headers = {
    'apns-expiration': '0',
    'apns-priority': '10',
    'apns-topic': BUNDLE_ID,
    'authorization': 'bearer {0}'.format(token.decode('ascii'))
  }
  payload = {
              'aps':{
                      'alert' : {
                                 'title' : title,
                                 'body' : message,
                                }
                     }
            }
  
  payload = json.dumps(payload).encode('utf-8')
  path = '/3/device/{0}'.format(token_id)
  conn.request(
    'POST',
    path,
    payload,
    headers=request_headers
  )
  resp = conn.get_response()
  print(resp.status)
  print(resp.read())

def send_fcm_notification(registration_tokens, title, message):
  cred = credentials.RefreshToken('<path to firebase credentials>.json')
      initialize_app(cred)
      registration_tokens = registration_tokens.
      message = messaging.MulticastMessage(
        data={'title': title, 'message': message},
        tokens=registration_tokens,
      )
  response = messaging.send_multicast(message)
  print(response.failure_count)

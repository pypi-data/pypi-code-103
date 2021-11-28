#!/opt/local/bin/python
# Copyright 2014, Octoboxy LLC.  All Rights Reserved.
''' Helper for decoding a Google reCAPTCHA token. '''

import base
import json
import logging

from . import environment
environment.DeferImport('requests')


def HumannessFromRecaptcha(request, token, action):
  ''' Makes a query to Google to validate a reCAPTCHA token.
      Returns humanness value 0 .. 1, or None if we're unable to reach Google.
  '''

  from django.conf import settings

  GOOGLE          = 'https://www.google.com/recaptcha/api/siteverify'
  INHUMAN         = 0

  if not settings.RECAPTCHA_SECRET_KEY:
    return None

  if not token:
    base.utils.Log('CAPTCHA', 'Token was not provided', level=logging.WARNING)
    return INHUMAN

  # Errors related to Google being down should return None and not INHUMAN
  data            = { 'secret': settings.RECAPTCHA_SECRET_KEY, 'response': token }
  remoteip        = base.utils.RemoteIp(request)
  if remoteip:
    data['remoteip']  = remoteip
  try:
    google        = requests.post(GOOGLE, data=data)
  except requests.exceptions.ConnectionError:
    google        = None
  if not google:
    base.utils.Log('CAPTCHA', 'Google unreachable', level=logging.WARNING)
    return None
  if google.status_code != 200:
    base.utils.Log('CAPTCHA', 'Google returned HTTP not-okay: {} {}'.format(google.status_code, google.reason), level=logging.WARNING)
    return None
  try:
    response      = json.loads(google.text)
  except json.decoder.JSONDecodeError:
    base.utils.Log('CAPTCHA', 'Google returned not-JSON!', level=logging.WARNING)
    return None
  # End Google section

  if not response.get('success'):
    base.utils.Log('CAPTCHA', 'Token validation failed: {!s}'.format(response.get('error-codes')), level=logging.WARNING)
    return INHUMAN

  if action and response.get('action') != action:
    base.utils.Log('CAPTCHA', 'Action mismatched {!s} != {!s}'.format(action, response.get('action')), level=logging.WARNING)
    return INHUMAN

  timestamp       = base.utils.ParseTimestamp(response.get('challenge_ts'))
  delta           = base.utils.Now() - timestamp
  if settings.RECAPTCHA_TOKEN_WINDOW and delta > settings.RECAPTCHA_TOKEN_WINDOW:
    base.utils.Log('CAPTCHA', 'Token too old: {}'.format(base.utils.FormatTimeDelta(delta)), level=logging.WARNING)
    return INHUMAN

  score           = response.get('score')
  if isinstance(score, int) or isinstance(score, float):
    score         = min(1, max(0, score))
    base.utils.Log('CAPTCHA', 'Score: {}'.format(score))
    return score

  base.utils.Log('CAPTCHA', 'Score was not a number!', level=logging.WARNING)


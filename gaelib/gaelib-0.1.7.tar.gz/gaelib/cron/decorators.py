from flask import request, abort
from gaelib.cron import constants


def cron_validate(handler):
  def check_if_cron(*args, **kwargs):
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
      client_ip = request.environ['REMOTE_ADDR']
    else:
      client_ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]

    if (request.headers.get('X-AppEngine-Cron') is None) and (client_ip not in constants.VALID_CRON_JOB_IP_ADDRS):
      return abort(400)
    else:
      return handler(*args, **kwargs)
  return check_if_cron

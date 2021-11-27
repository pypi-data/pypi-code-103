import os

from flask import g, jsonify, redirect, request, session
import constants
import gaelib.defaults as defaults


def is_dev():
  if os.getenv('GAE_DEPLOYMENT_ID', ''):
    return False
  else:
    return True


def is_prod():
  return not is_dev() and not is_staging()


def is_staging():
  return not is_dev() and 'staging' in os.getenv('GOOGLE_CLOUD_PROJECT')


def get_app_or_default_prop(prop_name):
  try:
    prop_value = getattr(constants, prop_name)
  except (AttributeError, ModuleNotFoundError):
    prop_value = ''
  if not prop_value:
    prop_value = getattr(defaults, prop_name)

  return prop_value


def get_dashboard_url_prefix():
  return get_app_or_default_prop('DASHBOARD_URL_PREFIX')


def get_dashboard_assets_prefix():
  return get_app_or_default_prop('DASHBOARD_ASSETS_PREFIX')


def is_dashboard_url():
  url = request.path
  return url.strip('/').startswith(get_dashboard_url_prefix())


def get_post_login_page():
  return get_app_or_default_prop('POST_LOGIN_PAGE')


def get_sidebar_template():
  return get_app_or_default_prop('SIDEBAR_TEMPLATE')


def get_staff_phones():
  return get_app_or_default_prop('STAFF_PHONES')


def get_profile_picture():
  return get_app_or_default_prop('DEFAULT_PROFILE_IMAGE')


def get_token_length():
  return get_app_or_default_prop('TOKEN_LENGTH')


def get_twilio_verification_sid():
  return get_app_or_default_prop('VERIFICATION_SID')


def get_twilio_account_sid():
  return get_app_or_default_prop('ACCOUNT_SID')


def get_twilio_auth_token():
  return get_app_or_default_prop('AUTH_TOKEN')


def dashboard_login_page():
  return redirect("/" + get_dashboard_url_prefix() + '/login', code=302)


def get_env():
  env = 'staging' if not is_prod() else 'prod'
  return env

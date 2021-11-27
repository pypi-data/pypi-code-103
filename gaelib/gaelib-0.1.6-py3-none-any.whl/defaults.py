"""
    This module contains all defaults available for when
    the application importing the lib doesnt set values
"""
DASHBOARD_URL_PREFIX = 'admindashboard'
DASHBOARD_ASSETS_PREFIX = 'https://storage.googleapis.com/gaelib-assets/assets'
POST_LOGIN_PAGE = 'users'
SIDEBAR_TEMPLATE = 'dashboard/operations_sidebar'
PARAMETER_LOGGING = 'true'
SESSION_SECRET = 'lib_key'
# TODO: Move this to a more generic bucket name
DEFAULT_PROFILE_IMAGE = 'https://storage.googleapis.com/crypticcup-images/default_profile.jpg'

# Twilio Auth Settings
VERIFICATION_SID = ''
ACCOUNT_SID = ''
AUTH_TOKEN = ''
TOKEN_LENGTH = 12

# APNS Settings
AUTH0_JKWS_DOMAIN = ''

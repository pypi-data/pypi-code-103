from gaelib.view.base_view import BaseHttpHandler
from gaelib.auth.models import User, UserRole
from gaelib.auth import auth, verify
from gaelib.env import get_app_or_default_prop, get_profile_picture, get_token_length
from gaelib.auth.twilio_client import TwilioClient
from flask import g, request, session


# pragma pylint: disable=too-few-public-methods


class Login(BaseHttpHandler):
  """
      The Login view function to sign in a user based on id_token.
      Creates a new User in datastore if user doesn't exist already.
  """

  def dispatch_request(self):
    """
        Process and dispatch response for request to Base-URL/login/
    """
    g.app.logger.debug("In Login View dispatch_request")
    user_id, id_token = auth.get_user_id_and_token()
    auth_type = auth.get_auth_type()

    if not user_id:
      return self.json_error("NO USER_ID", 400)

    if not id_token:
      return self.json_error("NO_ID_TOKEN", 400)

    # Make auth object
    auth_ob = auth.Auth(id_token=id_token)

    # pragma pylint: disable=broad-except
    # Verify the id_token with Firebase
    try:
      claims = auth_ob.authorize_login_request(auth_type=auth_type)
    except Exception as e:
      return self.json_error(
          "UNAUTHORIZED_TOKEN" + str(e), 401, "Unauthorised login attempt:")

    # Check if id_token has been authorised
    # if claims is None, Unauthorised
    if not claims:
      return self.json_error("EMPTY_CLAIM", 401, "Unauthorised login attempt:")

    g.app.logger.info("Signing in with claims %s" % str(claims))

    if request.json:
      device_token_data = request.json.get('device_token', {})
    else:
      device_token_data = {}

    user = check_for_new_user(g.app.logger, user_id=auth_ob.user_id, claims=claims,
                              device_token_data=device_token_data)

    session["gae_uid"] = user_id
    session["gae_token"] = id_token

    auth.login_callback(user)
    if auth_type == 'firebase':
      provider = claims.get('firebase').get('sign_in_provider')
    elif auth_type == 'auth0':
      provider = 'apple' if 'apple' in user.uid else 'google'

    response_dict = {"id": user.key().id,
                     "uId": user.uid,
                     "email": user.email,
                     "name": user.name,
                     "picture": user.picture,
                     "provider": provider,
                     }
    return self.json_success(response_dict, 202)


class Verification(BaseHttpHandler):

  def dispatch_request(self):
    """
        Process and dispatch response for request to Base-URL/verification/
    """
    g.app.logger.debug("In Verification View dispatch_request")
    if request.method == 'GET':
      req_args = request.args.to_dict()
      phone = req_args.get('phone')
      email = req_args.get('email')
      status = None
      if phone:
        to = phone
        channel = 'sms'
      elif email:
        to = email
        channel = 'email'
      else:
        return self.json_error("No phone number or e-mail specified", 400)
      status = TwilioClient().send_verification_code(to, channel)
      if status is not None:
        response_dict = {'status': 'success'}
        return self.json_success(response_dict, 200)
      else:
        return self.json_error("Error while sending verification code", 400)

    elif request.method == 'POST':
      phone = request.form.get('phone')
      email = request.form.get('email')
      code = request.form.get('code')
      status = None
      if phone:
        g.app.logger.debug("Verifying Phone")
        to = phone
      elif email:
        g.app.logger.debug("Verifying E-Mail")
        to = email
      else:
        return self.json_error("No Phone Number", 400)

      status = TwilioClient().check_verification(to, code)
      if status == 'success':
        user = check_for_new_user(g.app.logger, phone=phone, email=email)
        auth.login_callback(user)
        response_dict = {
            'status': 'success',
            'token': user.token
        }
        return self.json_success(response_dict, 200)
      else:
        return self.json_error("Incorrect Code", 400)


def check_for_new_user(logger, user_id=None, claims=None, device_token_data=None, phone=None, email=None):
  auth_type = auth.get_auth_type()
  if auth_type == 'verify':
    return check_for_new_user_with_phone_or_email(logger, phone, email, device_token_data)
  else:
    return check_for_new_user_with_uid(logger, user_id, claims, device_token_data)


def check_for_new_user_with_uid(logger, user_id, claims, device_token_data):
  """
      checks if user with email exists in datastore.
      If exists, return games_played, games_won,
      Else, add to datastore
      with attributes
      user_id, email, games_played, games_won, join_date
  """

  logger.info("Checking if " + user_id + " is a new user")

  uid_filter = ('uid', '=', user_id)

  try:
    user = User.retrieve(filters=[uid_filter])[0]
  except IndexError:
    user = None
  except Exception as e:
    logger.info("Error trying to retrieve User %s", e)

  if not user:
    # Checking for user being an old cryptic cup member
    # from migration. This is not code that should be in
    # the library long term
    email_filter = ('email', '=', claims['email'])
    filters = [email_filter]

    ######
    # TODO: Handle multiple users
    ####
    try:
      user = User.retrieve(filters=filters)[0]
    except IndexError:
      user = None

  name = claims.get('name', '')
  if not name:
    email = claims['email']
    name = email[:email.find('@')]

  picture = claims.get('picture', get_profile_picture())
  if user:
    user.update(
        uid=user_id,
        picture=picture,
        name=name,
        role=UserRole.DEFAULT.value
    )
  else:
    logger.info("Creating new user")
    logger.debug("\tUser ID: " + user_id)
    user = User(
        uid=user_id,
        email=claims['email'],
        picture=picture,
        name=name,
        role=UserRole.DEFAULT.value
    )
  user = update_device_token_data(user, device_token_data)
  user.put()
  return user


def check_for_new_user_with_phone_or_email(logger, phone, email, device_token_data):
  """
      checks if user with phone exists in datastore.
      If not then create a  new user.
  """

  if phone:
    logger.info("Checking if User with Phone:" + phone + " is a new user")
    filters = [('phone', '=', phone)]
  elif email:
    logger.info("Checking if User with Email:" + email + " is a new user")
    filters = [('email', '=', email)]
  else:
    logger.error("No Phone/E-mail provided to check new User")
    return None

  try:
    user = User.retrieve(filters=filters)[0]
  except IndexError:
    user = None
  except Exception as e:
    logger.info("Error trying to retrieve User %s", e)

  if not user:
    logger.info("Creating new user")
    user = User(
        phone=phone,
        email=email,
        token=verify.generate_user_token(get_token_length()),
        role=UserRole.DEFAULT.value,
        picture=get_profile_picture()
    )
  else:
    logger.info("Updating token for the existing user")
    user.update(token=verify.generate_user_token(get_token_length()))

  user = update_device_token_data(user, device_token_data)
  user.put()
  return user


def update_device_token_data(user, device_token_data):
  if device_token_data:
    user.update(
        os=device_token_data.get('os'),
        device_notification_token=device_token_data.get('token')
    )
  return user

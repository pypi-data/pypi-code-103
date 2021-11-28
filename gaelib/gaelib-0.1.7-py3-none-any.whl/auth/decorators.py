import constants
from flask import g, jsonify, request, session
from gaelib.auth import auth, verify
from gaelib.auth.models import User, UserRole
from gaelib.env import dashboard_login_page, is_dashboard_url


def auth_required(view_function):
  """
      Function to be used with as_view().
      Returns a decorator function which authenticates a request
      before the target view's dispatch_request() is invoked.
  """
  def decorator(*args, **kwargs):
    """
        Authenticates request before invoking dispatch_request
        of target view.
    """
    response_dict = {"success": 0}

    user_id, id_token = auth.get_user_id_and_token()
    auth_type = auth.get_auth_type()
    if is_dashboard_url() and not (user_id and id_token):
      return dashboard_login_page()

    if not user_id:
      response_dict["error_message"] = "UNAUTHORIZED USER"
      return jsonify(response_dict), 401

    if not id_token:
      response_dict["error_message"] = "UNAUTHORIZED TOKEN"
      return jsonify(response_dict), 401

    auth_ob = auth.Auth(id_token, user_id)
    error = ''
    # pragma pylint: disable=broad-except
    try:
      auth_result = auth_ob.authorize_request(auth_type=auth_type)
    except Exception as e:
      error = e
      auth_result = None

    if not auth_result:
      error = "Unauthorised login for web request found"
      if is_dashboard_url():
        g.app.logger.warning(error)
        session.pop("gae_uid", None)
        return dashboard_login_page()

      response_dict["error_message"] = str(error)
      return jsonify(response_dict), 401

    uid_filter = ('uid', '=', user_id)
    user = User.retrieve(filters=[uid_filter])[0]
    g.user_key = user.key().id
    return view_function(*args, **kwargs)

  # The following if block is required to avoid different
  # view functions getting mapped to the same endpoint name
  # when the view_function is a LazyView object.
  # We explicitly change the decorator name to the LazyView object's
  # view_function name.
  # This ensures there's no conflicting view function to end point mapping.
  # Note that if this is not done, then registering more than 1 url rules
  # to the same blueprint (say solo) will get the same endpoint name (solo.decorator)
  # which raises an exception.
  # Refer to
  # https://stackoverflow.com/questions/17256602/assertionerror-view-function-mapping-is-overwriting-an-existing-endpoint-functi
  # for further details
  if view_function.__class__.__name__ == "LazyView":
    decorator.__name__ = view_function.view_function
  return decorator


def verification_required(view_function):
  """
      Function to be used with as_view().
      Returns a decorator function which authenticates a request
      before the target view's dispatch_request() is invoked.
  """
  def decorator(*args, **kwargs):
    """
        Authenticates request before invoking dispatch_request
        of target view.
    """
    response_dict = {"success": 0}

    token = verify.get_user_token()

    if is_dashboard_url() and not token:
      return dashboard_login_page()

    if not token:
      response_dict["error_message"] = "USER TOKEN NOT FOUND IN HEADERS"
      return jsonify(response_dict), 401

    verify_result = verify.verify_request(token)

    if not verify_result:
      error = "Unauthorised login for web request found"
      if is_dashboard_url():
        g.app.logger.warning(error)
        return dashboard_login_page()
      response_dict['error_message'] = error
      return jsonify(response_dict), 401

    # Add Logic to incorporate new user criteria
    g.user_key = verify_result.key().id
    return view_function(*args, **kwargs)

  # The following if block is required to avoid different
  # view functions getting mapped to the same endpoint name
  # when the view_function is a LazyView object.
  # We explicitly change the decorator name to the LazyView object's
  # view_function name.
  # This ensures there's no conflicting view function to end point mapping.
  # Note that if this is not done, then registering more than 1 url rules
  # to the same blueprint (say solo) will get the same endpoint name (solo.decorator)
  # which raises an exception.
  # Refer to
  # https://stackoverflow.com/questions/17256602/assertionerror-view-function-mapping-is-overwriting-an-existing-endpoint-functi
  # for further details
  if view_function.__class__.__name__ == "LazyView":
    decorator.__name__ = view_function.view_function
  return decorator


def access_control(role):
  def decorator_without_arg(view_func):
    def access_control_decorator(*args, **kwargs):
      response_dict = {"success": 0}
      user = get_login_user()
      if user:
        if UserRole(user.role) is role:
          return view_func(*args, **kwargs)
        else:
          g.app.logger.error(
              "User %s does not have access to staff only ", str(user.__dict__))
      else:
        g.app.logger.error("Unauthorised access, user doesn't exist")

      response_dict["error_message"] = "UNAUTHORIZED ACCESS"
      return jsonify(response_dict), 200
    return access_control_decorator

  return decorator_without_arg


def get_login_user():
  auth_type = auth.get_auth_type()

  if auth_type == 'verify':
    token = verify.get_user_token()
    filter = ('token', '=', token)
  else:
    user_id, _ = auth.get_user_id_and_token()
    filter = ('uid', '=', user_id)

  try:
    user = User.retrieve(filters=[filter])[0]
  except IndexError:
    user = None
  return user

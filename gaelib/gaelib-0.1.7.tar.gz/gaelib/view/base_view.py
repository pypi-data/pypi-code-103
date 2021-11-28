"""
    This Module defines the BaseView Class
    which inherits View and has logger object
"""
from flask import g, jsonify, request
from flask.views import View
from werkzeug.utils import import_string, cached_property

from gaelib.auth.decorators import auth_required
from gaelib.cron.decorators import cron_validate


class LazyView(object):
  """
      This class is used to import the view class
      when needed and prevent upfront import.
  """

  def __init__(self, import_name, view_function):
    self.__module__, self.__name__ = import_name.rsplit('.', 1)
    self.import_name = import_name
    self.view_function = view_function

  @cached_property
  def view(self):
    return import_string(self.import_name).as_view(self.view_function)

  def __call__(self, *args, **kwargs):
    return self.view(*args, **kwargs)


class BaseHttpHandler(View):
  """ BaseView Class """

  def json_response(self, response_body, status, headers=None):
    if not isinstance(response_body, dict):
      g.app.logger.error("Response body not a dict, cannot convert to JSON")
      raise TypeError(
          "'\nThe view function return type must be a dictionary,'"
          "'but it was a {response_body.__class__.__name__}.'"
          .format(response_body=response_body))

    response_body = jsonify(response_body)

    if headers is None:
      headers = {}
    headers["Content-Type"] = "application/json"
    return response_body, status, headers

  def json_error(self, error_message, status_code, warning_message=None):
    """
        Logs error messages, defines appropriate response_dict,
        and returns the same with status code.
    """
    if warning_message is not None:
      g.app.logger.warning(warning_message)

    g.app.logger.error(error_message)
    response_dict = {}
    response_dict["success"] = 0
    response_dict["error_message"] = error_message
    return self.json_response(response_dict, status_code)

  def json_success(self, response_dict, status_code):
    """
        Updates response_dict with success=1.
        Returns the same with status code.
    """
    response_dict["success"] = 1
    return self.json_response(response_dict, status_code)

  def validate_request_args(self):
    request_args = request.args.to_dict()
    self.missing_args = []

    for args in self.required_request_args:
      if args not in request_args:
        self.missing_args.append(args)

    if not self.missing_args:
      return True
    return False

  def validation_error(self):
    if self.missing_args:
      return self.json_error("Missing Arguements: " + str(self.missing_args), 200)


class BaseApiHandler(BaseHttpHandler):
  decorators = [auth_required]


class BaseCronJobHandler(BaseHttpHandler):
  decorators = [cron_validate]

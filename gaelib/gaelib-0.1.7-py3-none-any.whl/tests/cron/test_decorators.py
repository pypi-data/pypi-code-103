from gaelib.tests.base import BaseUnitTestCase
from gaelib.cron.decorators import cron_validate
from werkzeug.exceptions import HTTPException
from mock import Mock


class DecoratorsTestCase(BaseUnitTestCase):

  def setUp(self):
    super().setUp()

  def check_success(self):
    self.tests_app.preprocess_request()
    decorated_func = cron_validate(Mock(return_value="OK"))
    response = decorated_func()
    self.assertEqual(response, "OK")

  def check_exception(self):
    self.tests_app.preprocess_request()
    decorated_func = cron_validate(Mock())
    self.assertRaises(HTTPException, decorated_func)

  def test_cron_validate_when_ip_is_not_valid(self):
    environ_dict = {
        'REMOTE_ADDR': '0.1.0.2'
    }
    with self.tests_app.test_request_context(environ_base=environ_dict):
      self.check_exception()

  def test_cron_validate_when_ip_is_valid(self):
    environ_dict = {
        'REMOTE_ADDR': '0.1.0.1'
    }
    with self.tests_app.test_request_context(environ_base=environ_dict):
      self.check_success()

  def test_cron_validate_with_http_valid_ip(self):
    environ_dict = {
        'HTTP_X_FORWARDED_FOR': '0.1.0.1,x.x.x.x'
    }
    with self.tests_app.test_request_context(environ_base=environ_dict):
      self.check_success()

  def test_cron_validate_with_http_forwarded_invalid_ip(self):
    environ_dict = {
        'HTTP_X_FORWARDED_FOR': '0.1.0.2,x.x.x.x'
    }
    with self.tests_app.test_request_context(environ_base=environ_dict):
      self.check_exception()

  def test_cron_validate_with_appengine_header_and_valid_ip(self):
    environ_dict = {
        'REMOTE_ADDR': '0.1.0.1',
        'HTTP_X_AppEngine_Cron': ''
    }
    with self.tests_app.test_request_context(environ_base=environ_dict, headers={}):
      self.check_success()

  def test_cron_validate_with_appengine_header_and_invalid_ip(self):
    environ_dict = {
        'REMOTE_ADDR': '0.1.0.1',
        'HTTP_X_AppEngine_Cron': ''
    }
    with self.tests_app.test_request_context(environ_base=environ_dict, headers={}):
      self.check_success()

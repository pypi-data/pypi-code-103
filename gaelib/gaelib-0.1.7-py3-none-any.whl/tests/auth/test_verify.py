from gaelib.tests.auth.base import BaseAuthUnitTestCase
from gaelib.storage import helpers
from gaelib.auth.twilio_client import TwilioClient
from gaelib.auth import verify
from gaelib.auth.models import User
from mock import patch
from gaelib.utils import web
from flask import g


class VerifyTestCase(BaseAuthUnitTestCase):

  def setUp(self):
    super().setUp()
    self.mock_twilio_client()

  def test_generate_user_token(self):
    with self.tests_app.test_request_context():
      self.tests_app.preprocess_request()
      token = verify.generate_user_token(10)
      self.assertEquals(len(token), 10)
      self.assertTrue(token.islower())

  def test_get_user_token(self):
    url = 'admindashboard/login'
    headers = {
        'token': 'dummy_token'
    }
    with self.tests_app.test_request_context(url, headers=headers):
      self.tests_app.preprocess_request()
      token = verify.get_user_token()
      self.assertEquals(token, 'dummy_token')

  def test_get_user_token_when_no_token_is_sent(self):
    url = 'admindashboard/login'
    with self.tests_app.test_request_context(url):
      self.tests_app.preprocess_request()
      token = verify.get_user_token()
      self.assertIsNone(token)

  def test_verify_request_when_token_matches(self):
    user = self.add_user_entity(name='User', token='Token')
    with self.tests_app.test_request_context():
      self.tests_app.preprocess_request()
      user = verify.verify_request('Token')
      self.assertIsNotNone(user)
      self.assertEquals(user.name, 'User')

  def test_verify_request_when_token_does_not_match(self):
    user = self.add_user_entity(name='User', token='Token')
    with self.tests_app.test_request_context():
      self.tests_app.preprocess_request()
      user = verify.verify_request('Token_1')
      self.assertIsNone(user)

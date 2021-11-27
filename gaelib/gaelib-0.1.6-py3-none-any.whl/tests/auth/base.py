from mock import patch, Mock
from gaelib.auth.models import User
from gaelib.tests.base import BaseUnitTestCase
from gaelib.utils import web


class BaseAuthUnitTestCase(BaseUnitTestCase):

  def setUp(self):
    super().setUp()

  def tearDown(self):
    super().tearDown()

  def add_user_entity(self, name='', email='', phone='', picture='http://dp.com', uid='', token='', role=0):
    user = User()
    user.update(
        name=name,
        email=email,
        picture=picture,
        phone=phone,
        uid=uid,
        token=token,
        role=role
    )
    user.put()
    return user

  def mock_twilio_client(self):
    self.twilio_client_patch = patch(
        'gaelib.auth.twilio_client.TwilioClient.get_client')
    self.twilio_client = self.twilio_client_patch.start()

  def mock_firebase_authorize(self):
    self.firebase_authorize_patch = patch(
        'gaelib.auth.auth.Auth.firebase_authorize')
    self.firebase_authorize = self.firebase_authorize_patch.start()

  def mock_auth0_authorize(self):
    self.auth0_authorize_patch = patch(
        'gaelib.auth.auth.Auth.auth0_authorize')
    self.auth0_authorize = self.auth0_authorize_patch.start()

  def mock_auth_obj(self):
    self.auth_obj_patch = patch(
        'gaelib.auth.auth.Auth')
    self.auth_obj = self.auth_obj_patch.start()

  def mock_get_user_id_and_token(self):
    self.get_user_id_and_token_patch = patch(
        'gaelib.auth.auth.get_user_id_and_token')
    self.get_user_id_and_token = self.get_user_id_and_token_patch.start()

  def mock_get_user_token(self):
    self.get_user_token_patch = patch(
        'gaelib.auth.verify.get_user_token')
    self.get_user_token = self.get_user_token_patch.start()

  def mock_get_auth_type(self):
    self.get_auth_type_patch = patch('gaelib.auth.auth.get_auth_type')
    self.get_auth_type = self.get_auth_type_patch.start()

  def mock_send_verification_code(self):
    self.send_verification_code_patch = patch(
        'gaelib.auth.twilio_client.TwilioClient.send_verification_code')
    self.send_verification_code = self.send_verification_code_patch.start()

  def mock_check_verification(self):
    self.check_verification_patch = patch(
        'gaelib.auth.twilio_client.TwilioClient.check_verification')
    self.check_verification = self.check_verification_patch.start()

  def mock_check_for_new_user_with_uid(self):
    self.check_for_new_user_with_uid_patch = patch(
        'gaelib.auth.views.check_for_new_user_with_uid')
    self.check_for_new_user_with_uid = self.check_for_new_user_with_uid_patch.start()

  def mock_check_for_new_user_with_phone_or_email(self):
    self.check_for_new_user_with_phone_or_email_patch = patch(
        'gaelib.auth.views.check_for_new_user_with_phone_or_email')
    self.check_for_new_user_with_phone_or_email = self.check_for_new_user_with_phone_or_email_patch.start()

  def mock_login_callback(self):
    self.login_callback_patch = patch(
        'gaelib.auth.auth.login_callback', create=True)
    self.login_callback = self.login_callback_patch.start()

  def mock_requests_get(self):
    self.requests_get_patch = patch(
        'requests.get')
    self.requests_get = self.requests_get_patch.start()

  def mock_jwt_get_unverified_header(self):
    self.jwt_get_unverified_header_patch = patch(
        'jose.jwt.get_unverified_header')
    self.jwt_get_unverified_header = self.jwt_get_unverified_header_patch.start()

  def mock_jwt_decode(self):
    self.jwt_decode_patch = patch(
        'jose.jwt.decode')
    self.jwt_decode = self.jwt_decode_patch.start()

  def get_mock_response(self, status=200, json_data=None):
    mock_resp = Mock()
    mock_resp.status_code = status

    # add json data if provided
    if json_data:
        mock_resp.json = Mock(
            return_value=json_data
        )
    return mock_resp

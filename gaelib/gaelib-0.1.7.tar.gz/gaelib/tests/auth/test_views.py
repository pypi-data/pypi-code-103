from gaelib.tests.auth.base import BaseAuthUnitTestCase
from gaelib.auth.models import User
from gaelib.auth import views
from gaelib.utils import web
from flask import g
import base64
import json

class LoginViewTestCase(BaseAuthUnitTestCase):
  def setUp(self):
    super().setUp()
    self.mock_firebase_authorize()
    self.mock_auth0_authorize()
    self.mock_login_callback()

  def tearDown(self):
    self.firebase_authorize_patch.stop()
    self.auth0_authorize_patch.stop()
    self.login_callback_patch.stop()
    super().tearDown()

  def test_when_authorization_is_present_with_both_user_id_and_id_token_and_auth_type_is_not_present_and_user_does_not_exist(self):
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b"sub:pass").decode("utf8"))
    }
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    self.firebase_authorize.return_value = claims
    response = self.client.post('/login/', headers=headers)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(202, response.status_code)
    user = User(key_str=data['id'])
    self.assertIsNotNone(user)
    self.assertEquals(data["uId"], user.uid)
    self.assertEquals(data["name"], user.name)
    self.assertEquals(1, self.get_entity_count('User'))

  def test_when_authorization_is_present_with_both_user_id_and_id_token_and_auth_type_is_not_present_and_user_already_exists(self):
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b"sub:pass").decode("utf8"))
    }
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    user = self.add_user_entity(uid='sub', name='user', email='email@abc')
    self.firebase_authorize.return_value = claims
    response = self.client.post('/login/', headers=headers)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(202, response.status_code)
    user_response = User(key_str=data['id'])
    self.assertIsNotNone(user)
    self.assertEquals(data["uId"], user.uid)
    self.assertEquals(data["name"], user.name)
    self.assertEquals(1, self.get_entity_count('User'))
    self.assertEquals(user.key().id, data['id'])


  def test_when_authorization_is_present_with_both_user_id_and_id_token_and_auth_type_is_firebase_and_user_does_not_exist(self):
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b"sub:pass").decode("utf8"))
    }
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    self.firebase_authorize.return_value = claims
    response = self.client.post('/login/?auth_type=firebase', headers=headers)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(202, response.status_code)
    user = User(key_str=data['id'])
    self.assertIsNotNone(user)
    self.assertEquals(data["uId"], user.uid)
    self.assertEquals(data["name"], user.name)
    self.assertEquals(1, self.get_entity_count('User'))


  def test_when_authorization_is_present_with_both_user_id_and_id_token_and_auth_type_is_firebase_and_user_already_exists(self):
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b"sub:pass").decode("utf8"))
    }
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    user = self.add_user_entity(uid='sub', name='user', email='email@abc')
    self.firebase_authorize.return_value = claims
    response = self.client.post('/login/?auth_type=firebase', headers=headers)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(202, response.status_code)
    user_response = User(key_str=data['id'])
    self.assertIsNotNone(user)
    self.assertEquals(data["uId"], user.uid)
    self.assertEquals(data["name"], user.name)
    self.assertEquals(1, self.get_entity_count('User'))
    self.assertEquals(user.key().id, data['id'])


  def test_when_authorization_is_present_with_both_user_id_and_id_token_and_auth_type_is_auth_0_and_user_does_not_exist(self):
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b"sub:pass").decode("utf8"))
    }
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    self.auth0_authorize.return_value = claims
    response = self.client.post('/login/?auth_type=auth0', headers=headers)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(202, response.status_code)
    user = User(key_str=data['id'])
    self.assertIsNotNone(user)
    self.assertEquals(data["uId"], user.uid)
    self.assertEquals(data["name"], user.name)
    self.assertEquals(1, self.get_entity_count('User'))


  def test_when_authorization_is_present_with_both_user_id_and_id_token_and_auth_type_is_auth_0_and_user_already_exists(self):
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b"sub:pass").decode("utf8"))
    }
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    user = self.add_user_entity(uid='sub', name='user', email='email@abc')
    self.auth0_authorize.return_value = claims
    response = self.client.post('/login/?auth_type=auth0', headers=headers)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(202, response.status_code)
    user_response = User(key_str=data['id'])
    self.assertIsNotNone(user)
    self.assertEquals(data["uId"], user.uid)
    self.assertEquals(data["name"], user.name)
    self.assertEquals(1, self.get_entity_count('User'))
    self.assertEquals(user.key().id, data['id'])


  def test_when_authorization_is_present_with_both_user_id_and_id_token_and_auth_type_is_not_present_and_user_does_not_exist(self):
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b"sub:pass").decode("utf8"))
    }
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    self.firebase_authorize.return_value = claims
    response = self.client.post('/login/', headers=headers)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(202, response.status_code)
    user = User(key_str=data['id'])
    self.assertIsNotNone(user)
    self.assertEquals(data["uId"], user.uid)
    self.assertEquals(data["name"], user.name)
    self.assertEquals(1, self.get_entity_count('User'))


  def test_when_authorization_is_present_with_user_id_and_auth_type_is_not_present(self):
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b"sub:").decode("utf8"))
    }
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    self.firebase_authorize.return_value = claims
    response = self.client.post('/login/', headers=headers)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(400, response.status_code)
    self.assertEquals("NO_ID_TOKEN", data["error_message"])
    self.assertEquals(0, self.get_entity_count('User'))

  def test_when_authorization_is_present_with_id_token_and_auth_type_is_not_present(self):
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b":pass").decode("utf8"))
    }
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    self.firebase_authorize.return_value = claims
    response = self.client.post('/login/', headers=headers)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(400, response.status_code)
    self.assertEquals("NO USER_ID", data["error_message"])
    self.assertEquals(0, self.get_entity_count('User'))
    self.assertEquals(0, self.get_entity_count('Player'))

  def test_when_authorization_is_not_present_and_auth_type_is_not_present(self):
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    self.firebase_authorize.return_value = claims
    response = self.client.post('/login/')
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(400, response.status_code)
    self.assertEquals("NO USER_ID", data["error_message"])
    self.assertEquals(0, self.get_entity_count('User'))

  def test_when_session_is_present_with_both_user_id_and_id_token_and_auth_type_is_not_present_and_user_does_not_exist(self):
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    self.firebase_authorize.return_value = claims
    with self.client.session_transaction() as sess:
      sess['gae_uid'] = 'sub'
      sess['gae_token'] = 'token'
    response = self.client.post('/login/')
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(202, response.status_code)
    user = User(key_str=data['id'])
    self.assertIsNotNone(user)
    self.assertEquals(data["uId"], user.uid)
    self.assertEquals(data["name"], user.name)
    self.assertEquals(1, self.get_entity_count('User'))


  def test_when_session_is_present_with_both_user_id_and_id_token_and_auth_type_is_not_present_and_user_already_exists(self):
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    user = self.add_user_entity(uid='sub', name='user', email='email@abc')
    self.firebase_authorize.return_value = claims
    with self.client.session_transaction() as sess:
      sess['gae_uid'] = 'sub'
      sess['gae_token'] = 'token'
    response = self.client.post('/login/')
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(202, response.status_code)
    user_response = User(key_str=data['id'])
    self.assertIsNotNone(user)
    self.assertEquals(data["uId"], user.uid)
    self.assertEquals(data["name"], user.name)
    self.assertEquals(1, self.get_entity_count('User'))
    self.assertEquals(user.key().id, data['id'])


  def test_when_session_is_present_with_both_user_id_and_id_token_and_auth_type_is_firebase_and_user_does_not_exist(self):
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    self.firebase_authorize.return_value = claims
    with self.client.session_transaction() as sess:
      sess['gae_uid'] = 'sub'
      sess['gae_token'] = 'token'
    response = self.client.post('/login/?auth_type=firebase')
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(202, response.status_code)
    user = User(key_str=data['id'])
    self.assertIsNotNone(user)
    self.assertEquals(data["uId"], user.uid)
    self.assertEquals(data["name"], user.name)
    self.assertEquals(1, self.get_entity_count('User'))


  def test_when_session_is_present_with_both_user_id_and_id_token_and_auth_type_is_firebase_and_user_already_exists(self):
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    with self.client.session_transaction() as sess:
      sess['gae_uid'] = 'sub'
      sess['gae_token'] = 'token'
    user = self.add_user_entity(uid='sub', name='user', email='email@abc')
    self.firebase_authorize.return_value = claims
    response = self.client.post('/login/?auth_type=firebase')
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(202, response.status_code)
    user_response = User(key_str=data['id'])
    self.assertIsNotNone(user)
    self.assertEquals(data["uId"], user.uid)
    self.assertEquals(data["name"], user.name)
    self.assertEquals(1, self.get_entity_count('User'))
    self.assertEquals(user.key().id, data['id'])


  def test_when_session_is_present_with_both_user_id_and_id_token_and_auth_type_is_auth_0_and_user_does_not_exist(self):
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    with self.client.session_transaction() as sess:
      sess['gae_uid'] = 'sub'
      sess['gae_token'] = 'token'
    self.auth0_authorize.return_value = claims
    response = self.client.post('/login/?auth_type=auth0')
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(202, response.status_code)
    user = User(key_str=data['id'])
    self.assertIsNotNone(user)
    self.assertEquals(data["uId"], user.uid)
    self.assertEquals(data["name"], user.name)
    self.assertEquals(1, self.get_entity_count('User'))


  def test_when_session_is_present_with_both_user_id_and_id_token_and_auth_type_is_auth_0_and_user_already_exists(self):
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    with self.client.session_transaction() as sess:
      sess['gae_uid'] = 'sub'
      sess['gae_token'] = 'token'
    user = self.add_user_entity(uid='sub', name='user', email='email@abc')
    self.auth0_authorize.return_value = claims
    response = self.client.post('/login/?auth_type=auth0')
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(202, response.status_code)
    user_response = User(key_str=data['id'])
    self.assertIsNotNone(user)
    self.assertEquals(data["uId"], user.uid)
    self.assertEquals(data["name"], user.name)
    self.assertEquals(1, self.get_entity_count('User'))
    self.assertEquals(user.key().id, data['id'])


  def test_when_session_is_present_with_both_user_id_and_id_token_and_auth_type_is_not_present_and_user_does_not_exist(self):
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    with self.client.session_transaction() as sess:
      sess['gae_uid'] = 'sub'
      sess['gae_token'] = 'token'
    self.firebase_authorize.return_value = claims
    response = self.client.post('/login/')
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(202, response.status_code)
    user = User(key_str=data['id'])
    self.assertIsNotNone(user)
    self.assertEquals(data["uId"], user.uid)
    self.assertEquals(data["name"], user.name)
    self.assertEquals(1, self.get_entity_count('User'))


  def test_when_session_is_present_with_user_id_and_auth_type_is_not_present(self):
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    with self.client.session_transaction() as sess:
      sess['gae_uid'] = 'sub'
    self.firebase_authorize.return_value = claims
    response = self.client.post('/login/')
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(400, response.status_code)
    self.assertEquals("NO_ID_TOKEN", data["error_message"])
    self.assertEquals(0, self.get_entity_count('User'))

  def test_when_session_is_present_with_id_token_and_auth_type_is_not_present(self):
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {}
    }
    with self.client.session_transaction() as sess:
      sess['gae_token'] = 'token'
    self.firebase_authorize.return_value = claims
    response = self.client.post('/login/')
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(400, response.status_code)
    self.assertEquals("NO USER_ID", data["error_message"])
    self.assertEquals(0, self.get_entity_count('User'))

  def test_when_claims_is_empty_and_auth_type_is_firebase(self):
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b"sub:pass").decode("utf8"))
    }
    claims = {}
    self.firebase_authorize.return_value = claims
    response = self.client.post('/login/', headers=headers)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(401, response.status_code)
    self.assertEquals("EMPTY_CLAIM", data["error_message"])
    self.assertEquals(0, self.get_entity_count('User'))

  def test_when_claims_is_empty_and_auth_type_is_auth0(self):
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b"sub:pass").decode("utf8"))
    }
    claims = {}
    self.auth0_authorize.return_value = claims
    response = self.client.post('/login/?auth_type=auth0', headers=headers)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(401, response.status_code)
    self.assertEquals("EMPTY_CLAIM", data["error_message"])
    self.assertEquals(0, self.get_entity_count('User'))

  def test_for_provider_when_auth_type_is_firebase(self):
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b"sub:pass").decode("utf8"))
    }
    claims = {
        'sub': 'sub',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {'sign_in_provider': 'google'}
    }
    self.firebase_authorize.return_value = claims
    response = self.client.post('/login/?auth_type=firebase', headers=headers)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(202, response.status_code)
    self.assertEquals(data["provider"], 'google')

  def test_for_provider_when_auth_type_is_auth0(self):
    headers = {
        'Authorization': "Basic {}".format(base64.b64encode(b"apple-apple:pass").decode("utf8"))
    }
    claims = {
        'sub': 'apple-apple',
        'name': 'user',
        'email': 'email@abc',
        'firebase': {'sign_in_provider': 'google'}
    }
    self.auth0_authorize.return_value = claims
    response = self.client.post('/login/?auth_type=auth0', headers=headers)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(202, response.status_code)
    self.assertEquals(data["provider"], 'apple')


class VerificationTestCase(BaseAuthUnitTestCase):

  def setUp(self):
    super().setUp()
    self.mock_send_verification_code()
    self.mock_check_verification()
    self.mock_login_callback()
    self.auth_type_json = {'auth_type': 'verify'}

  def tearDown(self):
    self.send_verification_code_patch.stop()
    self.check_verification_patch.stop()
    self.login_callback_patch.stop()
    super().tearDown()

  def test_verification_when_verifying_with_phone_and_verification_code_is_sent(self):
    self.send_verification_code.return_value = "NOT_NONE"
    response = self.client.get("/verification/?phone=1234", json=self.auth_type_json)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(200, response.status_code)
    self.assertEquals('success', data['status'])

  def test_verification_when_verifying_with_phone_and_verification_code_is_not_sent(self):
    self.send_verification_code.return_value = None
    response = self.client.get("/verification/?phone=1234", json=self.auth_type_json)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(400, response.status_code)
    self.assertEquals('Error while sending verification code', data['error_message'])

  def test_verification_when_verifying_with_email_and_verification_code_is_sent(self):
    self.send_verification_code.return_value = "NOT_NONE"
    response = self.client.get("/verification/?email=abcd", json=self.auth_type_json)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(200, response.status_code)
    self.assertEquals('success', data['status'])

  def test_verification_when_verifying_with_email_and_verification_code_is_not_sent(self):
    self.send_verification_code.return_value = None
    response = self.client.get("/verification/?email=abcd", json=self.auth_type_json)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(400, response.status_code)
    self.assertEquals('Error while sending verification code', data['error_message'])

  def test_verification_when_verifying_with_no_method_and_verification_code_is_not_sent(self):
    self.send_verification_code.return_value = None
    response = self.client.get("/verification/", json=self.auth_type_json)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(400, response.status_code)
    self.assertEquals('No phone number or e-mail specified', data['error_message'])

  def test_verification_when_verifying_with_phone_and_correct_code_and_user_does_not_exist(self):
    form_data = {
      'phone': '1234',
      'code': '1234',
      'auth_type': 'verify'
    }
    self.check_verification.return_value = 'success'
    response = self.client.post('/verification/', data=form_data)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(200, response.status_code)
    self.assertIsNotNone(data['token'])
    self.assertEquals('success', data['status'])
    self.assertEquals(1, self.get_entity_count('User'))
    user = User.retrieve(filters=[('token', '=', data['token'])])[0]
    self.assertEquals('1234', user.phone)


  def test_verification_when_verifying_with_phone_and_correct_code_and_user_exists(self):
    form_data = {
      'phone': '1234',
      'code': '1234',
      'auth_type': 'verify'
    }
    user = self.add_user_entity(phone='1234')
    self.check_verification.return_value = 'success'
    response = self.client.post('/verification/', data=form_data)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(200, response.status_code)
    self.assertIsNotNone(data['token'])
    self.assertEquals('success', data['status'])
    self.assertEquals(1, self.get_entity_count('User'))
    user_resp = User.retrieve(filters=[('token', '=', data['token'])])[0]
    self.assertEquals('1234', user_resp.phone)
    self.assertEquals(user.key().id, user_resp.key().id)


  def test_verification_when_verifying_with_phone_and_incorrect_code_and_user_does_not_exist(self):
    form_data = {
      'phone': '1234',
      'code': '1234',
      'auth_type': 'verify'
    }
    self.check_verification.return_value = 'failure'
    response = self.client.post('/verification/', data=form_data)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(400, response.status_code)
    self.assertEquals('Incorrect Code', data['error_message'])
    self.assertEquals(0, self.get_entity_count('User'))

  def test_verification_when_verifying_with_phone_and_incorrect_code_and_user_exists(self):
    form_data = {
      'phone': '1234',
      'code': '1234',
      'auth_type': 'verify'
    }
    user = self.add_user_entity(phone='1234')
    self.check_verification.return_value = 'failure'
    response = self.client.post('/verification/', data=form_data)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(400, response.status_code)
    self.assertEquals('Incorrect Code', data['error_message'])
    self.assertEquals(1, self.get_entity_count('User'))

  def test_verification_when_verifying_with_email_and_correct_code_and_user_does_not_exist(self):
    form_data = {
      'email': '1234',
      'code': '1234',
      'auth_type': 'verify'
    }
    self.check_verification.return_value = 'success'
    response = self.client.post('/verification/', data=form_data)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(200, response.status_code)
    self.assertIsNotNone(data['token'])
    self.assertEquals('success', data['status'])
    self.assertEquals(1, self.get_entity_count('User'))
    user = User.retrieve(filters=[('token', '=', data['token'])])[0]
    self.assertEquals('1234', user.email)
    self.assertIsNone(user.phone)


  def test_verification_when_verifying_with_email_and_correct_code_and_user_exists(self):
    form_data = {
      'email': '1234',
      'code': '1234',
      'auth_type': 'verify'
    }
    user = self.add_user_entity(email='1234', phone=None)
    self.check_verification.return_value = 'success'
    response = self.client.post('/verification/', data=form_data)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(200, response.status_code)
    self.assertIsNotNone(data['token'])
    self.assertEquals('success', data['status'])
    self.assertEquals(1, self.get_entity_count('User'))
    user_resp = User.retrieve(filters=[('token', '=', data['token'])])[0]
    self.assertEquals('1234', user_resp.email)
    self.assertIsNone(user_resp.phone)
    self.assertEquals(user.key().id, user_resp.key().id)


  def test_verification_when_verifying_with_email_and_incorrect_code_and_user_does_not_exist(self):
    form_data = {
      'email': '1234',
      'code': '1234',
      'auth_type': 'verify'
    }
    self.check_verification.return_value = 'failure'
    response = self.client.post('/verification/', data=form_data)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(400, response.status_code)
    self.assertEquals('Incorrect Code', data['error_message'])
    self.assertEquals(0, self.get_entity_count('User'))

  def test_verification_when_verifying_with_email_and_incorrect_code_and_user_exists(self):
    form_data = {
      'email': '1234',
      'code': '1234',
      'auth_type': 'verify'
    }
    user = self.add_user_entity(phone='1234')
    self.check_verification.return_value = 'failure'
    response = self.client.post('/verification/', data=form_data)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(400, response.status_code)
    self.assertEquals('Incorrect Code', data['error_message'])
    self.assertEquals(1, self.get_entity_count('User'))

  def test_verification_when_verifying_with_no_method(self):
    form_data = {
      'code': '1234',
      'auth_type': 'verify'
    }
    response = self.client.post('/verification/', data=form_data)
    data = json.loads(response.get_data(as_text=True))
    self.assertEquals(400, response.status_code)
    self.assertEquals('No Phone Number', data['error_message'])
    self.assertEquals(0, self.get_entity_count('User'))

class ViewsTestCase(BaseAuthUnitTestCase):

  def test_check_for_new_user_with_uid_when_new_user(self):
    with self.tests_app.test_request_context():
      self.tests_app.preprocess_request()
      user = views.check_for_new_user_with_uid(g.app.logger, 'user_id', {'name': 'user', 'email': 'user@cc'}, None)
      self.assertIsNotNone(user)
      self.assertEquals(1, self.get_entity_count('User'))
      self.assertEquals('user_id', user.uid)
      self.assertEquals('user', user.name)

  def test_check_for_new_user_if_device_token_updated_with_uid_when_new_user(self):
    device_token_data = {
      'token': 'test_token',
      'os': 'test_os'}
    with self.tests_app.test_request_context():
      self.tests_app.preprocess_request()
      user = views.check_for_new_user_with_uid(g.app.logger, 'user_id', {'name': 'user', 'email': 'user@cc'}, device_token_data)
      self.assertIsNotNone(user)
      self.assertEquals(1, self.get_entity_count('User'))
      self.assertEquals('user_id', user.uid)
      self.assertEquals('user', user.name)
      self.assertEquals('test_token', user.device_notification_token)
      self.assertEquals('test_os', user.os)

  def test_check_for_new_user_when_existing_user(self):
    with self.tests_app.test_request_context():
      self.tests_app.preprocess_request()
      user = self.add_user_entity(uid='user_id')
      self.assertEquals(1, self.get_entity_count('User'))
      user_resp = views.check_for_new_user_with_uid(g.app.logger, 'user_id', {'name': 'user', 'email': 'user@cc'}, None)
      self.assertIsNotNone(user)
      self.assertEquals(1, self.get_entity_count('User'))
      self.assertEquals(user.key().id, user_resp.key().id)
      self.assertEquals('user_id', user_resp.uid)
      self.assertEquals('user', user_resp.name)

  def test_check_for_new_user_if_device_token_updated_when_existing_user(self):
    device_token_data = {
      'token': 'test_token',
      'os': 'test_os'}
    with self.tests_app.test_request_context():
      self.tests_app.preprocess_request()
      user = self.add_user_entity(uid='user_id')
      self.assertEquals(1, self.get_entity_count('User'))
      user_resp = views.check_for_new_user_with_uid(g.app.logger, 'user_id', {'name': 'user', 'email': 'user@cc'}, device_token_data)
      self.assertIsNotNone(user)
      self.assertEquals(1, self.get_entity_count('User'))
      self.assertEquals(user.key().id, user_resp.key().id)
      self.assertEquals('user_id', user_resp.uid)
      self.assertEquals('user', user_resp.name)
      self.assertEquals('test_token', user_resp.device_notification_token)
      self.assertEquals('test_os', user_resp.os)

  def test_check_for_new_user_with_phone_or_email_with_phone_or_email_when_new_user_and_method_is_phone(self):
    user = self.add_user_entity(phone='0183409112', token='abc')
    with self.tests_app.test_request_context():
      self.tests_app.preprocess_request()
      result = views.check_for_new_user_with_phone_or_email(
          g.app.logger, '0183409', None, None)
      self.assertIsNotNone(result)
      self.assertEquals('0183409', result.phone)
      self.assertEquals(0, result.role)

  def test_check_for_new_user_with_phone_or_email_with_phone_or_email_when_new_user_and_method_is_email(self):
    user = self.add_user_entity(email='email123@abc.com', token='abc')
    with self.tests_app.test_request_context():
      self.tests_app.preprocess_request()
      result = views.check_for_new_user_with_phone_or_email(g.app.logger, None, 'email@abc.com', None)
      self.assertIsNotNone(result)
      self.assertEquals('email@abc.com', result.email)
      self.assertEquals(0, result.role)

  def test_check_for_new_user_when_new_user_and_method_is_None(self):
    with self.tests_app.test_request_context():
      self.tests_app.preprocess_request()
      result = views.check_for_new_user_with_phone_or_email(g.app.logger, None, None, None)
      self.assertIsNone(result)

  def test_check_for_new_user_with_phone_or_email_when_existing_user_and_method_is_phone(self):
    user = self.add_user_entity(phone='0183409', token='abc')
    with self.tests_app.test_request_context():
      self.tests_app.preprocess_request()
      result = views.check_for_new_user_with_phone_or_email(g.app.logger, '0183409', None, None)
      self.assertIsNotNone(result)
      self.assertEquals('0183409', result.phone)
      self.assertEquals(user.key().id, result.key().id)
      self.assertNotEquals(user.token, result.token)

  def test_check_for_new_user_with_phone_or_email_when_existing_user_and_method_is_email(self):
    user = self.add_user_entity(email='email@abc.com', token='abc')
    with self.tests_app.test_request_context():
      self.tests_app.preprocess_request()
      result = views.check_for_new_user_with_phone_or_email(g.app.logger, None, 'email@abc.com', None)
      self.assertIsNotNone(result)
      self.assertEquals('email@abc.com', result.email)
      self.assertEquals(user.key().id, result.key().id)
      self.assertNotEquals(user.token, result.token)

  def test_check_for_new_user_with_phone_or_email_if_device_token_updated_when_existing_user_and_method_is_email(self):
    user = self.add_user_entity(email='email@abc.com', token='abc')
    device_token_data = {
      'token': 'test_token',
      'os': 'test_os'}
    with self.tests_app.test_request_context(json={'device_token_data': device_token_data}):
      self.tests_app.preprocess_request()
      result = views.check_for_new_user_with_phone_or_email(g.app.logger, None, 'email@abc.com', device_token_data)
      self.assertIsNotNone(result)
      self.assertEquals('email@abc.com', result.email)
      self.assertEquals(user.key().id, result.key().id)
      self.assertEquals(result.os, 'test_os')
      self.assertEquals(result.device_notification_token, 'test_token')
      self.assertNotEquals(user.token, result.token)
  
  def test_check_for_new_user_with_phone_or_email_if_device_token_updated_when_existing_user_and_method_is_phone(self):
    user = self.add_user_entity(phone='12345', token='abc')
    device_token_data = {
      'token': 'test_token',
      'os': 'test_os'}
    with self.tests_app.test_request_context(json={'device_token_data': device_token_data}):
      self.tests_app.preprocess_request()
      result = views.check_for_new_user_with_phone_or_email(g.app.logger, '12345', None, device_token_data)
      self.assertIsNotNone(result)
      self.assertEquals('12345', result.phone)
      self.assertEquals(user.key().id, result.key().id)
      self.assertEquals(result.os, 'test_os')
      self.assertEquals(result.device_notification_token, 'test_token')
      self.assertNotEquals(user.token, result.token)

  def test_check_for_new_user_with_phone_or_email_if_device_token_updated_when_not_existing_user_and_method_is_email(self):
    device_token_data = {
      'token': 'test_token',
      'os': 'test_os'}
    with self.tests_app.test_request_context(json={'device_token_data': device_token_data}):
      self.tests_app.preprocess_request()
      result = views.check_for_new_user_with_phone_or_email(g.app.logger, None, 'email@abc.com', device_token_data)
      self.assertIsNotNone(result)
      self.assertEquals('email@abc.com', result.email)
      self.assertEquals(result.os, 'test_os')
      self.assertEquals(result.device_notification_token, 'test_token')
  
  def test_check_for_new_user_with_phone_or_email_if_device_token_updated_when_not_existing_user_and_method_is_phone(self):
    device_token_data = {
      'token': 'test_token',
      'os': 'test_os'}
    with self.tests_app.test_request_context(json={'device_token_data': device_token_data}):
      self.tests_app.preprocess_request()
      result = views.check_for_new_user_with_phone_or_email(g.app.logger, '12345', None, device_token_data)
      self.assertIsNotNone(result)
      self.assertEquals('12345', result.phone)
      self.assertEquals(result.os, 'test_os')
      self.assertEquals(result.device_notification_token, 'test_token')

  def test_check_for_new_user_with_phone_or_email_for_profile_picture_when_not_existing_user(self):
    with self.tests_app.test_request_context():
      self.tests_app.preprocess_request()
      result = views.check_for_new_user_with_phone_or_email(g.app.logger, '12345', None, None)
      self.assertIsNotNone(result)
      self.assertEquals('12345', result.phone)
      self.assertEquals('https://storage.googleapis.com/crypticcup-images/default_profile.jpg', result.picture)

  def test_check_for_new_user_with_phone_or_email_for_profile_picture_when_existing_user(self):
    user = self.add_user_entity(phone='12345', token='abc', picture='picture@')
    with self.tests_app.test_request_context():
      self.tests_app.preprocess_request()
      result = views.check_for_new_user_with_phone_or_email(g.app.logger, '12345', None, None)
      self.assertIsNotNone(result)
      self.assertEquals('12345', result.phone)
      self.assertEquals('picture@', result.picture)

  def test_check_for_new_user_when_auth_type_is_verify(self):
    self.mock_check_for_new_user_with_phone_or_email()
    self.mock_check_for_new_user_with_uid()
    with self.tests_app.test_request_context('/url/?auth_type=verify'):
      self.tests_app.preprocess_request()
      views.check_for_new_user(g.app.logger)
      self.assertTrue(self.check_for_new_user_with_phone_or_email.called)
      self.assertFalse(self.check_for_new_user_with_uid.called)
    self.check_for_new_user_with_phone_or_email_patch.stop()
    self.check_for_new_user_with_uid_patch.stop()

  def test_check_for_new_user_when_auth_type_is_not_verify(self):
    self.mock_check_for_new_user_with_phone_or_email()
    self.mock_check_for_new_user_with_uid()
    with self.tests_app.test_request_context():
      self.tests_app.preprocess_request()
      views.check_for_new_user(g.app.logger)
      self.assertFalse(self.check_for_new_user_with_phone_or_email.called)
      self.assertTrue(self.check_for_new_user_with_uid.called)
    self.check_for_new_user_with_phone_or_email_patch.stop()
    self.check_for_new_user_with_uid_patch.stop()



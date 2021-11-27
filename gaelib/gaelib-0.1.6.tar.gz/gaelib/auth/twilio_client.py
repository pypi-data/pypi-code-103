from twilio.rest import Client
from gaelib.env import get_twilio_account_sid, get_twilio_auth_token, get_twilio_verification_sid
from gaelib.utils.web import app


class TwilioClient():
  __client__ = None

  @classmethod
  def get_client(self):
    # To maintain Singleton State of the Client
    if self.__client__ == None:
      self.__client__ = Client(app.config.get(
          'ACCOUNT_SID'), app.config.get('AUTH_TOKEN'))
    return self.__client__

  @classmethod
  def send_verification_code(self, to, channel):
    service = app.config.get('VERIFICATION_SID')
    client = self.get_client()
    verification = client.verify \
        .services(service) \
        .verifications \
        .create(to=to, channel=channel)
    return verification.sid

  @classmethod
  def check_verification(self, phone, code):
    service = app.config.get('VERIFICATION_SID')
    client = self.get_client()
    try:
      verification_check = client.verify \
          .services(service) \
          .verification_checks \
          .create(to=phone, code=code)
    except:
      return 'failure'
    return 'success' if verification_check.status == 'approved' else 'failure'

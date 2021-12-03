import base64
from . import *

# Create the logger for the SDK
import logging, sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.Logger('NG_SDK')

logger_handler = logging.StreamHandler()
log.addHandler(logger_handler)
logger_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))


class Authenticator:
    def __init__(self):
        self.token = TOKEN
        self.login = LOGIN
        self.password = PASSWORD

    def get_token(self):
        if self.token is not None:
            log.debug('Authentication with Web Token ...')
            return {'Authorization': f'Bearer {self.token}'}

        else:
            if self.login is not None and self.password is not None:
                log.debug('Authentication with Credentials ...')
                credentials = self.login + ":" + self.password
                message_bytes = credentials.encode('ascii')
                base64_enc = base64.b64encode(message_bytes).decode('UTF-8')

                d = {'Authorization': f"Basic {base64_enc}"}
                return d

            else:
                log.error('No login or password provided, neither token can be read form environment variable.')
                raise Exception('Authentication issue : no credentials found')

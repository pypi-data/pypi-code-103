import os

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS')
assert ALLOWED_HOSTS


class Connector(object):

    @classmethod
    def _build_header(cls):
        return {
            'Content-Type': 'application/json',
            'Accept': '*/*'
        }

    @classmethod
    def say_hello(cls):
        print("Welcome to Blank package!")

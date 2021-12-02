""" A collection of helpers for testing. """
from base64 import b64encode


def basic_auth_authorization_header(username, password):
    """ Generate the basic auth header from the username and password. """
    auth_string = b64encode(b":".join((username.encode('latin1'), password.encode('latin1')))).decode()
    return {"Authorization": "Basic {}".format(auth_string)}

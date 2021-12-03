from getpass import getpass

import numpy
import requests
from oka.config import default_url, default_user, default_password

from .client import Oka


def toy_df():
    from idict import idict

    return idict.fromtoy(output_format="df")["df"]


def j(r):
    """Helper function needed because flask test_client() provide json as a property(?), not as a method."""
    return r.json() if callable(r.json) else r.json


def generate_token(url=default_url):
    data = {
        "username": default_user or input("Username to connect to OKA: "),
        "password": default_password or getpass("Password to connect to OKA: "),
    }
    response = requests.post(f"{url}/api/auth/login", json=data)
    if response and "access_token" in j(response):
        return j(response)["access_token"]
    raise Exception("[Error] Authentication failed.")


def new_data(**kwargs):
    from aiuna import new

    for l in list(kwargs):
        if isinstance(kwargs[l], list):
            if not isinstance(kwargs[l][0], list):
                kwargs[l] = [[str(v)] for v in kwargs[l]]
            kwargs[l] = numpy.array(kwargs[l])
        metafield_d = f"{l.upper()}d"
        metafield_t = f"{l.upper()}t"
        if metafield_t not in kwargs:
            if len(kwargs[l].shape) > 1 and kwargs[l].shape[1] > 1:
                kwargs[metafield_d] = [f"{l}{i}" for i in range(len(kwargs[l][0]))]
                kwargs[metafield_t] = [f"real" for _ in kwargs[l][0]]
            else:
                kwargs[metafield_d] = [f"{l}{0}"]
                kwargs[metafield_t] = [list(set([str(v[0]) for v in kwargs[l]]))]
    return new(**kwargs)

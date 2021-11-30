from typing import Optional

from hoss.error import *
from hoss.namespace import Namespace
from hoss.core import CoreService
from hoss.auth import AuthService

import urllib.parse


def connect(server_url: str, auth_instance: Optional[AuthService] = None) -> CoreService:
    return CoreService(server_url, auth_instance)


def resolve(uri, auth_instance: Optional[AuthService] = None):
    uri = urllib.parse.urlparse(uri)

    if not uri.scheme.lower().startswith("hoss"):
        raise ValueError("URI is not a valid Hoss URI")

    try:
        _, protocol = uri.scheme.lower().split("+")
        host, namespace_name, dataset_name = uri.netloc.split(":")
    except:
        raise ValueError("URI is not a valid Hoss URI")

    s = CoreService(f"{protocol}://{host}", auth_instance=auth_instance)
    ns = s.get_namespace(namespace_name)

    return ns.get_dataset(dataset_name) / uri.path

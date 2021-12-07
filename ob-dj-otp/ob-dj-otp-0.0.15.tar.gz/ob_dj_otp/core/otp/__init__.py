import importlib
import typing

default_app_config = "ob_dj_otp.core.otp.apps.OTPConfig"


def import_str_to_object(object_path: typing.Text):
    """  import_str_to_object takes full path of a python object
    the function will attempt to import the object and return it
    uninitiated
    """
    klass = object_path.split(".")[-1]
    path = ".".join(object_path.split(".")[:-1])
    module = importlib.import_module(path)
    return getattr(module, klass)

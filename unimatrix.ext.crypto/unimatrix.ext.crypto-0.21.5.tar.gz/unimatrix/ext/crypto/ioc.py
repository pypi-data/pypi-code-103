# pylint: skip-file
import ioc

from .secret import get_signer


def setup_ioc(*args, **kwargs):
    ioc.provide('ApplicationSigner', get_signer())

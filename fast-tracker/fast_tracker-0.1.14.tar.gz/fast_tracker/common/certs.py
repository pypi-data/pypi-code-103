# -*- coding: utf-8 -*-

import os


def where():
    return os.path.join(os.path.dirname(__file__), 'cacert.pem')

# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 14:39:17 2019

@author: chris.kerklaan
"""


def show_console_logging(level="INFO"):
    import logging
    import sys

    if level == "INFO":
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    if level == "DEBUG":
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

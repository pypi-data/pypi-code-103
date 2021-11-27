# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

import logging
from sweetrpg_model_core.model.base import Model


class AuthorVolume(Model):
    """A model object representing the link between author and volume."""

    def __init__(self, *args, **kwargs):
        """Creates a new AuthorVolume object.

        :key str author: The identifier of the Author.
        :key str volume: The identifier of the Volume.
        """
        logging.debug("args: %s, kwargs: %s", args, kwargs)

        super().__init__(*args, **kwargs)

        self.author = kwargs["author"]
        self.volume = kwargs["volume"]

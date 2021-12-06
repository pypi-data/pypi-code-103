# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

import logging
from sweetrpg_model_core.model.base import Model


class Author(Model):
    """A model object representing RPG authors."""

    def __init__(self, *args, **kwargs):
        """Creates a new Author object.

        :key str name: The name of the author.
        """
        logging.debug("args: %s, kwargs: %s", args, kwargs)
        print(kwargs)  # TODO: remove

        super().__init__(*args, **kwargs)

        self.name = kwargs.get("name")
        self.properties = kwargs.get("properties")
        self.tags = kwargs.get("tags")
        # volumes: see AuthorVolume
        # studios: see StudioAuthor

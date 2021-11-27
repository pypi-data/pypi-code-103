# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

import logging
from sweetrpg_model_core.model.base import EmbeddedModel


class VolumeProperty(EmbeddedModel):
    """A model object representing a property key/value pair for a Volume."""

    def __init__(self, *args, **kwargs):
        """ """
        logging.debug("args: %s, kwargs: %s", args, kwargs)

        super().__init__(*args, **kwargs)

        self.name = kwargs.get("name")
        self.kind = kwargs.get("kind")
        self.value = kwargs.get("value")

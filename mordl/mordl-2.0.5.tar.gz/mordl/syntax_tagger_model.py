# -*- coding: utf-8 -*-
# MorDL project: Syntax tagger model
#
# Copyright (C) 2020-present by Sergei Ternovykh
# License: BSD, see LICENSE for details
"""
Provides a model for syntax MorDL tagger.
"""
from mordl.base_model import BaseModel
from mordl.base_tagger_model import BaseTaggerModel
from mordl.defaults import CONFIG_ATTR


class SyntaxTaggerModel(BaseModel):

    def __init__(self, upos_model, feats_model, lemma_model):
        
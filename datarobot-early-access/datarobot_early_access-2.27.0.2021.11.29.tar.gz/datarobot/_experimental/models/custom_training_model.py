#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from datarobot.models.custom_model import _CustomModelBase


class CustomTrainingModel(_CustomModelBase):
    _model_type = "training"

# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from typing import List
from marshmallow import Schema, fields, post_dump, post_load

from ibm_wos_utils.explainability.entity.constants import ExplanationType


class FeatureRange():
    def __init__(self, min: str = None, min_inclusive: bool = None, max: str = None, max_inclusive: bool = None):
        self.min = min
        self.min_inclusive = min_inclusive
        self.max = max
        self.max_inclusive = max_inclusive


class ExplanationFeature():
    def __init__(self, feature_name: str = None, weight: str = None, feature_range: FeatureRange = None, feature_value: str = None, importance: str = None, positions: List = None):
        self.feature_name = feature_name
        self.weight = weight
        self.feature_range = feature_range
        self.feature_value = feature_value
        self.importance = importance
        self.positions = positions


class Prediction():
    def __init__(self, value: str, explanation_features: List[ExplanationFeature] = [], probability=None):
        self.value = value
        self.probability = probability
        self.explanation_features = explanation_features


class LimeExplanation():
    def __init__(self, predictions=None, error=None):
        self.explanation_type = ExplanationType.LIME.value
        self.predictions = predictions
        self.error = error


class ErrorTarget:
    def __init__(self, error_type, error_name):
        self.type = error_type
        self.name = error_name


class Error():
    def __init__(self, code, message, vals=[], target=None):
        self.code = code
        self.message = message
        self.vals = vals
        self.target = target


class BaseResponseSchema(Schema):

    def value_exist(self, value):
        if type(value) in [bool, int, float]:
            return True
        if value:
            return True
        return False


class FeatureRangeSchema(BaseResponseSchema):
    min = fields.String()
    min_inclusive = fields.Boolean()
    max = fields.String()
    max_inclusive = fields.Boolean()

    @post_load
    def create_feature_range(self, data):
        return FeatureRange(**data)


class ExplanationFeatureSchema(BaseResponseSchema):
    feature_name = fields.String()
    weight = fields.Number()
    feature_range = fields.Nested(FeatureRangeSchema)
    feature_value = fields.String()
    importance = fields.String()
    positions = fields.List(fields.Raw())

    @post_load
    def create_explanation_feature(self, data):
        return ExplanationFeature(**data)


class PredictionSchema(BaseResponseSchema):
    value = fields.String()
    probability = fields.Number()
    explanation_features = fields.List(fields.Nested(ExplanationFeatureSchema))

    @post_load
    def create_prediction(self, data):
        return Prediction(**data)


class ErrorTargetSchema(BaseResponseSchema):
    type = fields.String()
    name = fields.String()


class ErrorSchema(BaseResponseSchema):
    code = fields.String()
    message = fields.String()
    vals = fields.List(fields.String())
    target = fields.Nested(ErrorTargetSchema)


class LimeExplanationSchema(BaseResponseSchema):
    explanation_type = fields.String()
    predictions = fields.List(fields.Nested(PredictionSchema))
    error = fields.Nested(ErrorSchema)

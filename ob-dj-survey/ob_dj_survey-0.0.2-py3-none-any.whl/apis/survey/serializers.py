import logging
import typing

from rest_framework import serializers

from ob_dj_survey.apis.user.serializers import UserSerializer
from ob_dj_survey.core.survey.models import (
    Survey,
    SurveyCategory,
    SurveyChoice,
    SurveyQuestion,
    SurveyResponse,
    SurveySection,
)

logger = logging.getLogger(__name__)


class SurveyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyCategory
        fields = ("pk", "name", "created_at")


class SurveySectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveySection
        fields = ("pk", "name", "description", "category", "created_at")

    def to_representation(self, instance) -> typing.Dict:
        data = super().to_representation(instance)
        data["category"] = SurveyCategorySerializer(instance.category).data
        return data


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = (
            "pk",
            "section",
            "created_at",
        )

    def to_representation(self, instance) -> typing.Dict:
        data = super().to_representation(instance)
        data["section"] = SurveySectionSerializer(instance.section).data
        return data


class SurveyChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyChoice
        fields = ("pk", "title", "question", "created_at")

    def to_representation(self, instance) -> typing.Dict:
        data = super().to_representation(instance)
        data["question"] = SurveyQuestionSerializer(instance.question).data
        return data


class SurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyResponse
        fields = (
            "pk",
            "survey",
            "question",
            "choice",
            "status",
            "value",
            "created_by",
            "created_at",
            "updated_at",
        )

    def to_representation(self, instance) -> typing.Dict:
        data = super().to_representation(instance)
        data["survey"] = SurveySerializer(instance.survey).data
        data["question"] = SurveyQuestionSerializer(instance.question).data
        data["choice"] = SurveyChoiceSerializer(instance.choice).data
        data["created_by"] = UserSerializer(instance.created_by).data
        return data


class SurveyQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestion
        fields = (
            "pk",
            "title",
            "type",
            "survey",
            "is_active",
            "created_at",
        )

import typing

from django.db import models

if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model as User

    from ob_dj_survey.core.survey.models import (  # noqa
        Survey,
        SurveyAnswers,
        SurveyChoice,
        SurveyQuestion,
        SurveyResponse,
    )


class SurveyManager(models.Manager):
    def create(self, *args: typing.Any, **kwargs: typing.Any) -> "Survey":
        return super().create(*args, **kwargs)

    def active(self) -> models.QuerySet["Survey"]:
        return self.filter(questions__is_active=True)


class SurveyQuestionManager(models.Manager):
    def active(self) -> models.QuerySet["SurveyQuestion"]:
        return self.filter(is_active=True)


class SurveyAnswersManager(models.Manager):
    def create(
        self,
        survey: "Survey",
        created_by: "User",
        answers: typing.List["SurveyChoice"] = [],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> "SurveyAnswers":
        instance = super().create(survey=survey, created_by=created_by, *args, **kwargs)
        instance.submit(answers=answers)
        return instance


class SurveyResponseManager(models.Manager):
    def create(self, *args: typing.Any, **kwargs: typing.Any,) -> "SurveyResponse":
        return super().create(*args, **kwargs)

import typing

from django.db import models

if typing.TYPE_CHECKING:
    from ob_dj_survey.core.survey.models import Survey, SurveyResponse


class SurveyManager(models.Manager):
    def create(self, *args: typing.Any, **kwargs: typing.Any) -> "Survey":
        return super().create(*args, **kwargs)

    def active(self) -> models.QuerySet["Survey"]:
        return self.filter(questions__is_active=True)


class SurveyQuestionManager(models.Manager):
    def active(self) -> models.QuerySet["SurveyQuestion"]:
        return self.filter(is_active=True)


class SurveyResponseManager(models.Manager):
    def create(
        self,
        survey: "Survey",
        answers: typing.List["SurveyChoice"],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> "SurveyResponse":
        # TODO: For Later
        # instance.submit(answers=answers)
        return super().create(survey=survey, *args, **kwargs)

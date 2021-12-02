import typing

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ob_dj_survey.core.survey.managers import (
    SurveyManager,
    SurveyQuestionManager,
    SurveyResponseManager,
)


class SurveyCategory(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)


class SurveySection(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(
        SurveyCategory, on_delete=models.CASCADE, related_name="sections"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.__class__.__name__}(PK={self.pk}, Section={self.name})"


class Survey(models.Model):
    section = models.ForeignKey(
        SurveySection, on_delete=models.CASCADE, related_name="surveys"
    )
    callback = models.JSONField(
        null=True,
        blank=True,
        help_text=_(
            "The callback field is used to maintain callback to other apps "
            "(For example, if survey medical_record require to callback another app and pass "
            "survey response parameters)"
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = SurveyManager()

    def __str__(self):
        return f"{self.__class__.__name__}(PK={self.pk}, Survey={self.section})"


class SurveyQuestion(models.Model):
    class QuestionTypes(models.TextChoices):
        TEXT = "text", _("text (multiple line)")
        SHORT_TEXT = "short-text", _("short text (one line)")
        RADIO = "radio", _("radio")
        YES_NO = "yes_no", _("Yes/No")
        SELECT = "select", _("select")
        SELECT_IMAGE = "select_image", _("Select Image")
        SELECT_MULTIPLE = "select_multiple", _("Select Multiple")
        INTEGER = "integer", _("integer")
        FLOAT = "float", _("float")
        DATE = "date", _("date")

    title = models.CharField(max_length=200)
    type = models.CharField(
        max_length=100, choices=QuestionTypes.choices, default=QuestionTypes.RADIO.value
    )
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name="questions"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = SurveyQuestionManager()

    def __str__(self):
        return f"{self.__class__.__name__}(PK={self.pk}, Question={self.title})"

    def activate(self) -> typing.NoReturn:
        if self.is_active:
            raise ValidationError(_("Survey question is already active"))

        if (
            self.type
            in (
                self.QuestionTypes.SELECT.value
                or self.QuestionTypes.SELECT_MULTIPLE.value
            )
            and self.choices.count() < 1
        ):
            raise ValidationError(
                _("Please add minimum of 2 choices for survey question")
            )

        self.is_active = True
        self.save()


class SurveyChoice(models.Model):
    title = models.CharField(max_length=200)
    question = models.ForeignKey(
        SurveyQuestion, on_delete=models.CASCADE, related_name="choices"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.__class__.__name__}(" f"PK={self.pk}, " f"Choice={self.title})"


class SurveyResponse(models.Model):
    class Status(models.TextChoices):
        COMPLETED = "completed", _("Completed")
        PARTIAL = "partial", _("Partial")

    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name="responses"
    )
    question = models.ForeignKey(
        SurveyQuestion, on_delete=models.CASCADE, related_name="responses"
    )
    choice = models.ForeignKey(
        SurveyChoice,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="responses",
    )
    status = models.CharField(max_length=10, choices=Status.choices)
    value = models.TextField()
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SurveyResponseManager()

    def __str__(self):
        return f"{self.__class__.__name__}(PK={self.pk})"

    def clean(self) -> None:
        if self.question.type in [
            self.question.QuestionTypes.SELECT.value,
            self.question.QuestionTypes.SELECT_MULTIPLE.value,
            self.question.QuestionTypes.RADIO.value,
        ] and self.value not in self.question.choices.values_list("value", flat=True):
            raise ValidationError(
                _(
                    f"The answer {self.value} for question {self.question.title} is invalid choice"
                )
            )

        if self.question.type == self.question.QuestionTypes.YES_NO.value and self.value.lower() not in (
            "yes",
            "no",
        ):
            raise ValidationError(
                _(f"The answer for {self.question.title} can accept yes/no values")
            )

    def submit(self, answers: typing.List["SurveyChoice"]) -> typing.NoReturn:
        validated_answers = []
        for answer in answers:
            # If Answer Object is Dict
            if isinstance(answer, dict):
                answer = self.choice.model(**answer)
            setattr(answer, "question", self.question)
            answer.clean()
            validated_answers.append(answer)

        self.answers.bulk_create(validated_answers)

        if self.survey.questions.count() == self.answers.count() and (
            self.survey.validators == self.Status.COMPLETED.value
            or self.Status.PARTIAL.value
        ):
            self.status = self.Status.COMPLETED
        elif self.survey.questions.count() != self.answers.count() and (
            self.survey.validators == self.Status.PARTIAL.value
        ):
            self.status = self.Status.PARTIAL

        self.save()

from django.contrib import admin

from ob_dj_survey.core.survey.models import (
    Survey,
    SurveyCategory,
    SurveyChoice,
    SurveyQuestion,
    SurveyResponse,
    SurveySection,
)


class SurveyQuestionInlineAdmin(admin.TabularInline):
    model = SurveyQuestion
    extra = 0


class SurveySectionInlineAdmin(admin.TabularInline):
    model = SurveySection
    extra = 0


class SurveyCategoryInlineAdmin(admin.TabularInline):
    model = SurveyCategory
    extra = 0


class SurveyInlineAdmin(admin.TabularInline):
    model = Survey
    extra = 0


class SurveyChoiceInlineAdmin(admin.TabularInline):
    model = SurveyChoice
    extra = 0


class SurveyResponseInlineAdmin(admin.TabularInline):
    model = SurveyResponse
    extra = 0


@admin.register(SurveyCategory)
class SurveyCategoryAdmin(admin.ModelAdmin,):
    fieldsets = ((None, {"fields": ("name",)},),)
    list_display = ["name", "created_at"]
    inlines = [
        SurveySectionInlineAdmin,
    ]


@admin.register(SurveySection)
class SurveySectionAdmin(admin.ModelAdmin,):
    list_display = ["name", "description", "created_at"]
    fieldsets = ((None, {"fields": ("name", "description", "category",)},),)
    inlines = [SurveyInlineAdmin]


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin,):
    fieldsets = ((None, {"fields": ("section",)},),)
    list_display = ["section", "created_at"]
    inlines = [SurveyResponseInlineAdmin, SurveyQuestionInlineAdmin]


@admin.register(SurveyChoice)
class SurveyChoiceAdmin(admin.ModelAdmin,):
    fieldsets = ((None, {"fields": ("title", "question")},),)
    list_display = ["title", "created_at"]
    inlines = [SurveyResponseInlineAdmin]


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin,):
    fieldsets = ((None, {"fields": ("title", "type", "survey", "is_active")},),)
    list_display = ["title", "type", "is_active", "created_at"]
    inlines = [SurveyChoiceInlineAdmin, SurveyResponseInlineAdmin]


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin,):
    list_display = ["status", "value", "created_by", "updated_at", "created_at"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "survey",
                    "question",
                    "choice",
                    "status",
                    "value",
                    "created_by",
                )
            },
        ),
    )

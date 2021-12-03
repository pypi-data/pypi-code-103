from django.contrib import admin
from .models import TestLoggerUserModel, RequestLoggerModel, TestLoggerModel
from simple_history.admin import SimpleHistoryAdmin


# Register your models here.


class TestLoggerUserAdminModel(SimpleHistoryAdmin):
    history_list_display = ["changed_by"]
    search_fields = ['question', 'user__username']


class RequestLoggerAdminModel(SimpleHistoryAdmin):
    history_list_display = ["remote_address", "user__username", "response_code", "date", "body_request"]
    search_fields = ['endpoint', 'user__username']


class TestLoggerAdminModel(SimpleHistoryAdmin):
    history_list_display = ["question", "pub_date"]
    search_fields = ['question']


admin.site.register(TestLoggerUserModel, TestLoggerUserAdminModel)
admin.site.register(RequestLoggerModel, RequestLoggerAdminModel)
admin.site.register(TestLoggerModel, TestLoggerAdminModel)

from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords


class TestLoggerUserModel(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value


class TestLoggerModel(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    history = HistoricalRecords()


class RequestLoggerModel(models.Model):
    endpoint = models.CharField(max_length=100, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    response_code = models.PositiveSmallIntegerField()
    method = models.CharField(max_length=10, null=True)
    remote_address = models.CharField(max_length=20, null=True)
    exec_time = models.IntegerField(null=True)
    date = models.DateTimeField(auto_now=True)
    body_response = models.TextField()
    body_request = models.TextField()
    history = HistoricalRecords()

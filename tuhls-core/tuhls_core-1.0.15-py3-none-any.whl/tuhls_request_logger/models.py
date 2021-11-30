from django.db import models

from tuhls_core.models import CustomModel


class Request(CustomModel):
    user = models.UUIDField()
    method = models.CharField(max_length=8)
    status = models.IntegerField()
    ip = models.CharField(max_length=16)
    request_data = models.CharField(max_length=8192)
    response_data = models.CharField(max_length=8192)

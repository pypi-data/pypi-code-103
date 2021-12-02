from django.db import models
from django.contrib.gis.db.models import MultiPolygonField


class Place(models.Model):
    geoid = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    geom = MultiPolygonField()

    parent = models.ForeignKey('self', related_name='places', on_delete=models.CASCADE, null=True)

    class Type(models.IntegerChoices):
        state = 0
        county = 1
        city = 2
        tract = 3

    type = models.IntegerField(choices=Type.choices)

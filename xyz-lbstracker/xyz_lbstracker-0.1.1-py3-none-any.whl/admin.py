from django.contrib import admin

from . import models


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('create_time', 'mobile', 'memo', 'user')
    raw_id_fields = ('user',)
    search_fields = ("mobile", "memo")


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('create_time', 'event', 'longitude', 'latitude', 'address')
    raw_id_fields = ('event',)
    search_fields = ("address", )

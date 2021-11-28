from django.contrib import admin

from . import models


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('create_time', 'name', 'memo', 'user')
    raw_id_fields = ('user',)
    search_fields = ("name", "memo")


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('create_time', 'event', 'longitude', 'latitude', 'address')
    raw_id_fields = ('event',)
    search_fields = ("address", )

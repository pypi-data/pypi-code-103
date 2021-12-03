from django.contrib import admin

from wcd_geo_db.modules.bank.db import Geometry


@admin.register(Geometry)
class GeometryAdmin(admin.ModelAdmin):
    list_display = 'id', 'location',
    search_fields = 'id',

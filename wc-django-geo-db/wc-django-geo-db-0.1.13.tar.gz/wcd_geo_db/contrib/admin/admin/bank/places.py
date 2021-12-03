from django.contrib import admin

from wcd_geo_db.modules.bank.db import Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'types', 'route', 'grouping', 'division'
    # list_filter = 'division',
    search_fields = 'name', 'division__name', 'grouping__name'
    list_select_related = 'route', 'grouping', 'division'

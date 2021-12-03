from django.contrib import admin

from wcd_geo_db.modules.bank.db import Route


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'types'
    # list_filter = 'division',
    search_fields = 'name', 'division__name', 'grouping__name'
    list_select_related = 'grouping', 'division'

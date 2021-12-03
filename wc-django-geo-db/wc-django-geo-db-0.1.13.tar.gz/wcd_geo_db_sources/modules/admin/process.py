from django.contrib import admin
from django.contrib import messages
from django.utils.translation import pgettext_lazy, pgettext

from wcd_geo_db_sources.modules.process.cases import rerun_state
from wcd_geo_db_sources.modules.process.models import (
    ProcessState, ProcessSourceConfig
)


@admin.action(
    description=pgettext_lazy(
        'wcd_geo_db_sources:process', 'Rerun process'
    )
)
def rerun_process(modeladmin, request, queryset):
    if queryset.count() != 1:
        return modeladmin.message_user(
            request,
            pgettext(
                'wcd_geo_db_sources:process',
                'There could be only one process to rerun.'
            ),
            messages.ERROR
        )

    state = queryset.may_rerun().first()

    if state is None:
        return modeladmin.message_user(
            request,
            pgettext(
                'wcd_geo_db_sources:process',
                'Can\'t rerun this process.'
            ),
            messages.ERROR
        )

    return rerun_state(state)


@admin.register(ProcessState)
class ProcessStateAdmin(admin.ModelAdmin):
    list_display = 'id', 'source', 'status', 'stage',
    list_filter = 'status',
    search_fields = 'source', 'status', 'stage', 'state'

    actions = [rerun_process]


@admin.register(ProcessSourceConfig)
class ProcessSourceConfigAdmin(admin.ModelAdmin):
    list_display = 'id', 'source',
    list_filter = 'source',
    search_fields = 'source', 'config',

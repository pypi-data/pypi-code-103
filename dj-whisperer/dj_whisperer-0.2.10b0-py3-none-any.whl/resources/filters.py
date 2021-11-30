import sys

from whisperer.models import Webhook, WebhookEvent

if sys.version_info.major == 3:
    from django_filters import FilterSet, filters

    class WebhookFilterPY3(FilterSet):
        target_url = filters.CharFilter(field_name="target_url", lookup_expr="iexact")
        event_type = filters.CharFilter(field_name="event_type", lookup_expr="iexact")
        is_active = filters.BooleanFilter(field_name="is_active")

        class Meta:
            model = Webhook
            fields = ('target_url', 'is_active', 'event_type')

    class WebhookEventFilterPY3(FilterSet):
        event_type = filters.CharFilter(
            field_name='webhook__event_type', lookup_expr='iexact'
        )
        created_date = filters.DateFilter(
            field_name='created_date', lookup_expr='__all__'
        )
        delivered = filters.BooleanFilter(field_name="delivered")

        class Meta:
            model = WebhookEvent
            fields = (
                'uuid',
                'event_type',
                'response_http_status',
                'delivered',
                'created_date',
            )

    WebhookFilter = WebhookFilterPY3
    WebhookEventFilter = WebhookEventFilterPY3
else:
    import rest_framework_filters as PY2Filters

    class WebhookFilterPY2(PY2Filters.FilterSet):
        target_url = PY2Filters.CharFilter(name="target_url", lookup_expr="iexact")
        event_type = PY2Filters.CharFilter(name="event_type", lookup_expr="iexact")
        is_active = PY2Filters.BooleanFilter(name='is_active')

        class Meta:
            model = Webhook
            fields = ('target_url', 'is_active', 'event_type')

    class WebhookEventFilterPY2(PY2Filters.FilterSet):
        event_type = PY2Filters.CharFilter(
            name='webhook__event_type', lookup_expr='iexact'
        )
        created_date = PY2Filters.DateFilter(name='created_date', lookup_expr='__all__')
        delivered = PY2Filters.BooleanFilter(name='delivered')

        class Meta:
            model = WebhookEvent
            fields = (
                'uuid',
                'event_type',
                'response_http_status',
                'delivered',
                'created_date',
            )

    WebhookFilter = WebhookFilterPY2()
    WebhookEventFilter = WebhookEventFilterPY2()

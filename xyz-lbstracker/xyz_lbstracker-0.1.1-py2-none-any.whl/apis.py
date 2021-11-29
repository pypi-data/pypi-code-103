# -*- coding:utf-8 -*-
from __future__ import division, unicode_literals

from rest_framework.generics import get_object_or_404
from xyz_restful.mixins import UserApiMixin
from datetime import datetime
from . import models, serializers
from rest_framework import viewsets, decorators, response, status
from xyz_restful.decorators import register


@register()
class TemplateViewSet(viewsets.ModelViewSet):
    queryset = models.Template.objects.all()
    serializer_class = serializers.TemplateSerializer
    filter_fields = {
        # 'name': ['exact'],
        'is_active': ['exact'],
        'create_time': ['date', 'gte', 'lte']
    }

@register()
class EventViewSet(UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Event.objects.all()
    serializer_class = serializers.EventSerializer
    search_fields = ('mobile', 'code', 'memo')
    filter_fields = {
        'id': ['in', 'exact'],
        'code': ['exact'],
        'mobile': ['exact'],
        'is_sent': ['exact'],
        'is_read': ['exact'],
        'is_located': ['exact'],
    }

    @decorators.action(['POST'], detail=False, permission_classes=[])
    def locate(self, request):
        event = get_object_or_404(self.get_queryset(), code=request.data.get('code'))
        data = dict(event=event.id)
        data.update(request.data)
        location = serializers.LocationSerializer(data=data)
        location.is_valid(raise_exception=True)
        location.save()
        event.is_located = True
        event.locate_time = datetime.now()
        event.save()
        return response.Response(dict(detail='ok', url=event.template.url), status=status.HTTP_201_CREATED)


@register()
class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Location.objects.all()
    serializer_class = serializers.LocationSerializer
    # search_fields = ('event__name',)
    filter_fields = {
        'id': ['in', 'exact'],
        'event': ['in', 'exact'],
        'create_time': ['date', 'gte', 'lte']
    }

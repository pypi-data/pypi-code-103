# -*- coding:utf-8 -*-
from __future__ import division, unicode_literals

from rest_framework.generics import get_object_or_404
from xyz_restful.mixins import UserApiMixin

from . import models, serializers
from rest_framework import viewsets, decorators, response, status
from xyz_restful.decorators import register

@register()
class EventViewSet(UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Event.objects.all()
    serializer_class = serializers.EventSerializer
    search_fields = ('name','code')
    filter_fields = {
        'id': ['in', 'exact'],
        'code': ['exact'],
    }

    @decorators.action(['POST'], detail=False, permission_classes=[])
    def locate(self, request):
        print(request.data)
        event = get_object_or_404(self.get_queryset(), code=request.data.get('code'))
        data = dict(event=event.id)
        data.update(request.data)
        location = serializers.LocationSerializer(data=data)
        location.is_valid(raise_exception=True)
        location.save()
        return response.Response(dict(detail='ok'), status=status.HTTP_201_CREATED)


@register()
class LocationViewSet(viewsets.ModelViewSet):
    queryset = models.Location.objects.all()
    serializer_class = serializers.LocationSerializer
    # search_fields = ('event__name',)
    filter_fields = {
        'id': ['in', 'exact'],
        'event': ['in', 'exact'],
        'create_time': ['date', 'gte', 'lte']
    }

# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from xyz_restful.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from . import models


class EventSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', label='姓名', read_only=True)
    class Meta:
        model = models.Event
        fields = '__all__'
        read_only_fields = ('create_time', 'update_time', 'user')


class LocationSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', label='事件', read_only=True)
    class Meta:
        model = models.Location
        fields = '__all__'
        read_only_fields = ('create_time',)

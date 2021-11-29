# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from xyz_restful.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from . import models


class TemplateSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Template
        fields = '__all__'
        read_only_fields = ('create_time', 'code')


class EventSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', label='姓名', read_only=True)
    url = serializers.CharField(label='短连接', read_only=True)
    class Meta:
        model = models.Event
        fields = '__all__'
        read_only_fields = ('create_time',
                            # 'update_time',
                            'user',
                            'is_sent',
                            'sent_time',
                            'is_read',
                            'read_time',
                            'is_located',
                            'locate_time',
                            'code')


class LocationSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.__str__', label='事件', read_only=True)

    class Meta:
        model = models.Location
        fields = '__all__'
        read_only_fields = ('create_time',)

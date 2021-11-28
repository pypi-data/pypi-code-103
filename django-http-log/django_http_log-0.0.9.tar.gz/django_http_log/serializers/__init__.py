#!/user/bin/env python3
# -*- coding: utf-8 -*-
"""
--------------------------------------
    Author:     JiChao_Song
    Date  :     2021/4/15 13:40
    Desc  :
--------------------------------------
"""
from rest_framework import serializers
from rest_framework_mongoengine import serializers as dsrializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        exclude = kwargs.pop('exclude', None)
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)
        if exclude:
            allowed = set(exclude)
            for field_name in allowed:
                self.fields.pop(field_name)


class DocumentDynamicFieldsModelSerializer(dsrializers.DocumentSerializer):

    def __init__(self, *args, **kwargs):
        exclude = kwargs.pop('exclude', None)
        super(DocumentDynamicFieldsModelSerializer, self).__init__(*args, **kwargs)
        if exclude:
            allowed = set(exclude)
            for field_name in allowed:
                self.fields.pop(field_name)

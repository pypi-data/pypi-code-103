# -*- coding: utf-8 -*-

"""
@author: xuan
@contact: QQ:595127207
@Created on: 2021/6/1 001 22:38
@Remark: 数据映射模块
"""
import json
import logging

from django.apps import apps
from rest_framework import serializers
from xdj_utils.json_response import SuccessResponse
from xdj_utils.serializers import CustomModelSerializer
from xdj_utils.viewset import CustomModelViewSet

from xdj_datamap.models import DataMapsModel, FieldsModel

logger = logging.getLogger(__name__)


class FieldsSerializer(CustomModelSerializer):

    class Meta:
        model = FieldsModel
        fields = "__all__"


class DataMapSerializer(CustomModelSerializer):
    where_cluase = serializers.JSONField()
    fields = FieldsSerializer(many=True)

    class Meta:
        model = DataMapsModel
        fields = "__all__"


class DataMapViewSet(CustomModelViewSet):

    queryset = DataMapsModel.objects.all()
    serializer_class = DataMapSerializer
    search_fields = ['model_app', 'model_name', 'where_cluase', 'exclude_cluase']

    #获取datamap对象
    def get_obj(self, data):
        k = data
        datamap = k.get('datamap') or k.get('datamap_id')
        try:
            obj = self.queryset.get(id=datamap)
            return obj
        except DataMapsModel.DoesNotExist:
            logger.error(f'dose not have this datamap, datamap_id:{datamap}')

    #获取datamap对应的fields
    def get_fields_(self, obj):
        if obj is None: return []
        serializer = DataMapSerializer(obj)
        fields = serializer.data.get('fields')
        fields_ = []
        for field in fields:
            field = dict(field)
            fields_.append(field)
        fields_.sort(key=lambda o: o.get('field_sort'))

        return fields_

    # 获取datamap对应app和model的源模型，并按照where和exclude过滤
    def get_map_(self, obj):
        if obj is None: return self.queryset.none()

        model_app = obj.model_app
        model_name = obj.model_name
        where_cluase = json.loads(obj.where_cluase or "{}")
        exclude_cluase = json.loads(obj.exclude_cluase or "{}")
        qs = apps.get_model(model_app,model_name).objects.all()

        if qs is not None:
            qs = qs.filter(**where_cluase).exclude(**exclude_cluase)
        return qs

    def get_model_(self, request=None, *args, **kwargs):
        k = {**(request.data if request else {}), **kwargs}
        obj = self.get_obj(k)
        model_app = obj.model_app
        model_name = obj.model_name
        model = apps.get_model(model_app,model_name)
        model_ = []
        for m in model._meta.fields:
            model_.append({"name": m.name, "verbose_name": m.verbose_name})
        return model_

    def get_model(self, request, *args, **kwargs):
        return SuccessResponse(data=self.get_model_(request, args, kwargs), msg='获取成功')

    #获取数据
    def get_data_(self, request=None, *args, **kwargs):
        k = {**(request.data if request else {}), **kwargs}
        obj = self.get_obj(k)
        fields_ = self.get_fields_(obj)
        field_names = [o.get('field_name') for o in fields_]
        qs = self.get_map_(obj).values(*field_names).order_by(k.get('order_by','year'))
        ret = []
        for q in qs:
            ret.append(q)

        return {"body":ret,"fields":fields_}

    def get_data(self, request, *args, **kwargs):
        return SuccessResponse(data=self.get_data_(request, args, kwargs), msg='获取成功')
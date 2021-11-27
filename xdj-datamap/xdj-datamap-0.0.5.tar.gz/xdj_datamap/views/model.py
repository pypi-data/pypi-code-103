# -*- coding: utf-8 -*-

"""
@author: xuan
@contact: QQ:595127207
@Created on: 2021/6/1 001 22:38
@Remark: 数据映射模块
"""

from django.contrib.contenttypes.models import ContentType
from xdj_utils.serializers import CustomModelSerializer
from xdj_utils.viewset import CustomModelViewSet

from xdj_datamap.models import DataMapsModel


class ModelsSerializer(CustomModelSerializer):

    class Meta:
        model = ContentType
        fields = "__all__"



class ModelViewSet(CustomModelViewSet):

    queryset = DataMapsModel.objects.all()
    serializer_class = ModelsSerializer
    search_fields = ['app_label','model']
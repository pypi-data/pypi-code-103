# -*- coding: utf-8 -*-

"""
@author: xuan
@contact: QQ:595127207
@Created on: 2021/11/27 001 22:38
@Remark: 数据映射模块
"""

from xdj_utils.serializers import CustomModelSerializer
from xdj_utils.viewset import CustomModelViewSet

from xdj_datamap.models import FieldsModel


class FieldsSerializer(CustomModelSerializer):

    class Meta:
        model = FieldsModel
        fields = "__all__"


class FieldsViewSet(CustomModelViewSet):

    queryset = FieldsModel.objects.all()
    serializer_class = FieldsSerializer
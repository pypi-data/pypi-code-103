#!/user/bin/env python3
# -*- coding: utf-8 -*-
"""
--------------------------------------
    Author:     JiChao_Song
    Date  :     2021/11/28 下午7:12
    Desc  :
--------------------------------------
"""
from mongoengine import Document
from rest_framework.generics import GenericAPIView


class BaseAPIView(GenericAPIView):
    Model: Document

    exclude_fields = ['deleted', 'deleteTime']

    # 可查询字段列表 '-代表是外键  外键没有模糊查询'
    search_fields = []

    # 查询方式
    queries = "icontains"

    def search_queryset(self, request):
        params_dict = {}
        data = request.data
        params_list = list(data.keys())
        for i in self.search_fields:
            if i[0:1] != '-':
                if i in params_list and data[i] is not None:
                    a = f"{i}__{self.queries}"
                    params_dict[a] = data[i]
            else:
                a = i[1:]
                if a in params_list and data[a] is not None:
                    params_dict[a] = data[a]
        return params_dict

    def pop_serializer(self, serializer):
        exclude = self.exclude_fields
        data = serializer.data.copy()
        if exclude is not None:
            for i in exclude:
                del data[i]
        return data

    def preform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perfom_delete(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        pass

    def get(self, request, *args, **kwargs):
        pass

    def put(self, request, *args, **kwargs):
        pass

    def delete(self, request, *args, **kwargs):
        pass

    def patch(self, request, *args, **kwargs):
        pass

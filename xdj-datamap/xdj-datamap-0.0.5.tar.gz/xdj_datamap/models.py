from django.db import models

from xdj_utils.models import CoreModel
from xdj_datamap.conf import conf

table_prefix = conf.TABLE_PREFIX


def default_dict():
    return {}


class DataMapsModel(CoreModel):
    where_cluase = models.CharField(max_length=255, blank=True, null=True)
    exclude_cluase = models.CharField(max_length=255, blank=True, null=True)
    model_app = models.CharField(max_length=255, blank=True, null=True)
    model_name = models.CharField(max_length=255, blank=True, null=True)
    #fields

    class Meta:
        db_table = table_prefix + "datamap_model"
        verbose_name = '数据映射表'
        verbose_name_plural = verbose_name
        ordering = ('create_datetime',)


class FieldsModel(CoreModel):
    datamap = models.ManyToManyField(to='DataMapsModel',related_name='fields', verbose_name="字段", null=True, blank=True,
                               db_constraint=False, help_text="字段")
    field_name = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="字段名")
    field_desc = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="字段描述")
    field_fath = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="字段父描述")
    field_unit = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="字段单位")
    field_show = models.CharField(max_length=255, default="", blank=True, null=True, verbose_name="字段表示方式")#%，整数，两位小数
    field_sort = models.IntegerField( default=0, verbose_name="字段排序")

    class Meta:
        db_table = table_prefix + "datamap_field"
        verbose_name = '字段表'
        verbose_name_plural = verbose_name
        ordering = ('create_datetime',)
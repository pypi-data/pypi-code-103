# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string
import logging

log = logging.getLogger('django')


class Event(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "事件"
        ordering = ('-create_time',)

    name = models.CharField("名称", max_length=255, unique=True)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="lbstracker_events",
                             on_delete=models.PROTECT)
    code = models.CharField("代码", max_length=6, unique=True, blank=True)
    memo = models.TextField("备注", null=True, blank=True, default='')
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.code:
            self.code = get_random_string(6)
        super(Event, self).save(**kwargs)


class Location(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "定位"
        ordering = ('-create_time',)

    event = models.ForeignKey(Event, verbose_name=Event._meta.verbose_name, related_name="locations",
                              on_delete=models.PROTECT)
    longitude = models.DecimalField("经度", decimal_places=14, max_digits=18)
    latitude = models.DecimalField("纬度", decimal_places=15, max_digits=18)
    address = models.CharField("地址", max_length=255, null=True, blank=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)

    def __str__(self):
        return '%s@%s' % (self.event, self.create_time.isoformat())
    
    def save(self, **kwargs):
        if not self.id:
            self.check_address()
        super(Location, self).save(**kwargs)

    def check_address(self):
        if not self.address:
            from .helper import get_location_address
            try:
                self.address = get_location_address(self.longitude, self.latitude)
            except:
                import traceback
                log.error('Location(ID:%s).check_address error: %s', id, traceback.format_exc())

# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string
import logging

from django.utils.functional import cached_property

log = logging.getLogger('django')


class Template(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "模板"
        ordering = ('-create_time',)

    name = models.CharField("名称", max_length=255, unique=True)
    content = models.CharField("短信内容", max_length=255, null=True, blank=True,
                               help_text='短信文本模板, 其中"{{url}}"替换落地页地址')
    url = models.URLField("跳转网址", null=True, blank=True, default='')
    is_active = models.BooleanField("有效", blank=True, default=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.content:
            self.content = "{{url}}"
        super(Template, self).save(**kwargs)


class Event(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "事件"
        ordering = ('-create_time',)

    code = models.CharField("代码", max_length=6, unique=True, blank=True)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="lbstracker_events",
                             on_delete=models.PROTECT)
    mobile = models.CharField("手机", max_length=16)
    template = models.ForeignKey(Template, verbose_name=Template._meta.verbose_name, related_name="events",
                                 on_delete=models.PROTECT, )
    memo = models.TextField("备注", null=True, blank=True, default='')
    content = models.CharField("内容", max_length=255, null=True, blank=True)
    is_sent = models.BooleanField("已发", blank=True, default=False)
    is_read = models.BooleanField("已读", blank=True, default=False)
    is_located = models.BooleanField("已定位", blank=True, default=False)
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)
    sent_time = models.DateTimeField("发送时间", null=True, blank=True)
    read_time = models.DateTimeField("查看时间", null=True, blank=True)
    locate_time = models.DateTimeField("定位时间", null=True, blank=True)

    def __str__(self):
        return '%s(%s)' % (self.code, self.mobile)

    def save(self, **kwargs):
        if not self.code:
            self.code = get_random_string(6)
        if not self.content:
            from django.template import Template, Context
            from xyz_util.dateutils import get_next_date
            ctx = Context(dict(
                url=self.url,
                day=get_next_date(None, 7).isoformat())
            )
            self.content = Template(self.template.content).render(ctx)
        super(Event, self).save(**kwargs)

    @cached_property
    def url(self):
        from .helper import get_short_url_domain
        return '%s/%s' % (get_short_url_domain(), self.code)


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

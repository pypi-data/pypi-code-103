# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.dispatch import receiver
from xyz_saas.signals import to_get_party_settings


@receiver(to_get_party_settings)
def get_lbstracker_settings(sender, **kwargs):
    from .helper import get_short_url_domain
    return {
        'shortUrlDomain': get_short_url_domain()
    }

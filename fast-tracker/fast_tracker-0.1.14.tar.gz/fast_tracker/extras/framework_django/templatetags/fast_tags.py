# -*- coding: utf-8 -*-

import django.template

from fast_tracker.hooks.framework_django import (
        fast_browser_timing_header, fast_browser_timing_footer)

register = django.template.Library()

register.simple_tag(fast_browser_timing_header)
register.simple_tag(fast_browser_timing_footer)

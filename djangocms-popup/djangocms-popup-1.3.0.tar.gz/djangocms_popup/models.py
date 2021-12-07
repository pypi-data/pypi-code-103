from cms.models.pluginmodel import CMSPlugin
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from .settings import POPUP_LIST_TEMPLATES


class PopupPluginModel(CMSPlugin):
    display_delay = models.IntegerField(_("Display after X seconds"), default=0)
    can_reopen_popup = models.BooleanField(
        _("Allow the popup to be reopened if it is closed"), default=False
    )

    popup_template = models.CharField(
        verbose_name=_("Popup style"),
        choices=POPUP_LIST_TEMPLATES,
        max_length=300,
        blank=False,
    )

    def get_page_url(self):
        try:
            # thx https://stackoverflow.com/a/47953774/6813732
            return mark_safe(
                '<a href="'
                + self.page.get_absolute_url()
                + '">'
                + self.page.get_page_title()
                + "</a>"
            )
        except AttributeError:
            return ""

    # thx https://stackoverflow.com/a/12048244/6813732
    get_page_url.short_description = _("Page")

    class Meta:
        verbose_name = _("Popup")

    def __unicode__(self):
        return "Popup"

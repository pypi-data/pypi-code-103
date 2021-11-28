from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from feincms._internal import ct_render_to_string

from . import appsettings


class ButtonContent(models.Model):
    """
    Pager item, to show a previous/next page.
    The pages are auto determined, but can be overwritten
    """

    ALIGN_CHOICES = (
        ("", pgettext_lazy("align", "Inline")),
        ("left", pgettext_lazy("align", "Left")),
        ("center", pgettext_lazy("align", "Center")),
        ("right", pgettext_lazy("align", "Right")),
        ("block", pgettext_lazy("align", "Full Width")),
    )

    title = models.CharField(_("title"), max_length=200)
    url = models.URLField(_("URL"))

    style = models.CharField(_("style"), max_length=50, choices=appsettings.FEINCMS_BUTTON_STYLES)
    size = models.CharField(_("size"), blank=True, default="", max_length=10, choices=appsettings.FEINCMS_BUTTON_SIZES)
    align = models.CharField(_("alignment"), blank=True, default="", max_length=50, choices=ALIGN_CHOICES)

    class Meta:
        abstract = True
        verbose_name = _("button")
        verbose_name_plural = _("button")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return self.url

    @property
    def css_classes(self):
        classes = ["btn", self.style, self.size or ""]
        if self.align:
            if self.align == "left":
                classes.append("pull-left")
            elif self.align == "right":
                classes.append("pull-right")
            elif self.align == "block":
                classes.append("btn-block")

        return " ".join(classes).rstrip().replace("  ", " ")

    def render(self, **kwargs):
        return ct_render_to_string(
            ["content/button/%s.html" % self.region, "content/button/default.html"],
            {"content": self},
            request=kwargs.get("request"),
            context=kwargs.get("context"),
        )

from django.conf import settings
from django.utils.translation import pgettext_lazy

FEINCMS_BUTTON_STYLES = getattr(
    settings,
    "FEINCMS_BUTTON_STYLES",
    (
        ("btn-default", pgettext_lazy("button-style", "Default")),
        ("btn-primary", pgettext_lazy("button-style", "Primary")),
        ("btn-success", pgettext_lazy("button-style", "Success")),
        ("btn-info", pgettext_lazy("button-style", "Info")),
        ("btn-warning", pgettext_lazy("button-style", "Warning")),
        ("btn-danger", pgettext_lazy("button-style", "Danger")),
        ("btn-link", pgettext_lazy("button-style", "Link")),
    ),
)

FEINCMS_BUTTON_SIZES = getattr(
    settings,
    "FEINCMS_BUTTON_SIZES",
    (
        ("", pgettext_lazy("button-size", "Default")),
        ("btn-lg", pgettext_lazy("button-size", "Large")),
        ("btn-sm", pgettext_lazy("button-size", "Small")),
        ("btn-xs", pgettext_lazy("button-size", "Extra Small")),
    ),
)

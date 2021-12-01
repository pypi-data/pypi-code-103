import re
from django.dispatch import receiver
from django.templatetags.static import static
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _
from pretix.base.signals import logentry_display
from pretix.control.signals import html_head, html_page_start, nav_event, nav_topbar

from pretix_batch_emailer.views import BatchSenderView


@receiver(nav_topbar, dispatch_uid="pretix_batch_emailer")
def nav_topbar_f(sender, request=None, **kwargs):
    if re.match(r"^/control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/", sender.path):
        if "pretix_batch_emailer" in sender.event.plugins:
            return [{"label": _("Batch email visible orders"), "url": "#batch-emailer"}]

    return [{"label": "", "url": ""}]


@receiver(html_page_start, dispatch_uid="pretix_batch_emailer")
def order_eventpart_selection_public(sender, **kwargs):
    if re.match(
        r"^/control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/*", sender.path
    ):
        x = BatchSenderView().prefill(sender)
        return x
    return None


@receiver(html_head, dispatch_uid="pretix_batch_emailer")
def batch_emailer_script(sender, **kwargs):
    url = static("pretix_batch_emailer/batch-emailer.js")
    return f"<script src='{url}'> </script>"


@receiver(nav_event, dispatch_uid="pretix_batch_emailer")
def control_nav_import(sender, request=None, **kwargs):
    url = resolve(request.path_info)
    if not request.user.has_event_permission(
        request.organizer, request.event, "can_change_orders", request=request
    ):
        return []
    return [
        {
            "label": _("Batch email history"),
            "url": reverse(
                "plugins:pretix_batch_emailer:history",
                kwargs={
                    "event": request.event.slug,
                    "organizer": request.event.organizer.slug,
                },
            ),
            "active": (
                url.namespace == "plugins:pretix_batch_emailer"
                and url.url_name == "history"
            ),
            "icon": "envelope",
            "parent": reverse(
                "plugins:sendmail:send",
                kwargs={
                    "event": request.event.slug,
                    "organizer": request.event.organizer.slug,
                },
            ),
        },
    ]


@receiver(signal=logentry_display)
def pretixcontrol_logentry_display(sender, logentry, **kwargs):
    plains = {
        "pretix.plugins.pretix_batch_emailer.sent": _("Batch email was sent"),
        "pretix.plugins.pretix_batch_emailer.order.email.sent": _(
            "The order received a batch email."
        ),
    }
    if logentry.action_type in plains:
        return plains[logentry.action_type]

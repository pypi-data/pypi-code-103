from django.conf.urls import url

from pretix_batch_emailer.views import BatchSenderView, EmailHistoryView

urlpatterns = [
    url(
        r"^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/batch_emailer/send_mail/$",
        BatchSenderView.as_view(),
        name="batch_send",
    ),
    url(
        r"^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/batch_emailer/history/",
        EmailHistoryView.as_view(),
        name="history",
    ),
]

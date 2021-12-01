import bleach
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, ListView
from pretix.base.email import get_available_placeholders
from pretix.base.i18n import LazyI18nString, language
from pretix.base.models import LogEntry, Order
from pretix.base.services.mail import TolerantDict
from pretix.base.templatetags.rich_text import markdown_compile_email
from pretix.control.permissions import EventPermissionRequiredMixin

from pretix_batch_emailer.forms import CollectBulkOrdersForm

from . import forms
from .tasks import send_mails


class BatchSenderView(EventPermissionRequiredMixin, FormView):
    template_name = "pretix_batch_emailer/send_mail.html"
    permission = "can_change_orders"
    form_class = forms.BatchMailForm

    def prefill(self, request, *args, **kwargs):
        form = forms.CollectBulkOrdersForm()
        return render_to_string(
            "pretix_batch_emailer/collect_bulk_orders.html",
            {
                "form": form,
                "organizer": request.event.organizer,
                "event": request.event,
            },
            request=request,
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["event"] = self.request.event
        if "from_log" in self.request.GET:
            try:
                from_log_id = self.request.GET.get("from_log")
                logentry = LogEntry.objects.get(
                    id=from_log_id,
                    event=self.request.event,
                    action_type="pretix.plugins.pretix_batch_emailer.sent",
                )
                kwargs["initial"] = {
                    "recipients": [
                        r["id"] for r in logentry.parsed_data.get("recipients")
                    ],
                    "orders": logentry.parsed_data.get("orders"),
                    "description": logentry.parsed_data.get("description"),
                    "message": LazyI18nString(logentry.parsed_data["message"]),
                    "subject": LazyI18nString(logentry.parsed_data["subject"]),
                }

            except LogEntry.DoesNotExist:
                raise Http404(_("You supplied an invalid log entry ID"))
        return kwargs

    def post(self, request, *args, **kwargs):

        if request.POST.get("action") == "prefill":
            form = CollectBulkOrdersForm(request.POST)
            if form.is_valid():
                recipients = Order.objects.filter(
                    code__in=form.data.get("orders", "").split(",")
                )
                form = forms.BatchMailForm(
                    initial={
                        "recipients": recipients.values_list("id", flat=True),
                        "orders": form.data.get("orders"),
                    },
                    event=self.request.event,
                )
                return self.render_to_response(self.get_context_data(form=form))
            else:
                previous = request.POST.get("previous", "/")
                messages.add_message(
                    request, messages.ERROR, _("No orders are visible.")
                )
                return HttpResponseRedirect(previous)

        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        messages.error(
            self.request, _("We could not send the email. See below for details.")
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        orders = form.cleaned_data.get("recipients").distinct()

        self.output = {}
        if not orders:
            messages.error(
                self.request, _("There are no orders matching this selection.")
            )
            return self.get(self.request, *self.args, **self.kwargs)

        if self.request.POST.get("action") == "preview":
            for locale in self.request.event.settings.locales:
                with language(locale, self.request.event.settings.region):
                    context_dict = TolerantDict()
                    for k, v in get_available_placeholders(
                        self.request.event, ["event", "order", "position_or_address"]
                    ).items():
                        context_dict[
                            k
                        ] = '<span class="placeholder" title="{}">{}</span>'.format(
                            _(
                                "This value will be replaced based on dynamic parameters."
                            ),
                            v.render_sample(self.request.event),
                        )

                    subject = bleach.clean(
                        form.cleaned_data["subject"].localize(locale), tags=[]
                    )
                    preview_subject = subject.format_map(context_dict)
                    message = form.cleaned_data["message"].localize(locale)
                    preview_text = markdown_compile_email(
                        message.format_map(context_dict)
                    )

                    self.output[locale] = {
                        "subject": _("Subject: {subject}").format(
                            subject=preview_subject
                        ),
                        "html": preview_text,
                        "attachment": form.cleaned_data.get("attachment"),
                    }

            return self.get(self.request, *self.args, **self.kwargs)

        kwargs = {
            "event": self.request.event.pk,
            "user": self.request.user.pk,
            "subject": form.cleaned_data["subject"].data,
            "message": form.cleaned_data["message"].data,
            "description": form.cleaned_data["description"],
            "orders": [o.pk for o in orders],
        }
        if (
            form.cleaned_data.get("attachment") is not None
            and form.cleaned_data.get("attachment") is not False
        ):
            kwargs["attachments"] = [form.cleaned_data["attachment"].id]

        send_mails.apply_async(kwargs=kwargs)
        self.request.event.log_action(
            "pretix.plugins.pretix_batch_emailer.sent",
            user=self.request.user,
            data=dict(form.cleaned_data),
        )
        messages.success(
            self.request,
            _(
                "Your message has been queued and will be sent to the contact addresses of %d "
                "orders in the next few minutes."
            )
            % len(orders),
        )

        return redirect(
            "plugins:pretix_batch_emailer:history",
            event=self.request.event.slug,
            organizer=self.request.event.organizer.slug,
        )

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["output"] = getattr(self, "output", None)
        return ctx


class EmailHistoryView(EventPermissionRequiredMixin, ListView):
    template_name = "pretix_batch_emailer/history.html"
    permission = "can_change_orders"
    model = LogEntry
    context_object_name = "logs"
    paginate_by = 5

    def get_queryset(self):
        qs = LogEntry.objects.filter(
            event=self.request.event,
            action_type="pretix.plugins.pretix_batch_emailer.sent",
        ).select_related("event", "user")
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()

        for log in ctx["logs"]:
            log.pdata = log.parsed_data
            log.pdata["locales"] = {}
            log.pdata["recipients"] = Order.objects.filter(
                code__in=log.pdata["orders"].split(",")
            )
            for locale, msg in log.pdata["message"].items():
                log.pdata["locales"][locale] = {
                    "message": msg,
                    "subject": log.pdata["subject"][locale],
                }
        return ctx

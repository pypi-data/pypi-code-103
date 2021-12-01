from django import forms
from django.conf import settings
from django.forms import ModelMultipleChoiceField
from django.utils.translation import gettext_lazy as _
from django_scopes.forms import SafeModelMultipleChoiceField
from i18nfield.forms import I18nFormField, I18nTextarea, I18nTextInput
from pretix.base.email import get_available_placeholders
from pretix.base.forms import PlaceholderValidator
from pretix.base.models import Order
from pretix.control.forms import CachedFileField


class BatchMailForm(forms.Form):
    orders = forms.CharField(widget=forms.HiddenInput(), required=True)
    recipients = SafeModelMultipleChoiceField(
        queryset=Order.objects.none(),
    )
    description = forms.CharField(label=_("Recipient Description"))
    subject = forms.CharField(label=_("Subject"))
    message = forms.CharField(label=_("Message"))
    attachment = CachedFileField(
        label=_("Attachment"),
        required=False,
        ext_whitelist=(
            ".png",
            ".jpg",
            ".gif",
            ".jpeg",
            ".pdf",
            ".txt",
            ".docx",
            ".gif",
            ".svg",
            ".pptx",
            ".ppt",
            ".doc",
            ".xlsx",
            ".xls",
            ".jfif",
            ".heic",
            ".heif",
            ".pages",
            ".bmp",
            ".tif",
            ".tiff",
        ),
        help_text=_(
            "Sending an attachment increases the chance of your email not arriving or being sorted into spam folders. We recommend only using PDFs "
            "of no more than 2 MB in size."
        ),
        max_size=settings.FILE_UPLOAD_MAX_SIZE_EMAIL_ATTACHMENT,
    )

    def _set_field_placeholders(self, fn, base_parameters):
        phs = [
            "{%s}" % p
            for p in sorted(
                get_available_placeholders(self.event, base_parameters).keys()
            )
        ]
        ht = _("Available placeholders: {list}").format(list=", ".join(phs))
        if self.fields[fn].help_text:
            self.fields[fn].help_text += " " + str(ht)
        else:
            self.fields[fn].help_text = ht
        self.fields[fn].validators.append(PlaceholderValidator(phs))

    def __init__(self, *args, **kwargs):
        if "event" in kwargs:
            event = self.event = kwargs.pop("event")

        super().__init__(*args, **kwargs)

        if self.initial:
            order_str = self.initial.get("orders", "")

        else:
            order_str = self.data.get("orders", "")

        self.fields["recipients"] = ModelMultipleChoiceField(
            label=_("Send email to"),
            widget=forms.SelectMultiple(),
            required=True,
            queryset=Order.objects.filter(code__in=order_str.split(",")),
        )

        self.fields["subject"] = I18nFormField(
            label=_("Subject"),
            widget=I18nTextInput,
            required=True,
            locales=event.settings.get("locales"),
        )
        self.fields["message"] = I18nFormField(
            label=_("Message"),
            widget=I18nTextarea,
            required=True,
            locales=event.settings.get("locales"),
        )
        self._set_field_placeholders(
            "subject", ["event", "order", "position_or_address"]
        )
        self._set_field_placeholders(
            "message", ["event", "order", "position_or_address"]
        )

        def clean_recipients(self):
            recipients = self.cleaned_data.get("recipients", "")
            if not recipients:
                return


class CollectBulkOrdersForm(forms.Form):
    orders = forms.CharField(
        widget=forms.HiddenInput(attrs={"id": "batch_emailer_orders"})
    )
    url = forms.CharField(widget=forms.HiddenInput(attrs={"id": "batch_emailer_url"}))
    action = forms.CharField(
        widget=forms.HiddenInput(attrs={"id": "batch_emailer_action"}),
        initial="prefill",
    )
    previous = forms.CharField(widget=forms.HiddenInput())

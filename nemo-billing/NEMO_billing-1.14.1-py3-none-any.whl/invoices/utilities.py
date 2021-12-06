import ntpath
import os
from datetime import datetime
from decimal import Decimal
from typing import Optional

from NEMO.utilities import send_mail
from NEMO.views.customization import get_media_file_contents
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.formats import date_format, number_format
from django.utils.text import slugify


def get_invoice_document_filename(invoice, filename):
    account_name = slugify(invoice.project_details.project.account.name)
    project_name = slugify(invoice.project_details.name)
    now = datetime.now()
    # generated_date = now.strftime("%Y-%m-%d_%H-%M-%S")
    year = now.strftime("%Y")
    ext = os.path.splitext(filename)[1]
    return f"invoices/{year}/{account_name}/{project_name}/{slugify(invoice.invoice_number)}_{project_name}{ext}"


def get_merchant_logo_filename(configuration, filename):
    name = slugify(configuration.name + "_merchant_logo")
    ext = os.path.splitext(filename)[1]
    return f"merchant_logos/{name}{ext}"


def display_amount(amount: Optional[Decimal], configuration=None) -> str:
    # We need to specifically check for None since amount = 0 will evaluate to False
    if amount is None:
        return ""
    rounded_amount = round(amount, 2)
    currency = (
        f"{configuration.currency_symbol}"
        if configuration and configuration.currency_symbol
        else f"{configuration.currency} "
        if configuration and configuration.currency
        else ""
    )
    if amount < 0:
        return f"({currency}{number_format(abs(rounded_amount), decimal_pos=2)})"
    else:
        return f"{currency}{number_format(rounded_amount, decimal_pos=2)}"


def render_and_send_email(template_prefix, context, from_email, to=None, bcc=None, cc=None, attachments=None) -> int:
    subject = render_template_from_media("{0}_subject.txt".format(template_prefix), context)
    # remove superfluous line breaks
    subject = " ".join(subject.splitlines()).strip()
    subject = format_email_subject(subject)
    template_name = "{0}_message.html".format(template_prefix)
    content = render_template_from_media(template_name, context).strip()
    return send_mail(
        subject=subject, content=content, from_email=from_email, to=to, bcc=bcc, cc=cc, attachments=attachments
    )


def format_email_subject(subject):
    prefix = getattr(settings, "INVOICE_EMAIL_SUBJECT_PREFIX", "")
    return prefix + force_str(subject)


def render_template_from_media(template_name, context):
    """ Try to find the template in media folder. if it doesn't exists, look in project templates """
    file_name = ntpath.basename(template_name)
    email_contents = get_media_file_contents(file_name)
    if email_contents:
        return Template(email_contents).render(Context(context))
    else:
        # otherwise look in templates
        return render_to_string(template_name, context)


def render_combine_responses(request, original_response: HttpResponse, template_name, context):
    """ Combines contents of an original http response with a new one """
    additional_content = render(request, template_name, context)
    original_response.content += additional_content.content
    return original_response


def category_name_for_item_type(billable_item_type) -> str:
    from NEMO_billing.invoices.invoice_generator import invoice_generator_class

    return invoice_generator_class.get_invoice_data_processor().category_name_for_item_type(billable_item_type)


def name_for_billable_item(billable_item) -> str:
    from NEMO_billing.invoices.invoice_generator import invoice_generator_class

    return invoice_generator_class.get_invoice_data_processor().name_for_item(billable_item)


# Remove when NEMO 3.14 is released
def export_format_datetime(date_time=None, date_format=True, time_format=True, underscore=True, as_current_tz=True):
    """ This function returns a formatted date/time for export files. Default returns date + time format, with underscores """
    time = date_time if date_time else timezone.now() if as_current_tz else datetime.now()
    export_date_format = getattr(settings, "EXPORT_DATE_FORMAT", "m_d_Y").replace("-", "_")
    export_time_format = getattr(settings, "EXPORT_TIME_FORMAT", "h_i_s").replace("-", "_")
    if not underscore:
        export_date_format = export_date_format.replace("_", "-")
        export_time_format = export_time_format.replace("_", "-")
    separator = "-" if underscore else "_"
    datetime_format = (
        export_date_format
        if date_format and not time_format
        else export_time_format
        if not date_format and time_format
        else export_date_format + separator + export_time_format
    )
    return format_datetime(time, datetime_format, as_current_tz)


# Remove when NEMO 3.14 is released
def format_datetime(universal_time=None, datetime_format="DATETIME_FORMAT", as_current_tz=True, use_l10n=None) -> str:
    time = universal_time if universal_time else timezone.now() if as_current_tz else datetime.now()
    local_time = timezone.localtime(time) if as_current_tz else time
    return date_format(local_time, datetime_format, use_l10n)

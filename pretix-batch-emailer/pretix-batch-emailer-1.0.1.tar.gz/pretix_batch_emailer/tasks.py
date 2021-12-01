from i18nfield.strings import LazyI18nString
from pretix.base.email import get_email_context
from pretix.base.i18n import language
from pretix.base.models import Event, InvoiceAddress, Order, User
from pretix.base.services.mail import SendMailException, mail
from pretix.base.services.tasks import ProfiledEventTask
from pretix.celery_app import app


@app.task(base=ProfiledEventTask, acks_late=True)
def send_mails(
    event: Event,
    user: int,
    subject: dict,
    message: dict,
    orders: list,
    description: str,
    attachments: list = None,
) -> None:
    failures = []
    user = User.objects.get(pk=user) if user else None
    orders = Order.objects.filter(pk__in=orders, event=event)
    subject = LazyI18nString(subject)
    message = LazyI18nString(message)

    for o in orders:
        try:
            ia = o.invoice_address
        except InvoiceAddress.DoesNotExist:
            ia = InvoiceAddress(order=o)

        if o.email:
            try:
                with language(o.locale, event.settings.region):
                    email_context = get_email_context(
                        event=event, order=o, position_or_address=ia
                    )
                    mail(
                        o.email,
                        subject,
                        message,
                        email_context,
                        event,
                        locale=o.locale,
                        order=o,
                        attach_cached_files=attachments,
                    )
                    o.log_action(
                        "pretix.plugins.pretix_batch_emailer.order.email.sent",
                        user=user,
                        data={
                            "subject": subject.localize(o.locale).format_map(
                                email_context
                            ),
                            "message": message.localize(o.locale).format_map(
                                email_context
                            ),
                            "recipient": o.email,
                            "description": description,
                        },
                    )
            except SendMailException:
                failures.append(o.email)

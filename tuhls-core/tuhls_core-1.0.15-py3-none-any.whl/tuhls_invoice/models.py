from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from tuhls_core.models import CustomModel


class Invoice(CustomModel):
    class Types(models.TextChoices):
        INVOICE = "i", "invoice"
        ESTIMATE = "e", "estimate"
        CREDIT_NOTE = "cn", "credit note"

    user = models.UUIDField()
    type = models.CharField(max_length=2, choices=Types.choices, blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)

    name = models.CharField(max_length=63, blank=True, null=True)
    address1 = models.CharField(max_length=63, blank=True, null=True)
    address2 = models.CharField(max_length=63, blank=True, null=True)
    zip_code = models.CharField(max_length=63, blank=True, null=True)
    city = models.CharField(max_length=63, blank=True, null=True)
    country = models.CharField(max_length=63, blank=True, null=True)
    state = models.CharField(max_length=63, blank=True, null=True)
    company = models.CharField(max_length=63, blank=True, null=True)
    vat = models.CharField(max_length=63, blank=True, null=True)

    payment_reference = models.CharField(max_length=63, blank=True, null=True)
    payment_provider = models.CharField(max_length=63, blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    def total(self):
        t = 0
        for detail in self.details.all():
            t = t + detail.amount
        return t

    def get_type_name(self):
        return dict(self.Types.choices)[self.type]

    def get_invoice_number(self):
        if self.number:
            return f"{self.type}-{self.number:06d}"
        else:
            """ """

    def get_file_name(self):
        return f"{settings.SAAS_SHORT_NAME}-{self.get_type_name()}-{self.get_invoice_number()}.pdf"


@receiver(post_save, sender=Invoice)
def find_next_number(sender: Invoice, instance: Invoice, created: bool, **kwargs):
    if not instance.number:
        last_invoice = (
            sender.objects.filter(type=instance.type, number__gt=0)
            .order_by("-number")
            .first()
        )
        if last_invoice and last_invoice.number and last_invoice.number > 0:
            instance.number = last_invoice.number + 1
        else:
            instance.number = 1
        instance.save()


class InvoiceDetail(CustomModel):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="details"
    )

    name = models.CharField(max_length=63)
    description = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)

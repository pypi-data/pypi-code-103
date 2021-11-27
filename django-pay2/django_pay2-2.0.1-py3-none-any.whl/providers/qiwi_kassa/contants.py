from django.db.models import TextChoices


class NotifyType(TextChoices):
    PAYMENT = "PAYMENT"
    CAPTURE = "CAPTURE"
    REFUND = "REFUND"
    CHECK_CARD = "CHECK_CARD"


class Status(TextChoices):
    SUCCESS = "SUCCESS"

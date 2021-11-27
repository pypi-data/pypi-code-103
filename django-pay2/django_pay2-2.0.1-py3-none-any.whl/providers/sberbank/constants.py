from django.db.models import IntegerChoices, TextChoices


class SberbankCallbackOperation(TextChoices):
    approved = "approved"
    declined_by_timeout = "declinedByTimeout"
    deposited = "deposited"
    reversed = "reversed"
    refunded = "refunded"


class SberbankCallbackStatus(IntegerChoices):
    success = 1
    error = 0

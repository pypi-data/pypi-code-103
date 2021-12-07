from django.conf import settings

VERIFICATION_SERIALIZER = getattr(settings, "OTP_VERIFICATION_SERIALIZER", None)

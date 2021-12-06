from django.dispatch import Signal
to_send_sms = Signal(providing_args=["mobile", "content"])
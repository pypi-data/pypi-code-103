import logging
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.forms.fields import CharField
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField

logger = logging.getLogger(__name__)


class FireBasePhoneAuthFrom(forms.Form):
    phone_number = PhoneNumberField(
        widget=forms.TextInput(),
        required=True)
    token = forms.CharField(widget=forms.HiddenInput())
    verification_code = CharField(
        widget=forms.TextInput(attrs={'label': 'verification code'}),
        required=False,
    )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct phone_number"
        ),
        'inactive': _("This account is inactive."),
    }

    class Media:
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/intlTelInput.min.js',
            'fb_phoneauth/main.js',
        )
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/css/intlTelInput.css',)
        }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        self.TestingMode = 'true' if getattr(
            settings, 'FIREBASE_TESTING_MODE', False) else 'false'
        self.set_api_config()
        super().__init__(*args, **kwargs)

    def set_api_config(self):
        self.firebaseConfig = {
            "apiKey": getattr(settings, 'FIREBASE_API_KEY', ''),
            "authDomain": getattr(settings, 'FIREBASE_AUTH_DOMAIN', ''),
            "projectId": getattr(settings, 'FIREBASE_PROJECT_ID', ''),
            "storageBucket": getattr(settings, 'FIREBASE_STORAGE_BUCKET', ''),
            "messagingSenderId": getattr(settings, 'FIREBASE_MESSAGING_SENDER_ID', ''),
            "appId": getattr(settings, 'FIREBASE_APP_ID', '')
        }

    def clean(self):
        phone_number = self.cleaned_data.get('phone_number')
        token = self.cleaned_data.get('token')
        logger.debug(
            (F'cleaned: phone_number: {phone_number}, token: {token}')
        )
        if phone_number:
            phone_number = phone_number.as_e164
        self.user_cache = authenticate(
            self.request, phone_number=phone_number, token=token)
        if self.user_cache is None:
            raise self.get_invalid_login_error()
        return self.cleaned_data

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
        )

    def get_user(self):
        return self.user_cache

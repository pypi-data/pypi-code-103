from mad_notifications.utils import notificaion_unique_file_path
from django.db import models
from django.contrib.auth import get_user_model
from django.apps import apps
from mad_notifications.settings import notification_settings


# Create your models here.


class EmailTemplate(models.Model):
    id = models.BigAutoField(unique=True, primary_key=True)
    name = models.CharField(max_length=225, blank=False, null=False, help_text="Template Name")
    slug = models.SlugField(max_length=225, blank=False, null=False, unique=True, help_text="Unique Template identifer")
    content = models.TextField(blank=False, null=False, help_text='Templated content of the email. <a href="https://docs.djangoproject.com/en/dev/topics/templates/" target="_target">Refer to docs for more details</a>.')
    from_email = models.CharField(max_length=225, blank=True, null=True, help_text='For example: No Reply <noreply@example.com>')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-id']


class Device(models.Model):
    id = models.BigAutoField(unique=True, primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, blank=False, null=True)
    token = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

class Notification(models.Model):
    id = models.BigAutoField(unique=True, primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, blank=False, null=True)
    title = models.CharField(max_length=254, blank=False, null=False)
    content = models.TextField(blank=False, null=True)
    image = models.FileField(upload_to=notificaion_unique_file_path, blank=True, null=True)
    icon = models.FileField(upload_to=notificaion_unique_file_path, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    actions = models.JSONField(default=dict, blank=True, help_text="")
    data = models.JSONField(default=dict, blank=True, help_text="All keys and values in the dictionary must be strings.")
    template = models.ForeignKey(EmailTemplate, blank=True, null=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-id']



# Model methods
def get_notification_model():
    """Return the Notification model that is active in this project."""
    return apps.get_model(notification_settings.NOTIFICATION_MODEL)


def get_email_template_model():
    """Return the Notification model that is active in this project."""
    return apps.get_model(notification_settings.EMAIL_TEMPLATE_MODEL)


def get_device_model():
    """Return the Notification model that is active in this project."""
    return apps.get_model(notification_settings.DEVICE_MODEL)
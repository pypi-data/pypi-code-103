# from django.contrib import admin

# Register your models for the admin site here.

from django.contrib import admin

from marketmanager.models import Config, Order, Structure, Webhook, WatchConfig

from allianceauth.services.hooks import get_extension_logger

logger = get_extension_logger(__name__)

@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    pass

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass

@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    pass

@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    pass

@admin.register(WatchConfig)
class WatchConfigAdmin(admin.ModelAdmin):
    pass

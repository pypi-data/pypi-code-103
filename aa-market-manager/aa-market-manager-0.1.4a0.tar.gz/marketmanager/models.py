from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from eveuniverse.models import (
    EveSolarSystem,
    EveConstellation,
    EveRegion,
    EveType,
)


class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (("basic_access", "Can access this app"),)


class Config(models.Model):
    fetch_regions = models.ManyToManyField(EveRegion, verbose_name=_("Fetch Regions"))

    def save(self, *args, **kwargs):
        if not self.pk and Config.objects.exists():
            # Force a single object
            raise ValidationError('There is can be only one \
                                    AnalyticsIdentifier instance')
        self.pk = self.id = 1  # If this happens to be deleted and recreated, force it to be 1
        return super().save(*args, **kwargs)


class Order(models.Model):
    """An EVE Market Order"""
    order_id = models.PositiveBigIntegerField(
        _("Order ID"),
        help_text="Unique order ID",
        primary_key=True)
    eve_type = models.ForeignKey(
        EveType,
        verbose_name=_("Type"),
        on_delete=models.CASCADE)
    duration = models.PositiveIntegerField(
        _("Duration"),
        help_text="Number of days the order was valid for (starting from the issued date). An order expires at time issued + duration")
    is_buy_order = models.BooleanField(
        _("Buy Order"),
        default=False,
        help_text="True if the order is a bid (buy) order")
    issued = models.DateTimeField(
        _("Issued"),
        help_text="Date and time when this order was issued",
        auto_now=False,
        auto_now_add=False)
    location_id = models.PositiveBigIntegerField(
        _("Location ID"),
        help_text="ID of the location where order was placed")
    eve_solar_system = models.ForeignKey(
        EveSolarSystem,
        verbose_name=_("System"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,)
    eve_region = models.ForeignKey(
        EveRegion,
        verbose_name=_("Region"),
        on_delete=models.CASCADE)
    min_volume = models.PositiveIntegerField(
        _("Minimum Volume"),
        null=True,
        blank=True,
        help_text="For buy orders, the minimum quantity that will be accepted in a matching sell order")
    price = models.DecimalField(
        _("Price"),
        max_digits=20,
        decimal_places=2,
        help_text="Cost per unit for this order")
    escrow = models.DecimalField(
        _("Escrow"),
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="For buy orders, the amount of ISK in escrow")
    RANGE_CHOICES = [
        ('1', '1'), ('10', '10'), ('2', '2'), ('20', '20'), ('3', '3'),
        ('30', '30'), ('4', '4'), ('40', '40'), ('5', '5'),
        ('region', _('Region')),
        ('solarsystem', _('Solar System')),
        ('station', _('Station'))]
    range = models.CharField(
        _("Order Range"),
        max_length=20,
        choices=RANGE_CHOICES,
        help_text="Valid order range, numbers are ranges in jumps")
    volume_remain = models.PositiveIntegerField(
        _("Volume Remaining"),
        help_text="Quantity of items still required or offered")
    volume_total = models.PositiveIntegerField(
        _("Volume Total"),
        help_text="Quantity of items required or offered at time order was placed")
    is_corporation = models.BooleanField(
        _("Is Corporation"),
        default=False,
        help_text="Signifies whether the buy/sell order was placed on behalf of a corporation.")
    wallet_division = models.PositiveIntegerField(
        _("Wallet Division"),
        null=True,
        blank=True,
        help_text="The corporation wallet division used for this order.")
    issued_by_character = models.ForeignKey(
        EveCharacter,
        verbose_name=_("Character"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    issued_by_corporation = models.ForeignKey(
        EveCorporationInfo,
        verbose_name=_("Corporation"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,)
    STATE_CHOICES = [
        ('', ''),
        ('cancelled', _('Cancelled')),
        ('expired ', _('Expired'))]
    state = models.CharField(
        _("Order State"),
        max_length=20,
        choices=RANGE_CHOICES,
        help_text="Current order state, Only valid for Authenticated order History. Will not update from Public Market Data.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Structure(models.Model):
    """An EVE Online Upwell Structure"""
    structure_id = models.PositiveBigIntegerField(
        _("Structure ID"),
        primary_key=True)
    name = models.CharField(
        _("Name"),
        max_length=100)
    owner_id = models.IntegerField(_("Owner ID"))
    solar_system = models.ForeignKey(
        EveSolarSystem,
        verbose_name=_("Solar System"),
        on_delete=models.CASCADE)
    eve_type = models.ForeignKey(
        EveType,
        verbose_name=_(""),
        on_delete=models.CASCADE)
    pull_market = models.BooleanField(
        _("Pull Market Orders"),
        help_text="Useful to ignore specific structures for _reasons_",
        default=True)


class Webhook(models.Model):
    name = models.CharField(
        _("Name"),
        max_length=100)
    webhook = models.URLField(_("URL"), max_length=200)


class WatchConfig(models.Model):
    """Rules to Watch"""
    # Item Rules, Run once for each Item
    buy_order = models.BooleanField(_("Buy Order"))
    type = models.ManyToManyField(EveType, verbose_name=_("EVE Types"))
    # Location Rules, Combined
    location = models.ManyToManyField(Structure, verbose_name=_(""))
    solar_system = models.ManyToManyField(EveSolarSystem, verbose_name=_(""))
    constellation = models.ManyToManyField(EveConstellation, verbose_name=_(""))
    region = models.ManyToManyField(EveRegion, verbose_name=_(""))
    # Filter
    structure_type = models.ManyToManyField(EveType,
                                            help_text="Filter by structure Type/Size/Docking (ie, forts/keeps for cap fuel)",
                                            verbose_name=_("Structure Type Filter"),
                                            related_name="structure_type")
    # Comparators
    volume = models.IntegerField(_("Volume"),
                                 help_text="Set to Zero to check ANY/EVERY order against Price")
    price = models.IntegerField(_("Price"),
                                help_text="Set to Zero to check ANY/EVERY order against Volume")
    jita_compare_percent = models.IntegerField(_("Jita Comparison %"),
                                               help_text="If set ignores Flat price value")

    # Destinations

    webhooks = models.ManyToManyField(Webhook, verbose_name=_("Webhooks"))

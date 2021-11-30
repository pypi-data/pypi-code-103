"""
models
"""

from datetime import datetime

from django.db import models

from allianceauth.eveonline.models import EveCharacter
from allianceauth.groupmanagement.models import AuthGroup


class General(models.Model):
    """
    General module permissions
    """

    class Meta:
        """
        meta
        """

        verbose_name = "Fleet Finder"
        managed = False
        default_permissions = ()
        permissions = (
            ("access_fleetfinder", "Can access the Fleet Finder app"),
            ("manage_fleets", "Can manage fleets"),
        )


class Fleet(models.Model):
    """
    Fleet
    """

    fleet_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=50, default="")
    fleet_commander = models.ForeignKey(
        EveCharacter,
        on_delete=models.SET_NULL,
        related_name="+",
        default=None,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField()
    motd = models.TextField(blank=True, default="")
    is_free_move = models.BooleanField()

    groups = models.ManyToManyField(
        AuthGroup,
        related_name="restricted_groups",
        help_text="Group listed here will be able to join the fleet",
    )

    class Meta:
        """
        meta
        """

        default_permissions = ()


class FleetInformation(models.Model):
    """
    Fleet Information
    """

    fleet = models.ForeignKey(
        Fleet,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
        related_name="+",
    )
    ship_type_name = models.CharField(max_length=100)
    count = models.IntegerField()
    date = models.DateTimeField(default=datetime.now)

    class Meta:
        """
        meta
        """

        default_permissions = ()

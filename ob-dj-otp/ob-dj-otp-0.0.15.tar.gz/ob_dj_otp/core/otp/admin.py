from django.contrib import admin
from django.http import HttpRequest

from ob_dj_otp.core.otp.models import OneTruePairing


class OneTruePairingAdmin(admin.ModelAdmin):
    """ OneTruePairingAdmin
    """

    list_display = (
        "phone_number",
        "usage",
        "status",
        "created_at",
        "verification_code",
    )
    model = OneTruePairing

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: OneTruePairing = None
    ) -> bool:
        return False


admin.site.register(OneTruePairing, OneTruePairingAdmin)

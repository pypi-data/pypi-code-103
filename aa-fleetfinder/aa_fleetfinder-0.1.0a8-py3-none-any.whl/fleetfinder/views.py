"""
views
"""

from bravado.exception import HTTPNotFound

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.defaulttags import register
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from allianceauth.eveonline.evelinks.eveimageserver import character_portrait_url
from allianceauth.eveonline.models import EveCharacter
from allianceauth.groupmanagement.models import AuthGroup
from allianceauth.services.hooks import get_extension_logger
from esi.decorators import token_required

from fleetfinder import __title__
from fleetfinder.app_settings import avoid_cdn
from fleetfinder.models import Fleet
from fleetfinder.tasks import get_fleet_composition, open_fleet, send_fleet_invitation
from fleetfinder.utils import LoggerAddTag

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required()
@permission_required("fleetfinder.access_fleetfinder")
def dashboard(request):
    """
    dashboard view
    :param request:
    :return:
    """

    # groups = request.user.groups.all()
    # fleets = Fleet.objects.filter(Q(groups__group__in=groups) | Q(groups=None)).all()

    context = {
        # "fleets": fleets,
        "avoid_cdn": avoid_cdn(),  # AVOID_CDN setting
    }

    if "error_edit_fleet" in request.session:
        context["error"] = request.session["error_edit_fleet"].get("error", "")

        del request.session["error_edit_fleet"]

    logger.info(f"Module called by {request.user}")

    return render(request, "fleetfinder/dashboard.html", context)


@login_required()
@permission_required("fleetfinder.access_fleetfinder")
def ajax_dashboard(request) -> JsonResponse:
    """
    dashboard view
    :param request:
    :return:
    """

    data = list()
    groups = request.user.groups.all()
    fleets = Fleet.objects.filter(Q(groups__group__in=groups) | Q(groups=None)).all()

    for fleet in fleets:
        fleet_commander_name = fleet.fleet_commander.character_name
        fleet_commander_portrait = (
            '<img class="img-rounded eve-character-portrait" '
            'src="{portrait_url}" '
            'alt="{character_name}">'.format(
                portrait_url=character_portrait_url(
                    character_id=fleet.fleet_commander.character_id, size=32
                ),
                character_name=fleet_commander_name,
            )
        )
        fleet_commander_html = fleet_commander_portrait + fleet_commander_name

        button_join_url = reverse("fleetfinder:join_fleet", args=[fleet.fleet_id])
        button_join = (
            '<a href="{button_url}" '
            'class="btn btn-sm btn-default">{button_text}</a>'.format(
                button_url=button_join_url, button_text=_("Join Fleet")
            )
        )

        button_details = ""
        button_edit = ""

        if request.user.has_perm("fleetfinder.manage_fleets"):
            button_details_url = reverse(
                "fleetfinder:fleet_details", args=[fleet.fleet_id]
            )
            button_details = (
                '<a href="{button_url}" '
                'class="btn btn-sm btn-default">{button_text}</a>'.format(
                    button_url=button_details_url, button_text=_("View fleet details")
                )
            )

            button_edit_url = reverse("fleetfinder:edit_fleet", args=[fleet.fleet_id])
            button_edit = (
                '<a href="{button_url}" '
                'class="btn btn-sm btn-default">{button_text}</a>'.format(
                    button_url=button_edit_url, button_text=_("Edit Fleet advert")
                )
            )

        data.append(
            {
                "fleet_commander": {
                    "html": fleet_commander_html,
                    "sort": fleet_commander_name,
                },
                "fleet_name": fleet.name,
                "created_at": fleet.created_at,
                "join": button_join,
                "details": button_details,
                "edit": button_edit,
            }
        )

    return JsonResponse(data, safe=False)


@login_required()
@permission_required("fleetfinder.manage_fleets")
@token_required(
    scopes=(
        "esi-fleets.read_fleet.v1",
        "esi-fleets.write_fleet.v1",
    )
)
def create_fleet(request, token):
    """
    create fleet view
    :param request:
    :param token:
    :return:
    """

    if request.method == "POST":
        auth_groups = AuthGroup.objects.filter(internal=False).all()

        context = {}

        if "modified_fleet_data" in request.session:
            context["error"] = request.session["modified_fleet_data"].get("error", "")
            context["motd"] = request.session["modified_fleet_data"].get("motd", "")
            context["name"] = request.session["modified_fleet_data"].get("name", "")
            context["groups"] = request.session["modified_fleet_data"].get("groups", "")
            context["is_free_move"] = request.session["modified_fleet_data"].get(
                "free_move", ""
            )
            context["character_id"] = token.character_id
            context["auth_groups"] = auth_groups

            del request.session["modified_fleet_data"]
        else:
            context = {"character_id": token.character_id, "auth_groups": auth_groups}

        # AVOID_CDN setting
        context["avoid_cdn"] = avoid_cdn()

        logger.info(f"Fleet created by {request.user}")

        return render(request, "fleetfinder/create_fleet.html", context=context)

    return redirect("fleetfinder:dashboard")


@login_required()
@permission_required("fleetfinder.manage_fleets")
def edit_fleet(request, fleet_id):
    """
    fleet edit view
    :param request:
    :param fleet_id:
    :return:
    """

    fleet = Fleet.objects.get(fleet_id=fleet_id)
    auth_groups = AuthGroup.objects.filter(internal=False)

    context = {
        "character_id": fleet.fleet_commander.character_id,
        "auth_groups": auth_groups,
        "fleet": fleet,
        "avoid_cdn": avoid_cdn(),  # AVOID_CDN setting
    }

    logger.info(
        "Fleet {fleet_id} edit view by {user}".format(
            fleet_id=fleet_id, user=request.user
        )
    )

    return render(request, "fleetfinder/edit_fleet.html", context=context)


@login_required()
@permission_required("fleetfinder.access_fleetfinder")
def join_fleet(request, fleet_id):
    """
    join fleet view
    :param request:
    :param fleet_id:
    :return:
    """

    context = {}
    groups = request.user.groups.all()
    fleet = Fleet.objects.filter(
        Q(groups__group__in=groups) | Q(groups=None), fleet_id=fleet_id
    ).count()

    if fleet == 0:
        return redirect("fleetfinder:dashboard")

    if request.method == "POST":
        character_ids = request.POST.getlist("character_ids", [])
        send_fleet_invitation.delay(character_ids, fleet_id)

        return redirect("fleetfinder:dashboard")

    characters = (
        EveCharacter.objects.filter(character_ownership__user=request.user)
        .select_related()
        .order_by("character_name")
    )

    context["characters"] = characters

    # AVOID_CDN setting
    context["avoid_cdn"] = avoid_cdn()

    return render(request, "fleetfinder/join_fleet.html", context=context)


@login_required()
@permission_required("fleetfinder.manage_fleets")
def save_fleet(request):
    """
    save fleet
    :param request:
    :return:
    """

    if request.method == "POST":
        free_move = request.POST.get("free_move", False)

        if free_move == "on":
            free_move = True

        motd = request.POST.get("motd", "")
        name = request.POST.get("name", "")
        groups = request.POST.getlist("groups", [])

        try:
            open_fleet(request.POST["character_id"], motd, free_move, name, groups)
        except HTTPNotFound as ex:
            if request.POST.get("origin", "") == "edit":
                # Here ccp return "character not in fleet".
                # Instead push our own message to be clearer
                request.session["error_edit_fleet"] = {
                    "error": "Fleet advert is no longer valid"
                }

                return redirect("fleetfinder:dashboard")

            if request.POST.get("origin", "") == "create":
                request.session["modified_fleet_data"] = {
                    "error": ex.swagger_result["error"],
                    "motd": motd,
                    "name": name,
                    "free_move": free_move,
                    "groups": groups,
                }

                return redirect("fleetfinder:create_fleet")

    return redirect("fleetfinder:dashboard")


@login_required()
@permission_required("fleetfinder.manage_fleets")
def fleet_details(request, fleet_id):
    """
    fleet details view
    :param request:
    :param fleet_id:
    :return:
    """

    # fleet = get_fleet_composition(fleet_id)

    context = {
        # "fleet": fleet,
        # "fleet_details": fleet.fleet,
        # "aggregate": fleet.aggregate,
        # "differential": fleet.differential,
        "avoid_cdn": avoid_cdn(),  # AVOID_CDN setting
        "fleet_id": fleet_id,
    }

    logger.info(
        "Fleet {fleet_id} details view called by {user}".format(
            fleet_id=fleet_id, user=request.user
        )
    )

    return render(request, "fleetfinder/fleet_details.html", context=context)


@login_required()
@permission_required("fleetfinder.manage_fleets")
def ajax_fleet_details(request, fleet_id) -> JsonResponse:
    """

    :param request:
    :param fleet_id:
    """

    fleet = get_fleet_composition(fleet_id)

    data = {
        "fleet_member": [],
        # "differential": fleet.differential,
        "fleet_composition": [],
    }

    # data = {"differential": [fleet.differential]}
    for member in fleet.fleet:
        data["fleet_member"].append(member)

    for ship, number in fleet.aggregate.items():
        data["fleet_composition"].append({"ship_type_name": ship, "number": number})

    return JsonResponse(data, safe=False)


@register.filter
def get_item(dictionary, key):
    """
    little helper: get a key from a dictionary
    :param dictionary:
    :param key:
    :return:
    """

    return dictionary.get(key)

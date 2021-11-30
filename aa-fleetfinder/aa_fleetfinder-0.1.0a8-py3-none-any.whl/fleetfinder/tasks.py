"""
tasks
"""

from concurrent.futures import ThreadPoolExecutor, as_completed

from bravado.exception import (
    HTTPBadGateway,
    HTTPGatewayTimeout,
    HTTPNotFound,
    HTTPServiceUnavailable,
)
from celery import shared_task

from django.core.cache import cache
from django.utils import timezone

from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger
from allianceauth.services.tasks import QueueOnce
from esi.models import Token

from fleetfinder import __title__
from fleetfinder.models import Fleet
from fleetfinder.providers import esi
from fleetfinder.utils import LoggerAddTag

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


ESI_ERROR_LIMIT = 50
ESI_TIMEOUT_ONCE_ERROR_LIMIT_REACHED = 60
ESI_MAX_RETRIES = 3


CACHE_KEY_NOT_IN_FLEET_ERROR = (
    "fleetfinder_task_check_fleet_adverts_error_counter_not_in_fleet_"
)
CACHE_KEY_NO_FLEET_ERROR = (
    "fleetfinder_task_check_fleet_adverts_error_counter_no_fleet_"
)
CACHE_KEY_FLEET_CHANGED_ERROR = (
    "fleetfinder_task_check_fleet_adverts_error_counter_fleet_changed_"
)
CACHE_MAX_ERROR_COUNT = 3


# params for all tasks
TASK_DEFAULT_KWARGS = {
    "time_limit": 120,  # stop after 2 minutes
}

# params for tasks that make ESI calls
TASK_ESI_KWARGS = {
    **TASK_DEFAULT_KWARGS,
    **{
        "autoretry_for": (
            OSError,
            HTTPBadGateway,
            HTTPGatewayTimeout,
            HTTPServiceUnavailable,
        ),
        "retry_kwargs": {"max_retries": ESI_MAX_RETRIES},
        "retry_backoff": True,
    },
}


@shared_task
def open_fleet(character_id, motd, free_move, name, groups):
    """
    open a fleet
    :param character_id:
    :param motd:
    :param free_move:
    :param name:
    :param groups:
    :return:
    """

    required_scopes = ["esi-fleets.read_fleet.v1", "esi-fleets.write_fleet.v1"]

    esi_client = esi.client
    token = Token.get_token(character_id, required_scopes)

    fleet_result = esi_client.Fleets.get_characters_character_id_fleet(
        character_id=token.character_id, token=token.valid_access_token()
    ).result()
    fleet_id = fleet_result.pop("fleet_id")
    fleet_role = fleet_result.pop("role")

    if fleet_id is None or fleet_role is None or fleet_role != "fleet_commander":
        return

    fleet_commander = EveCharacter.objects.get(character_id=token.character_id)

    fleet = Fleet(
        fleet_id=fleet_id,
        created_at=timezone.now(),
        motd=motd,
        is_free_move=free_move,
        fleet_commander=fleet_commander,
        name=name,
    )
    fleet.save()
    fleet.groups.set(groups)

    esi_fleet = {"is_free_move": free_move, "motd": motd}
    esi_client.Fleets.put_fleets_fleet_id(
        fleet_id=fleet_id, token=token.valid_access_token(), new_settings=esi_fleet
    ).result()


@shared_task
def send_fleet_invitation(character_ids, fleet_id):
    """
    send a fleet invitation through the eve client
    :param character_ids:
    :param fleet_id:
    """

    required_scopes = ["esi-fleets.write_fleet.v1"]
    fleet = Fleet.objects.get(fleet_id=fleet_id)
    fleet_commander_token = Token.get_token(
        fleet.fleet_commander.character_id, required_scopes
    )
    _processes = []

    with ThreadPoolExecutor(max_workers=50) as ex:
        for _chracter_id in character_ids:
            _processes.append(
                ex.submit(
                    send_invitation,
                    character_id=_chracter_id,
                    fleet_commander_token=fleet_commander_token,
                    fleet_id=fleet_id,
                )
            )

    for item in as_completed(_processes):
        _ = item.result()


@shared_task
def send_invitation(character_id, fleet_commander_token, fleet_id):
    """
    open the fleet invite window in the eve client
    :param character_id:
    :param fleet_commander_token:
    :param fleet_id:
    """

    esi_client = esi.client
    invitation = {"character_id": character_id, "role": "squad_member"}

    esi_client.Fleets.post_fleets_fleet_id_members(
        fleet_id=fleet_id,
        token=fleet_commander_token.valid_access_token(),
        invitation=invitation,
    ).result()


def close_esi_fleet(fleet: Fleet, reason: str) -> None:
    """
    closing registered fleet
    :param fleet:
    :param reason:
    """

    logger.info(
        "Closing fleet with ID {fleet_id}. Reason: {reason}".format(
            fleet_id=fleet.fleet_id, reason=reason
        )
    )

    fleet.delete()


def esi_fleetadvert_error_handling(
    cache_key: str, fleet: Fleet, logger_message: str
) -> None:
    """
    ESI error handling
    :param cache_key:
    :param fleet:
    :param logger_message:
    """

    if int(cache.get(cache_key + str(fleet.fleet_id))) < CACHE_MAX_ERROR_COUNT:
        error_count = int(cache.get(cache_key + str(fleet.fleet_id)))

        error_count += 1

        logger.info(
            '"{logger_message}" Error Count: {error_count}.'.format(
                logger_message=logger_message, error_count=error_count
            )
        )

        cache.set(
            cache_key + str(fleet.fleet_id),
            str(error_count),
            75,
        )
    else:
        close_esi_fleet(fleet=fleet, reason=logger_message)


def init_error_caches(fleet: Fleet) -> None:
    """
    initialize error caches
    :param fleet:
    """

    if cache.get(CACHE_KEY_FLEET_CHANGED_ERROR + str(fleet.fleet_id)) is None:
        cache.set(CACHE_KEY_FLEET_CHANGED_ERROR + str(fleet.fleet_id), "0", 75)

    if cache.get(CACHE_KEY_NO_FLEET_ERROR + str(fleet.fleet_id)) is None:
        cache.set(CACHE_KEY_NO_FLEET_ERROR + str(fleet.fleet_id), "0", 75)

    if cache.get(CACHE_KEY_NOT_IN_FLEET_ERROR + str(fleet.fleet_id)) is None:
        cache.set(CACHE_KEY_NOT_IN_FLEET_ERROR + str(fleet.fleet_id), "0", 75)


@shared_task(**{**TASK_ESI_KWARGS}, **{"base": QueueOnce})
def check_fleet_adverts():
    """
    scheduled task
    check for fleets adverts
    """

    required_scopes = ["esi-fleets.read_fleet.v1", "esi-fleets.write_fleet.v1"]

    esi_client = esi.client

    fleets = Fleet.objects.all()

    fleet_count = fleets.count()

    logger.info(
        "{fleet_count} registered fleets found. {processing_text}".format(
            fleet_count=fleet_count,
            processing_text="Processing ..."
            if fleet_count > 0
            else "Nothing to do ...",
        )
    )

    if fleet_count > 0:
        for fleet in fleets:
            init_error_caches(fleet=fleet)

            logger.info(
                "Processing information for fleet with ID {fleet_id}".format(
                    fleet_id=fleet.fleet_id
                )
            )

            token = Token.get_token(fleet.fleet_commander.character_id, required_scopes)

            try:
                fleet_result = esi_client.Fleets.get_characters_character_id_fleet(
                    character_id=token.character_id, token=token.valid_access_token()
                ).result()

                fleet_id = fleet_result["fleet_id"]

                if fleet_id != fleet.fleet_id:
                    esi_fleetadvert_error_handling(
                        cache_key=CACHE_KEY_FLEET_CHANGED_ERROR,
                        fleet=fleet,
                        logger_message="FC switched to another fleet",
                    )

            except HTTPNotFound:
                esi_fleetadvert_error_handling(
                    cache_key=CACHE_KEY_NOT_IN_FLEET_ERROR,
                    fleet=fleet,
                    logger_message=(
                        "FC is not in the registered fleet anymore or "
                        "fleet is no longer available."
                    ),
                )

            except Exception:
                esi_fleetadvert_error_handling(
                    cache_key=CACHE_KEY_NO_FLEET_ERROR,
                    fleet=fleet,
                    logger_message="Registered fleet is no longer available.",
                )


@shared_task
def get_fleet_composition(fleet_id):
    """
    getting the fleet composition
    :param fleet_id:
    :return:
    """

    required_scopes = ["esi-fleets.read_fleet.v1", "esi-fleets.write_fleet.v1"]

    esi_client = esi.client

    fleet = Fleet.objects.get(fleet_id=fleet_id)
    token = Token.get_token(fleet.fleet_commander.character_id, required_scopes)
    fleet_infos = esi_client.Fleets.get_fleets_fleet_id_members(
        fleet_id=fleet_id, token=token.valid_access_token()
    ).result()

    characters = {}
    systems = {}
    ship_type = {}

    for member in fleet_infos:
        characters[member["character_id"]] = ""
        systems[member["solar_system_id"]] = ""
        ship_type[member["ship_type_id"]] = ""

    ids = []
    ids.extend(list(characters.keys()))
    ids.extend(list(systems.keys()))
    ids.extend(list(ship_type.keys()))

    ids_to_name = esi_client.Universe.post_universe_names(ids=ids).result()

    for member in fleet_infos:
        index_character = [x["id"] for x in ids_to_name].index(member["character_id"])
        member["character_name"] = ids_to_name[index_character]["name"]

        index_solar_system = [x["id"] for x in ids_to_name].index(
            member["solar_system_id"]
        )
        member["solar_system_name"] = ids_to_name[index_solar_system]["name"]

        index_ship_type = [x["id"] for x in ids_to_name].index(member["ship_type_id"])
        member["ship_type_name"] = ids_to_name[index_ship_type]["name"]

    aggregate = get_fleet_aggregate(fleet_infos)

    # differential = dict()
    #
    # for key, value in aggregate.items():
    #     fleet_info_agg = FleetInformation.objects.filter(
    #         fleet__fleet_id=fleet_id, ship_type_name=key
    #     )
    #
    #     if fleet_info_agg.count() > 0:
    #         differential[key] = value - fleet_info_agg.latest("date").count
    #     else:
    #         differential[key] = value
    #
    #     FleetInformation.objects.create(fleet=fleet, ship_type_name=key, count=value)

    return FleetViewAggregate(
        fleet_infos,
        aggregate,
        # differential,
    )


@shared_task
def get_fleet_aggregate(fleet_infos):
    """
    getting aggregate numbers for fleet composition
    :param fleet_infos:
    :return:
    """

    counts = dict()

    for member in fleet_infos:
        type_ = member.get("ship_type_name")

        if type_ in counts:
            counts[type_] += 1
        else:
            counts[type_] = 1

    return counts


class FleetViewAggregate:
    """
    helper class
    """

    def __init__(
        self,
        fleet,
        aggregate,
        # differential,
    ):
        self.fleet = fleet
        self.aggregate = aggregate
        # self.differential = differential

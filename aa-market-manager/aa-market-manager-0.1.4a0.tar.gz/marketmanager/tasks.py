from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from celery import shared_task

from allianceauth.services.hooks import get_extension_logger
from discord.embeds import Embed
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from esi.models import Token

from eveuniverse.models import (
    EveSolarSystem,
    EveRegion,
    EveType,
)

from marketmanager.models import WatchConfig, Config, Order, Structure

from marketmanager.providers import (
    get_markets_region_id_orders,
    get_characters_character_id_orders,
    get_corporations_corporation_id_orders,
    get_universe_structures,
    get_universe_structures_structure_id,
    get_corporations_corporation_id_structures
)
from marketmanager.task_helpers import get_corp_token, get_random_market_token

logger = get_extension_logger(__name__)


def discord_bot_active() -> bool:
    return apps.is_installed("aadiscordbot")


if discord_bot_active():
    import aadiscordbot.tasks


@shared_task
def fetch_public_market_orders():
    """Fetch&Save Public Market Orders for configured regions
    bulk calls fetch_markets_region_id_orders(region_id: int)"""
    for region in Config.objects.get(id=1).fetch_regions.all():
        fetch_markets_region_id_orders.delay(region.id)


@shared_task
def fetch_markets_region_id_orders(region_id: int):
    for order in get_markets_region_id_orders(region_id):

        order_eve_type, order_eve_type_fetched = EveType.objects.get_or_create_esi(
            id=order["type_id"],
            enabled_sections=[EveType.Section.MARKET_GROUPS]
        )
        order_eve_solar_system, order_eve_solar_system_fetched = EveSolarSystem.objects.get_or_create_esi(
            id=order["system_id"]
        )

        Order.objects.update_or_create(
            order_id=order["order_id"],
            defaults={
                'eve_type': order_eve_type,
                'duration': order["duration"],
                'is_buy_order': order["is_buy_order"],
                'issued': order["issued"],
                'location_id': order["location_id"],
                'min_volume': order["min_volume"],
                'price': order["price"],
                'range': order["range"],
                'eve_solar_system': order_eve_solar_system,
                'eve_region': order_eve_solar_system.eve_constellation.eve_region,
                'volume_remain': order["volume_remain"],
                'volume_total': order["volume_total"]},
        )


@shared_task
def fetch_all_character_orders():
    """Fetch&Save every Characters Market Orders
    bulk calls fetch_characters_character_id_orders(character_id)"""

    character_ids = Token.objects.values_list('character_id').require_scopes(
        ["esi-markets.read_character_orders.v1"])
    unique_character_ids = list(dict.fromkeys(character_ids))
    for character_id in unique_character_ids:
        fetch_characters_character_id_orders.delay(character_id[0])


@shared_task
def fetch_characters_character_id_orders(character_id: int):
    """Fetch&Save a single Characters Market Orders
    bulk called by fetch_all_character_orders()

    Parameters
    ----------
    corporation_id: int
        Should match a valid Character ID"""
    for order in get_characters_character_id_orders(character_id):

        order_eve_type, order_eve_type_fetched = EveType.objects.get_or_create_esi(
            id=order["type_id"],
            enabled_sections=[EveType.Section.MARKET_GROUPS]
        )
        order_eve_region, order_eve_region_fetched = EveRegion.objects.get_or_create_esi(
            id=order["region_id"]
        )
        if order["is_buy_order"] is None:
            order_is_buy_order = False
        else:
            order_is_buy_order = True

        Order.objects.update_or_create(
            order_id=order["order_id"],
            defaults={
                'eve_type': order_eve_type,
                'duration': order["duration"],
                'is_buy_order': order_is_buy_order,
                'is_corporation': order["is_corporation"],
                'issued': order["issued"],
                'location_id': order["location_id"],
                'eve_region': order_eve_region,
                'min_volume': order["min_volume"],
                'price': order["price"],
                'escrow': order["escrow"],
                'range': order["range"],
                'volume_remain': order["volume_remain"],
                'volume_total': order["volume_total"]},
        )


@shared_task
def fetch_all_corporation_orders():
    """Fetch&Save every Corporations Market Orders
    bulk calls fetch_corporations_corporation_id_orders(corporation_id)"""
    for corporation in EveCorporationInfo.objects.all():
        fetch_corporations_corporation_id_orders.delay(corporation.corporation_id)


@shared_task
def fetch_corporations_corporation_id_orders(corporation_id: int):
    """Fetch&Save a Corporations Market Orders
    Is Bulk-Called by fetch_all_corporation_orders()

    Parameters
    ----------
    corporation_id: int
        Should match a valid Corporation ID"""
    scopes = ["esi-markets.read_corporation_orders.v1"]
    req_roles = ["Accountant", "Trader"]

    token = get_corp_token(corporation_id, scopes, req_roles)
    if token is False:
        logger.error(f"No Token for Corporation {corporation_id}")
        return

    for order in get_corporations_corporation_id_orders(corporation_id, token):

        order_eve_type, order_eve_type_fetched = EveType.objects.get_or_create_esi(
            id=order["type_id"],
            enabled_sections=[EveType.Section.MARKET_GROUPS]
        )
        order_eve_corporation = EveCorporationInfo.objects.get(
            corporation_id=corporation_id
        )
        order_eve_region, order_eve_region_fetched = EveRegion.objects.get_or_create_esi(
            id=order["region_id"]
        )
        try:
            order_eve_character = EveCharacter.objects.get(
                character_id=order["issued_by"]
            )
        except ObjectDoesNotExist:
            EveCharacter.objects.create_character(order["issued_by"])
            order_eve_character = EveCharacter.objects.get(
                character_id=order["issued_by"]
            )

        if order["is_buy_order"] is None:
            order_is_buy_order = False
        else:
            order_is_buy_order = True

        Order.objects.update_or_create(
            order_id=order["order_id"],
            defaults={
                'eve_type': order_eve_type,
                'duration': order["duration"],
                'is_buy_order': order_is_buy_order,
                'is_corporation': True,
                'issued': order["issued"],
                'issued_by_character': order_eve_character,
                'issued_by_corporation': order_eve_corporation,
                'wallet_division': order["wallet_division"],
                'location_id': order["location_id"],
                'eve_region': order_eve_region,
                'min_volume': order["min_volume"],
                'price': order["price"],
                'escrow': order["escrow"],
                'range': order["range"],
                'volume_remain': order["volume_remain"],
                'volume_total': order["volume_total"]},
        )


@shared_task()
def fetch_public_structures():
    for structure_id in get_universe_structures(filter="market"):
        structure = get_universe_structures_structure_id(
            structure_id, get_random_market_token())

        structure_eve_solar_system, structure_eve_solar_system_fetched = EveSolarSystem.objects.get_or_create_esi(
            id=structure["solar_system_id"]
        )
        structure_eve_type, structure_eve_type_fetched = EveType.objects.get_or_create_esi(
            id=structure["type_id"],
            enabled_sections=[EveType.Section.MARKET_GROUPS]
        )

        Structure.objects.update_or_create(
            structure_id=structure_id,
            defaults={
                'name': structure["name"],
                'owner_id': structure["owner_id"],
                'solar_system': structure_eve_solar_system,
                'eve_type': structure_eve_type
            }
        )


@shared_task()
def fetch_all_corporations_structures():
    for corporation in EveCorporationInfo.objects.all():
        fetch_corporations_corporation_id_structures.delay(corporation.corporation_id)


@shared_task()
def fetch_corporations_corporation_id_structures(corporation_id: int):
    scopes = ["esi-corporations.read_structures.v1"]
    req_roles = ["Station_Manager"]

    token = get_corp_token(corporation_id, scopes, req_roles)
    if token is False:
        logger.error(f"No Token for Corporation {corporation_id}")
        return

    for structure in get_corporations_corporation_id_structures(corporation_id, token):
        if structure["services"]["market"] == "Offline" or "Online":
            structure_eve_solar_system, structure_eve_solar_system_fetched = EveSolarSystem.objects.get_or_create_esi(
                id=structure["solar_system_id"]
            )
            structure_eve_type, structure_eve_type_fetched = EveType.objects.get_or_create_esi(
                id=structure["type_id"],
                enabled_sections=[EveType.Section.MARKET_GROUPS]
            )
            Structure.objects.update_or_create(
                structure_id=structure["structure_id"],
                defaults={
                    'name': structure["name"],
                    'owner_id': structure["corporation_id"],
                    'solar_system': structure_eve_solar_system,
                    'eve_type': structure_eve_type
                }
            )


# @shared_task
# def run_market_checks():
#     # filter by unique typeids in Watchconfig
#     for type in WatchConfig.objects.values("Type").distinct():
#         # for each typeID, process its WatchConfig

#         embed = template_discord_embed(type)
#         # idk do stuff

#         #

#         # Comparators

#         # Volume
#         embed.add_field("Volume Insufficient",
#                         f"{config.locations}: {current_quant}/{config.volume}")
#         # Price
#         embed.add_field("Overpriced Order",
#                         f"{config.locations}: {current_quant}/{config.volume}")
#         # Jita %
#     return True


# def template_discord_embed(evetype: EveType) -> Embed:
#     """Prep a standard Embed template, WatchConfigs may further modify/add fields"""
#     embed = Embed

#     embed.title = f"AA Market Manager: {evetype.name}"
#     embed.thumbnail = evetype.icon_url
#     embed.color = "Red"
#     embed.description = "The Following Rules were Failed"

#     return embed

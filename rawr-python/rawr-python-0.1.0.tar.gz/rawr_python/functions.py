from importlib.resources import path
from typing import Literal

import requests
import yaml
from pydantic import parse_obj_as

from . import resources as resources_module
from .classes import Match, Summoner, Timeline
from .utils import renamestyle_keys

with path(resources_module, "resources.yaml") as yaml_file:
    with open(yaml_file) as f:
        queues = yaml.safe_load(f)["queues"]


def get_summoner(headers: dict[str, str], account_name: str) -> Summoner:
    url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{account_name}"
    resp = requests.get(url, headers=headers).json()
    summoner_raw = renamestyle_keys(resp)
    summoner = parse_obj_as(Summoner, summoner_raw)

    return summoner


def get_match_ids(
    headers: dict[str, str],
    player_id: str,
    queue: Literal["solo_duo", "flex", "clash"],
    num_games: int,
) -> list[str]:
    url = (
        f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{player_id}/"
        f"ids?queue={queues[queue]}&start=0&count={num_games}"
    )
    match_ids = requests.get(url, headers=headers).json()

    return match_ids


def get_match(headers: dict[str, str], match_id: str) -> Match:
    url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
    resp = requests.get(url, headers=headers).json()
    match_raw = renamestyle_keys(resp)
    match = parse_obj_as(Match, match_raw)

    return match


def get_timeline(headers: dict[str, str], match_id: str) -> Timeline:
    url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
    resp = requests.get(url, headers=headers).json()
    timeline_raw = renamestyle_keys(resp)
    timeline = parse_obj_as(Timeline, timeline_raw)

    return timeline


def get_timelines(headers: dict[str, str], match_ids: list[str]) -> list[Timeline]:
    return [get_timeline(headers, match_id) for match_id in match_ids]

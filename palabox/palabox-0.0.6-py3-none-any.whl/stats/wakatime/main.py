"""Wakatime stats."""

import json
from dataclasses import asdict
from datetime import datetime

import dacite
import requests

from palabox.stats.wakatime.types import WakatimeStats
from palabox.utils import json_converter


def get_user_stats(token: str) -> WakatimeStats:
    """Get user stats."""
    response = requests.get(
        f"https://wakatime.com/share/{token}.json",
    )
    if response.ok:
        data: WakatimeStats = dacite.from_dict(
            WakatimeStats,
            response.json(),
            dacite.Config(
                {datetime: lambda dateStr: datetime.strptime(dateStr, "%Y-%m-%dT%H:%M:%S%z")}
            ),
        )
        return data

    raise ValueError(f"Problem with the request {response}, '{response.content.decode()}'")


if __name__ == "__main__":
    data = get_user_stats(
        "@5fba56dd-c3e1-4bec-9596-fd1565702df9/b026f6b2-5e5f-4a7e-8d1b-8039ee9a6aa6"
    )
    with open("test.json", "w", encoding="utf-8") as file:
        json.dump(asdict(data), file, indent=2, default=json_converter)

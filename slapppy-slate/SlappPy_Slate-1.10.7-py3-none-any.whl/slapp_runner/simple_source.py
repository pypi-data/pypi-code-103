import functools
import re
from typing import Dict, List, Optional, Tuple

import battlefy_toolkit.org_lists.splatoon_orgs
from slapp_py.helpers.str_helper import truncate, escape_characters

# Mapping takes a list of tournament names and gives an organisation name
SOURCE_ORGANISER_MAPPING: Dict[str, List[str]] = {
    'area-cup': ['-area-cup-'],
    'asquidmin': ['-turtlement-'],
    'deep-sea-solutions': ['megalodon-cup-', '-minnow-cup-', 'trick-no-treat'],
    'fresh-start-cup': ['-fresh-start-cup-'],
    'gamesetmatch': ['-gsm-'],
    'inkling-performance-labs': ['-low-ink-', '-testing-grounds-', '-swim-or-sink-'],
    'inktv': ['-bns-', '-swl-winter-snowflake-', '-splatoon-world-league-', '-inktv-open-', '-extrafaganza-', '-inkvitational-'],
    'little-squid-league': ['-little-squid-league-', '-little-squid-league-invitational-'],
    'midway-ink-tour': ['-midway-'],
    'sitback-saturdays': ['-sitback-saturdays-'],
    'splatcom': ['-armas-random-', '-duelos-', '-dúos-dittos-', 'splatcom-', '-suizo-latino-', '-torneo-de-', '-torneo-festivo-'],
    'splatoon2': ['-splatoon-2-north-american-online-open-'],
    'splatoon-amateur-circuit': ['-sac-tournament-', '-season-3-tournament-3-youre-an', '-season-3-tournament-2-hey-now'],
    'squid-south': ['squid-south-2v2-', '-squid-souths-halloween-2v2-'],
    'squid-spawning-grounds': ['-squid-spawning-grounds-'],
    'squidboards-splatoon-2-community-events': ['-sqss-', '-squidboards-splat-series-'],
    'swift-second-saturdays': ['-sss-'],
}


class SimpleSource:
    id: str
    name: str
    date: str
    organiser: Optional[str]
    tournament_name: Optional[str]
    url: Optional[str]

    def __init__(self, id: str, name: str):
        """Constructor for SimpleSource"""
        self.id = id
        self.name = name
        (self.date, self.organiser, self.tournament_name, self.url) = self.initialise(name)

    @staticmethod
    def from_dict(obj: dict) -> 'SimpleSource':
        assert isinstance(obj, dict)
        source_id, source_name = obj.popitem()
        return SimpleSource(id=source_id, name=source_name)

    def to_dict(self) -> dict:
        return {self.id: self.name}

    def __str__(self):
        return self.name

    @staticmethod
    @functools.cache
    def initialise(source_name: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """Initialise the simple source's (date, organiser, tournament name, url)."""
        if not source_name:
            return None, None, None, None

        if len(source_name) > 11 and source_name.count('-') > 3:
            date = source_name[0:10].strip('- ')
            default_tourney_name = source_name[11:].strip('- ')
        else:
            date = None
            default_tourney_name = None

        id_at_the_end_match = re.search("-+([0-9a-fA-F]+)$", source_name, re.I)
        if id_at_the_end_match:
            # We always want to grab the last match as the id is at the end of the source name.
            guid = id_at_the_end_match.groups()[-1]
            url = f"https://battlefy.com/_/_/{guid}/info"
        else:
            url = None

        for organiser, tourneys in SOURCE_ORGANISER_MAPPING.items():
            for tournament_name in tourneys:
                if tournament_name in source_name:
                    return date, organiser.strip('- '), tournament_name.strip('- '), url
        else:
            for organiser in battlefy_toolkit.org_lists.splatoon_orgs.ORG_SLUGS:
                if f"-{organiser}-" in source_name:
                    tournament_name = SimpleSource._strip_source_id(default_tourney_name.replace(f"-{organiser}-", ''))
                    return date, organiser.strip('- '), tournament_name.strip('- '), url

        return date, None, default_tourney_name, url

    def get_linked_date_display(self) -> str:
        """Return a markdown link with the truncated source date if available,
        otherwise return its truncated_name only."""
        link = self.url
        if self.date:
            text = truncate(escape_characters(self.date), 16, '…')
        else:
            text = self.truncated_name
        return f"[{text}]({link})" if link else text

    def get_linked_name_display(self) -> str:
        """Return a markdown link with the truncated source name (date-name) if available,
        otherwise return its truncated_name only."""
        link = self.url
        text = self.truncated_name
        return f"[{text}]({link})" if link else text

    @property
    def truncated_name(self):
        """The source with the id removed and truncated down."""
        if self.date and self.tournament_name:
            display_name = self.date + '-' + self.tournament_name
        else:
            display_name = self._strip_source_id(self.name)
        return truncate(escape_characters(display_name), 100, '…')

    @staticmethod
    def _strip_source_id(source):
        return re.sub("-+[0-9a-fA-F]+$", '', source)

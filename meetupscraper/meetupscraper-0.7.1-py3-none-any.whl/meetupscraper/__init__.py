import urllib.parse
import logging
import dataclasses
import datetime

import dateutil.parser
import lxml.html
import requests


LOGGER = logging.getLogger("meetupscraper")


@dataclasses.dataclass(frozen=True)
class Venue:
    name: str
    street: str


@dataclasses.dataclass(frozen=True)
class Event:
    url: str
    num_attendees: int
    date: datetime.datetime
    title: str
    group_name: str
    description: list
    venue: Venue


def _get_venue(html):
    h = lxml.html.fromstring(html)
    try:
        street = h.xpath('//* [@data-testid="location-info"]/text()')[0]
    except IndexError:
        try:
            street = h.xpath(
                '//* [@class="venueDisplay-venue-address '
                'text--secondary text--small text--wrapNice"]/text()'
            )[0]
        except IndexError:
            street = ""
    try:
        venue_name = h.xpath(
            '//* [@data-event-label="event-location"]/text()'
        )[0]
    except IndexError:
        try:
            venue_name = h.xpath(
                '//* [@class="wrap--singleLine--truncate"]/text()'
            )[0]
        except IndexError:
            LOGGER.debug("html=%r", html)
            raise
    return Venue(
        name=venue_name,
        street=street,
    )


def get_upcoming_events(meetup_name):
    prefix = "https://www.meetup.com/" + urllib.parse.quote(meetup_name)
    url = prefix + "/events/rss/"
    LOGGER.info("Looking up %r", url)
    s = requests.get(url).text
    rss = lxml.etree.fromstring(s.encode())

    timestamps = []
    for item in rss.xpath("//item"):
        description = item.xpath(".//description/text()")[0]
        h = lxml.html.fromstring(description)
        p = h.xpath("//p/text()")
        meetup_url = p.pop()
        num_attendees = int(p.pop())
        date = dateutil.parser.parse(p.pop())
        now = datetime.datetime.today()
        if date < now:
            date = date.replace(year=date.year + 1)
        group_name = p[0]
        p.pop()  # discard address
        LOGGER.info("Looking up %r", meetup_url)
        yield Event(
            title=item.xpath(".//title/text()")[0],
            num_attendees=num_attendees,
            date=date,
            url=meetup_url,
            group_name=group_name,
            description=p[1:],
            venue=_get_venue(requests.get(meetup_url).text),
        )

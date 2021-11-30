"""pymindergas package."""

import json
import logging
import requests

from datetime import date as dt
from dateutil.parser import parse

LOG = logging.getLogger(__name__)

class Mindergas:
    """Mindergas Class."""

    REQUEST_URL = "https://www.mindergas.nl/api/meter_readings"

    def __init__(self):
        """Initialize."""

    def postReading(self, auth_token, reading, date=None):
        """Post meter reading for a specific date."""

        headers = {
            "Content-Type": "application/json",
            "AUTH-TOKEN": auth_token,
        }
        LOG.debug(headers)

        if date == None:
            date = dt.today().strftime("%Y-%m-%d")
        else:
            try:
                date = parse(date).strftime("%Y-%m-%d")
            except ValueError:
                LOG.error("Invalid date: %s", date)
                return False
        LOG.debug("Date: %s", date)

        data = {
            "date": date,
            "reading": reading,
        }
        data = json.dumps(data)
        LOG.debug(data)

        try:
            response = requests.post(self.REQUEST_URL, headers=headers, data=data)
        except:
            LOG.error("Error when requesting response.")
            return False
        else:
            LOG.debug("Status code: %s", response.status_code)

            if response.status_code == 201:
                LOG.info("Reading posted.")
                return True
            else:
                LOG.error("Code {}: {}".format(response.status_code, response.text))
                return False

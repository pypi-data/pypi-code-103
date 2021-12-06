# Copyright 2014 Google Inc. All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import datetime
import json
import logging
import multiprocessing
import pkgutil
import re
from functools import lru_cache

import packaging.utils
import requests

try:
    CPU_COUNT = max(2, multiprocessing.cpu_count())
except NotImplementedError:  # pragma: no cover
    CPU_COUNT = 2

PROJECT_NAME = re.compile(r"[\w.-]+")
PYPI_INDEX_URL = "https://pypi.org/pypi"


def just_name(supposed_name):
    """Strip off any versioning or restrictions metadata from a project name."""
    return PROJECT_NAME.match(supposed_name).group(0).lower()


def manual_overrides():
    """Read the overrides file.

    Read the overrides from cache, if available. Otherwise, an attempt is made
    to read the file as it currently stands on GitHub, and then only if that
    fails is the included file used. The result is cached for one day.
    """
    return _manual_overrides(datetime.date.today())


@lru_cache(maxsize=1)
def _manual_overrides(_cache_date=None):
    """Read the overrides file.

    An attempt is made to read the file as it currently stands on GitHub, and
    then only if that fails is the included file used.
    """
    log = logging.getLogger("ciu")
    request = requests.get("https://raw.githubusercontent.com/"
                           "matthewdeanmartin/caniuseonlywheels/"
                           "master/caniuseonlywheels/overrides.json")
    if request.status_code == 200:
        log.info("Overrides loaded from GitHub and cached")
        overrides = request.json()
    else:
        log.info("Overrides loaded from included package data and cached")
        raw_bytes = pkgutil.get_data(__name__, "overrides.json")
        overrides = json.loads(raw_bytes.decode("utf-8"))
    return frozenset(map(packaging.utils.canonicalize_name, overrides.keys()))


def supports_wheels(project_name, index_url=PYPI_INDEX_URL):
    """Check with PyPI if a project supports wheels."""
    log = logging.getLogger("ciu")
    log.info("Checking {} ...".format(project_name))
    url = "{}/{}/json".format(index_url, project_name)
    request = requests.get(url)
    if request.status_code >= 400:
        log = logging.getLogger("ciu")
        log.warning(
            "problem fetching {}, assuming ported ({})".format(
                project_name, request.status_code
            )
        )
        return True
    response = request.json()
    found1 = False

    # is there at least 1 wheel? Maybe support scenario
    # of checking if most recent has wheel, too.
    for version, release in response["releases"].items():
        for file_info in release:
            if file_info["filename"].endswith(".whl"):
                found1 = True
                break
        if found1:
            break

    return found1


if __name__ == "__main__":
    assert supports_wheels("jake")
    assert not supports_wheels("termcolor")

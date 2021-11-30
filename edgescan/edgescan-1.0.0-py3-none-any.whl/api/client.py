from typing import List, Iterator, Any, Optional, Dict, Iterable
from edgescan.api.authentication import DEFAULT_API_KEY
from edgescan.api.host import DEFAULT_HOST
from edgescan.constants import COLLECTION_TYPES
from edgescan.data.types.asset import Asset
from edgescan.data.types.host import Host
from edgescan.data.types.license import License
from edgescan.data.types.vulnerability import Vulnerability
from edgescan.http.session import DEFAULT_MAX_RETRIES_ON_CONNECTION_ERRORS, DEFAULT_MAX_RETRIES_ON_READ_ERRORS, \
    DEFAULT_MAX_RETRIES_ON_REDIRECT, DEFAULT_BACKOFF_FACTOR

import edgescan.data.parser as parser
import edgescan.http.session
import hodgepodge.pattern_matching
import hodgepodge.platforms
import hodgepodge.time
import urllib.parse
import datetime
import logging
import collections

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class EdgeScan:
    def __init__(
            self,
            host: str = DEFAULT_HOST,
            api_key: str = DEFAULT_API_KEY,
            max_retries_on_connection_errors: int = DEFAULT_MAX_RETRIES_ON_CONNECTION_ERRORS,
            max_retries_on_read_errors: int = DEFAULT_MAX_RETRIES_ON_READ_ERRORS,
            max_retries_on_redirects: int = DEFAULT_MAX_RETRIES_ON_REDIRECT,
            backoff_factor: float = DEFAULT_BACKOFF_FACTOR):

        self.host = host
        self.url = 'https://{}'.format(host)
        self.session = edgescan.http.session.get_session(
            api_key=api_key,
            max_retries_on_connection_errors=max_retries_on_connection_errors,
            max_retries_on_read_errors=max_retries_on_read_errors,
            max_retries_on_redirects=max_retries_on_redirects,
            backoff_factor=backoff_factor,
        )

    @property
    def hosts_url(self) -> str:
        return urllib.parse.urljoin(self.url, 'api/v1/hosts.json')

    @property
    def assets_url(self) -> str:
        return urllib.parse.urljoin(self.url, 'api/v1/assets.json')

    @property
    def vulnerabilities_url(self) -> str:
        return urllib.parse.urljoin(self.url, 'api/v1/vulnerabilities.json')

    def _iter_objects(self, url: str) -> Iterator[Any]:
        collection_type = _get_collection_type_from_url(url)

        response = self.session.get(url)
        response.raise_for_status()

        reply = response.json()
        for row in reply[collection_type]:
            row = parser.parse_object(row, collection_type=collection_type)
            if row:
                yield row

    def _count_objects(self, url: str) -> int:
        response = self.session.get(url)
        response.raise_for_status()

        reply = response.json()
        return reply['total']

    def get_asset(self, asset_id: int) -> Optional[Asset]:
        return next(self.iter_assets(ids=[asset_id]), None)

    def get_assets(
            self,
            ids: Optional[Iterable[int]] = None,
            names: Optional[Iterable[str]] = None,
            tags: Optional[Iterable[str]] = None,
            host_ids: Optional[Iterable[int]] = None,
            hostnames: Optional[Iterable[str]] = None,
            ip_addresses: Optional[Iterable[str]] = None,
            os_types: Optional[Iterable[str]] = None,
            os_versions: Optional[Iterable[str]] = None,
            alive: Optional[bool] = None,
            vulnerability_ids: Optional[Iterable[int]] = None,
            vulnerability_names: Optional[Iterable[str]] = None,
            cve_ids: Optional[Iterable[str]] = None,
            min_asset_create_time: Optional[datetime.datetime] = None,
            max_asset_create_time: Optional[datetime.datetime] = None,
            min_asset_update_time: Optional[datetime.datetime] = None,
            max_asset_update_time: Optional[datetime.datetime] = None,
            min_next_assessment_time: Optional[datetime.datetime] = None,
            max_next_assessment_time: Optional[datetime.datetime] = None,
            min_last_assessment_time: Optional[datetime.datetime] = None,
            max_last_assessment_time: Optional[datetime.datetime] = None,
            min_last_host_scan_time: Optional[datetime.datetime] = None,
            max_last_host_scan_time: Optional[datetime.datetime] = None,
            min_host_last_seen_time: Optional[datetime.datetime] = None,
            max_host_last_seen_time: Optional[datetime.datetime] = None,
            min_vulnerability_create_time: Optional[datetime.datetime] = None,
            max_vulnerability_create_time: Optional[datetime.datetime] = None,
            min_vulnerability_update_time: Optional[datetime.datetime] = None,
            max_vulnerability_update_time: Optional[datetime.datetime] = None,
            min_vulnerability_open_time: Optional[datetime.datetime] = None,
            max_vulnerability_open_time: Optional[datetime.datetime] = None,
            min_vulnerability_close_time: Optional[datetime.datetime] = None,
            max_vulnerability_close_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> List[Asset]:

        return list(self.iter_assets(
            ids=ids,
            names=names,
            tags=tags,
            host_ids=host_ids,
            hostnames=hostnames,
            ip_addresses=ip_addresses,
            os_types=os_types,
            os_versions=os_versions,
            alive=alive,
            vulnerability_ids=vulnerability_ids,
            vulnerability_names=vulnerability_names,
            cve_ids=cve_ids,
            min_asset_create_time=min_asset_create_time,
            max_asset_create_time=max_asset_create_time,
            min_asset_update_time=min_asset_update_time,
            max_asset_update_time=max_asset_update_time,
            min_next_assessment_time=min_next_assessment_time,
            max_next_assessment_time=max_next_assessment_time,
            min_last_assessment_time=min_last_assessment_time,
            max_last_assessment_time=max_last_assessment_time,
            min_last_host_scan_time=min_last_host_scan_time,
            max_last_host_scan_time=max_last_host_scan_time,
            min_host_last_seen_time=min_host_last_seen_time,
            max_host_last_seen_time=max_host_last_seen_time,
            min_vulnerability_create_time=min_vulnerability_create_time,
            max_vulnerability_create_time=max_vulnerability_create_time,
            min_vulnerability_update_time=min_vulnerability_update_time,
            max_vulnerability_update_time=max_vulnerability_update_time,
            min_vulnerability_open_time=min_vulnerability_open_time,
            max_vulnerability_open_time=max_vulnerability_open_time,
            min_vulnerability_close_time=min_vulnerability_close_time,
            max_vulnerability_close_time=max_vulnerability_close_time,
            limit=limit,
        ))

    def iter_assets(
            self,
            ids: Optional[Iterable[int]] = None,
            names: Optional[Iterable[str]] = None,
            tags: Optional[Iterable[str]] = None,
            host_ids: Optional[Iterable[int]] = None,
            hostnames: Optional[Iterable[str]] = None,
            ip_addresses: Optional[Iterable[str]] = None,
            os_types: Optional[Iterable[str]] = None,
            os_versions: Optional[Iterable[str]] = None,
            alive: Optional[bool] = None,
            vulnerability_ids: Optional[Iterable[int]] = None,
            vulnerability_names: Optional[Iterable[str]] = None,
            cve_ids: Optional[Iterable[str]] = None,
            min_asset_create_time: Optional[datetime.datetime] = None,
            max_asset_create_time: Optional[datetime.datetime] = None,
            min_asset_update_time: Optional[datetime.datetime] = None,
            max_asset_update_time: Optional[datetime.datetime] = None,
            min_next_assessment_time: Optional[datetime.datetime] = None,
            max_next_assessment_time: Optional[datetime.datetime] = None,
            min_last_assessment_time: Optional[datetime.datetime] = None,
            max_last_assessment_time: Optional[datetime.datetime] = None,
            min_last_host_scan_time: Optional[datetime.datetime] = None,
            max_last_host_scan_time: Optional[datetime.datetime] = None,
            min_host_last_seen_time: Optional[datetime.datetime] = None,
            max_host_last_seen_time: Optional[datetime.datetime] = None,
            min_vulnerability_create_time: Optional[datetime.datetime] = None,
            max_vulnerability_create_time: Optional[datetime.datetime] = None,
            min_vulnerability_update_time: Optional[datetime.datetime] = None,
            max_vulnerability_update_time: Optional[datetime.datetime] = None,
            min_vulnerability_open_time: Optional[datetime.datetime] = None,
            max_vulnerability_open_time: Optional[datetime.datetime] = None,
            min_vulnerability_close_time: Optional[datetime.datetime] = None,
            max_vulnerability_close_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> Iterator[Asset]:

        #: If looking up assets based on related hosts.
        if host_ids or (min_host_last_seen_time is not None) or (max_host_last_seen_time is not None):
            hosts = self.iter_hosts(
                ids=host_ids,
                hostnames=hostnames,
                ip_addresses=ip_addresses,
                os_types=os_types,
                os_versions=os_versions,
                alive=alive,
                asset_ids=ids,
                asset_tags=tags,
                min_host_last_seen_time=min_host_last_seen_time,
                max_host_last_seen_time=max_host_last_seen_time,
            )
            ids = list({host.asset_id for host in hosts})

        #: If looking up assets based on related vulnerabilities.
        if vulnerability_ids or vulnerability_names or \
                (min_vulnerability_create_time is not None) or \
                (max_vulnerability_create_time is not None) or \
                (min_vulnerability_update_time is not None) or \
                (max_vulnerability_update_time is not None) or \
                (min_vulnerability_open_time is not None) or \
                (max_vulnerability_open_time is not None) or \
                (min_vulnerability_close_time is not None) or \
                (max_vulnerability_close_time is not None):

            vulnerabilities = self.iter_vulnerabilities(
                ids=vulnerability_ids,
                names=vulnerability_names,
                cve_ids=cve_ids,
                asset_ids=ids,
                min_vulnerability_create_time=min_vulnerability_create_time,
                max_vulnerability_create_time=max_vulnerability_create_time,
                min_vulnerability_update_time=min_vulnerability_update_time,
                max_vulnerability_update_time=max_vulnerability_update_time,
                min_vulnerability_open_time=min_vulnerability_open_time,
                max_vulnerability_open_time=max_vulnerability_open_time,
                min_vulnerability_close_time=min_vulnerability_close_time,
                max_vulnerability_close_time=max_vulnerability_close_time,
            )
            ids = list({vulnerability.asset_id for vulnerability in vulnerabilities})

        #: Lookup assets.
        i = 0
        for asset in self._iter_objects(url=self.assets_url):
            if not asset.matches(
                ids=ids,
                names=names,
                tags=tags,
                min_create_time=min_asset_create_time,
                max_create_time=max_asset_create_time,
                min_update_time=min_asset_update_time,
                max_update_time=max_asset_update_time,
                min_next_assessment_time=min_next_assessment_time,
                max_next_assessment_time=max_next_assessment_time,
                min_last_assessment_time=min_last_assessment_time,
                max_last_assessment_time=max_last_assessment_time,
                min_last_host_scan_time=min_last_host_scan_time,
                max_last_host_scan_time=max_last_host_scan_time,
            ):
                continue

            yield asset

            if limit:
                i += 1
                if i >= limit:
                    return

    def count_assets(
            self,
            ids: Optional[Iterable[int]] = None,
            names: Optional[Iterable[str]] = None,
            tags: Optional[Iterable[str]] = None,
            host_ids: Optional[Iterable[int]] = None,
            hostnames: Optional[Iterable[str]] = None,
            ip_addresses: Optional[Iterable[str]] = None,
            os_types: Optional[Iterable[str]] = None,
            os_versions: Optional[Iterable[str]] = None,
            alive: Optional[bool] = None,
            vulnerability_ids: Optional[Iterable[int]] = None,
            vulnerability_names: Optional[Iterable[str]] = None,
            cve_ids: Optional[Iterable[str]] = None,
            min_asset_create_time: Optional[datetime.datetime] = None,
            max_asset_create_time: Optional[datetime.datetime] = None,
            min_asset_update_time: Optional[datetime.datetime] = None,
            max_asset_update_time: Optional[datetime.datetime] = None,
            min_next_assessment_time: Optional[datetime.datetime] = None,
            max_next_assessment_time: Optional[datetime.datetime] = None,
            min_last_assessment_time: Optional[datetime.datetime] = None,
            max_last_assessment_time: Optional[datetime.datetime] = None,
            min_last_host_scan_time: Optional[datetime.datetime] = None,
            max_last_host_scan_time: Optional[datetime.datetime] = None,
            min_host_last_seen_time: Optional[datetime.datetime] = None,
            max_host_last_seen_time: Optional[datetime.datetime] = None,
            min_vulnerability_create_time: Optional[datetime.datetime] = None,
            max_vulnerability_create_time: Optional[datetime.datetime] = None,
            min_vulnerability_update_time: Optional[datetime.datetime] = None,
            max_vulnerability_update_time: Optional[datetime.datetime] = None,
            min_vulnerability_open_time: Optional[datetime.datetime] = None,
            max_vulnerability_open_time: Optional[datetime.datetime] = None,
            min_vulnerability_close_time: Optional[datetime.datetime] = None,
            max_vulnerability_close_time: Optional[datetime.datetime] = None) -> int:

        assets = self.iter_assets(
            ids=ids,
            names=names,
            tags=tags,
            host_ids=host_ids,
            hostnames=hostnames,
            ip_addresses=ip_addresses,
            os_types=os_types,
            os_versions=os_versions,
            alive=alive,
            vulnerability_ids=vulnerability_ids,
            vulnerability_names=vulnerability_names,
            cve_ids=cve_ids,
            min_asset_create_time=min_asset_create_time,
            max_asset_create_time=max_asset_create_time,
            min_asset_update_time=min_asset_update_time,
            max_asset_update_time=max_asset_update_time,
            min_next_assessment_time=min_next_assessment_time,
            max_next_assessment_time=max_next_assessment_time,
            min_last_assessment_time=min_last_assessment_time,
            max_last_assessment_time=max_last_assessment_time,
            min_last_host_scan_time=min_last_host_scan_time,
            max_last_host_scan_time=max_last_host_scan_time,
            min_host_last_seen_time=min_host_last_seen_time,
            max_host_last_seen_time=max_host_last_seen_time,
            min_vulnerability_create_time=min_vulnerability_create_time,
            max_vulnerability_create_time=max_vulnerability_create_time,
            min_vulnerability_update_time=min_vulnerability_update_time,
            max_vulnerability_update_time=max_vulnerability_update_time,
            min_vulnerability_open_time=min_vulnerability_open_time,
            max_vulnerability_open_time=max_vulnerability_open_time,
            min_vulnerability_close_time=min_vulnerability_close_time,
            max_vulnerability_close_time=max_vulnerability_close_time,
        )
        return sum(1 for _ in assets)

    def get_host(self, host_id: int) -> Optional[Host]:
        return next(self.iter_hosts(ids=[host_id]), None)

    def get_hosts(
            self,
            ids: Optional[Iterable[int]] = None,
            hostnames: Optional[Iterable[str]] = None,
            ip_addresses: Optional[Iterable[str]] = None,
            os_types: Optional[Iterable[str]] = None,
            os_versions: Optional[Iterable[str]] = None,
            alive: Optional[bool] = None,
            asset_ids: Optional[Iterable[int]] = None,
            asset_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            vulnerability_ids: Optional[Iterable[int]] = None,
            vulnerability_names: Optional[Iterable[str]] = None,
            cve_ids: Optional[Iterable[str]] = None,
            min_asset_create_time: Optional[datetime.datetime] = None,
            max_asset_create_time: Optional[datetime.datetime] = None,
            min_asset_update_time: Optional[datetime.datetime] = None,
            max_asset_update_time: Optional[datetime.datetime] = None,
            min_next_assessment_time: Optional[datetime.datetime] = None,
            max_next_assessment_time: Optional[datetime.datetime] = None,
            min_last_assessment_time: Optional[datetime.datetime] = None,
            max_last_assessment_time: Optional[datetime.datetime] = None,
            min_last_host_scan_time: Optional[datetime.datetime] = None,
            max_last_host_scan_time: Optional[datetime.datetime] = None,
            min_host_last_seen_time: Optional[datetime.datetime] = None,
            max_host_last_seen_time: Optional[datetime.datetime] = None,
            min_vulnerability_create_time: Optional[datetime.datetime] = None,
            max_vulnerability_create_time: Optional[datetime.datetime] = None,
            min_vulnerability_update_time: Optional[datetime.datetime] = None,
            max_vulnerability_update_time: Optional[datetime.datetime] = None,
            min_vulnerability_open_time: Optional[datetime.datetime] = None,
            max_vulnerability_open_time: Optional[datetime.datetime] = None,
            min_vulnerability_close_time: Optional[datetime.datetime] = None,
            max_vulnerability_close_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> List[Host]:

        return list(self.iter_hosts(
            ids=ids,
            hostnames=hostnames,
            ip_addresses=ip_addresses,
            os_types=os_types,
            os_versions=os_versions,
            alive=alive,
            asset_ids=asset_ids,
            asset_names=asset_names,
            asset_tags=asset_tags,
            vulnerability_ids=vulnerability_ids,
            vulnerability_names=vulnerability_names,
            cve_ids=cve_ids,
            min_asset_create_time=min_asset_create_time,
            max_asset_create_time=max_asset_create_time,
            min_asset_update_time=min_asset_update_time,
            max_asset_update_time=max_asset_update_time,
            min_next_assessment_time=min_next_assessment_time,
            max_next_assessment_time=max_next_assessment_time,
            min_last_assessment_time=min_last_assessment_time,
            max_last_assessment_time=max_last_assessment_time,
            min_last_host_scan_time=min_last_host_scan_time,
            max_last_host_scan_time=max_last_host_scan_time,
            min_host_last_seen_time=min_host_last_seen_time,
            max_host_last_seen_time=max_host_last_seen_time,
            min_vulnerability_create_time=min_vulnerability_create_time,
            max_vulnerability_create_time=max_vulnerability_create_time,
            min_vulnerability_update_time=min_vulnerability_update_time,
            max_vulnerability_update_time=max_vulnerability_update_time,
            min_vulnerability_open_time=min_vulnerability_open_time,
            max_vulnerability_open_time=max_vulnerability_open_time,
            min_vulnerability_close_time=min_vulnerability_close_time,
            max_vulnerability_close_time=max_vulnerability_close_time,
            limit=limit,
        ))

    def iter_hosts(
            self,
            ids: Optional[Iterable[int]] = None,
            hostnames: Optional[Iterable[str]] = None,
            ip_addresses: Optional[Iterable[str]] = None,
            os_types: Optional[Iterable[str]] = None,
            os_versions: Optional[Iterable[str]] = None,
            alive: Optional[bool] = None,
            asset_ids: Optional[Iterable[int]] = None,
            asset_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            vulnerability_ids: Optional[Iterable[int]] = None,
            vulnerability_names: Optional[Iterable[str]] = None,
            cve_ids: Optional[Iterable[str]] = None,
            min_asset_create_time: Optional[datetime.datetime] = None,
            max_asset_create_time: Optional[datetime.datetime] = None,
            min_asset_update_time: Optional[datetime.datetime] = None,
            max_asset_update_time: Optional[datetime.datetime] = None,
            min_next_assessment_time: Optional[datetime.datetime] = None,
            max_next_assessment_time: Optional[datetime.datetime] = None,
            min_last_assessment_time: Optional[datetime.datetime] = None,
            max_last_assessment_time: Optional[datetime.datetime] = None,
            min_last_host_scan_time: Optional[datetime.datetime] = None,
            max_last_host_scan_time: Optional[datetime.datetime] = None,
            min_host_last_seen_time: Optional[datetime.datetime] = None,
            max_host_last_seen_time: Optional[datetime.datetime] = None,
            min_vulnerability_create_time: Optional[datetime.datetime] = None,
            max_vulnerability_create_time: Optional[datetime.datetime] = None,
            min_vulnerability_update_time: Optional[datetime.datetime] = None,
            max_vulnerability_update_time: Optional[datetime.datetime] = None,
            min_vulnerability_open_time: Optional[datetime.datetime] = None,
            max_vulnerability_open_time: Optional[datetime.datetime] = None,
            min_vulnerability_close_time: Optional[datetime.datetime] = None,
            max_vulnerability_close_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> Iterator[Host]:

        #: If filtering hosts based on related assets.
        if asset_tags:
            assets = self.iter_assets(
                ids=asset_ids,
                names=asset_names,
                tags=asset_tags,
                min_asset_create_time=min_asset_create_time,
                max_asset_create_time=max_asset_create_time,
                min_asset_update_time=min_asset_update_time,
                max_asset_update_time=max_asset_update_time,
                min_next_assessment_time=min_next_assessment_time,
                max_next_assessment_time=max_next_assessment_time,
                min_last_assessment_time=min_last_assessment_time,
                max_last_assessment_time=max_last_assessment_time,
                min_last_host_scan_time=min_last_host_scan_time,
                max_last_host_scan_time=max_last_host_scan_time,
            )
            asset_ids = list({asset.id for asset in assets})

        #: If filtering hosts based on related vulnerabilities.
        if vulnerability_ids or vulnerability_names or cve_ids:
            vulnerabilities = self.iter_vulnerabilities(
                ids=vulnerability_ids,
                names=vulnerability_names,
                cve_ids=cve_ids,
                min_vulnerability_create_time=min_vulnerability_create_time,
                max_vulnerability_create_time=max_vulnerability_create_time,
                min_vulnerability_update_time=min_vulnerability_update_time,
                max_vulnerability_update_time=max_vulnerability_update_time,
                min_vulnerability_open_time=min_vulnerability_open_time,
                max_vulnerability_open_time=max_vulnerability_open_time,
                min_vulnerability_close_time=min_vulnerability_close_time,
                max_vulnerability_close_time=max_vulnerability_close_time,
            )
            asset_ids = list({v.asset_id for v in vulnerabilities})

        #: The location of a host may be specified by IP address or hostname.
        ip_addresses = set(ip_addresses) if ip_addresses else set()
        hostnames = set(hostnames) if hostnames else set()
        locations = ip_addresses | hostnames

        i = 0
        for host in self._iter_objects(url=self.hosts_url):
            if not host.matches(
                ids=ids,
                asset_ids=asset_ids,
                locations=locations,
                os_types=os_types,
                os_versions=os_versions,
                alive=alive,
                min_last_seen_time=min_host_last_seen_time,
                max_last_seen_time=max_host_last_seen_time,
            ):
                continue

            yield host

            if limit:
                i += 1
                if i >= limit:
                    return

    def count_hosts(
            self,
            ids: Optional[Iterable[int]] = None,
            hostnames: Optional[Iterable[str]] = None,
            ip_addresses: Optional[Iterable[str]] = None,
            os_types: Optional[Iterable[str]] = None,
            os_versions: Optional[Iterable[str]] = None,
            alive: Optional[bool] = None,
            asset_ids: Optional[Iterable[int]] = None,
            asset_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            vulnerability_ids: Optional[Iterable[int]] = None,
            vulnerability_names: Optional[Iterable[str]] = None,
            cve_ids: Optional[Iterable[str]] = None,
            min_asset_create_time: Optional[datetime.datetime] = None,
            max_asset_create_time: Optional[datetime.datetime] = None,
            min_asset_update_time: Optional[datetime.datetime] = None,
            max_asset_update_time: Optional[datetime.datetime] = None,
            min_next_assessment_time: Optional[datetime.datetime] = None,
            max_next_assessment_time: Optional[datetime.datetime] = None,
            min_last_assessment_time: Optional[datetime.datetime] = None,
            max_last_assessment_time: Optional[datetime.datetime] = None,
            min_last_host_scan_time: Optional[datetime.datetime] = None,
            max_last_host_scan_time: Optional[datetime.datetime] = None,
            min_host_last_seen_time: Optional[datetime.datetime] = None,
            max_host_last_seen_time: Optional[datetime.datetime] = None,
            min_vulnerability_create_time: Optional[datetime.datetime] = None,
            max_vulnerability_create_time: Optional[datetime.datetime] = None,
            min_vulnerability_update_time: Optional[datetime.datetime] = None,
            max_vulnerability_update_time: Optional[datetime.datetime] = None,
            min_vulnerability_open_time: Optional[datetime.datetime] = None,
            max_vulnerability_open_time: Optional[datetime.datetime] = None,
            min_vulnerability_close_time: Optional[datetime.datetime] = None,
            max_vulnerability_close_time: Optional[datetime.datetime] = None) -> int:

        hosts = self.iter_hosts(
            ids=ids,
            hostnames=hostnames,
            ip_addresses=ip_addresses,
            os_types=os_types,
            os_versions=os_versions,
            alive=alive,
            asset_ids=asset_ids,
            asset_names=asset_names,
            asset_tags=asset_tags,
            vulnerability_ids=vulnerability_ids,
            vulnerability_names=vulnerability_names,
            cve_ids=cve_ids,
            min_asset_create_time=min_asset_create_time,
            max_asset_create_time=max_asset_create_time,
            min_asset_update_time=min_asset_update_time,
            max_asset_update_time=max_asset_update_time,
            min_next_assessment_time=min_next_assessment_time,
            max_next_assessment_time=max_next_assessment_time,
            min_last_assessment_time=min_last_assessment_time,
            max_last_assessment_time=max_last_assessment_time,
            min_last_host_scan_time=min_last_host_scan_time,
            max_last_host_scan_time=max_last_host_scan_time,
            min_host_last_seen_time=min_host_last_seen_time,
            max_host_last_seen_time=max_host_last_seen_time,
            min_vulnerability_create_time=min_vulnerability_create_time,
            max_vulnerability_create_time=max_vulnerability_create_time,
            min_vulnerability_update_time=min_vulnerability_update_time,
            max_vulnerability_update_time=max_vulnerability_update_time,
            min_vulnerability_open_time=min_vulnerability_open_time,
            max_vulnerability_open_time=max_vulnerability_open_time,
            min_vulnerability_close_time=min_vulnerability_close_time,
            max_vulnerability_close_time=max_vulnerability_close_time,
        )
        return sum(1 for _ in hosts)

    def get_vulnerability(self, vulnerability_id: int) -> Optional[Vulnerability]:
        return next(self.iter_vulnerabilities(ids=[vulnerability_id]), None)

    def get_vulnerabilities(
            self,
            ids: Optional[Iterable[int]] = None,
            names: Optional[Iterable[str]] = None,
            cve_ids: Optional[Iterable[str]] = None,
            locations: Optional[Iterable[str]] = None,
            affects_pci_compliance: Optional[bool] = None,
            include_application_layer_vulnerabilities: Optional[bool] = True,
            include_network_layer_vulnerabilities: Optional[bool] = True,
            asset_ids: Optional[Iterable[int]] = None,
            asset_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            host_ids: Optional[Iterable[int]] = None,
            hostnames: Optional[Iterable[str]] = None,
            ip_addresses: Optional[Iterable[str]] = None,
            os_types: Optional[Iterable[str]] = None,
            os_versions: Optional[Iterable[str]] = None,
            alive: Optional[bool] = None,
            min_asset_create_time: Optional[datetime.datetime] = None,
            max_asset_create_time: Optional[datetime.datetime] = None,
            min_asset_update_time: Optional[datetime.datetime] = None,
            max_asset_update_time: Optional[datetime.datetime] = None,
            min_next_assessment_time: Optional[datetime.datetime] = None,
            max_next_assessment_time: Optional[datetime.datetime] = None,
            min_last_assessment_time: Optional[datetime.datetime] = None,
            max_last_assessment_time: Optional[datetime.datetime] = None,
            min_last_host_scan_time: Optional[datetime.datetime] = None,
            max_last_host_scan_time: Optional[datetime.datetime] = None,
            min_host_last_seen_time: Optional[datetime.datetime] = None,
            max_host_last_seen_time: Optional[datetime.datetime] = None,
            min_vulnerability_create_time: Optional[datetime.datetime] = None,
            max_vulnerability_create_time: Optional[datetime.datetime] = None,
            min_vulnerability_update_time: Optional[datetime.datetime] = None,
            max_vulnerability_update_time: Optional[datetime.datetime] = None,
            min_vulnerability_open_time: Optional[datetime.datetime] = None,
            max_vulnerability_open_time: Optional[datetime.datetime] = None,
            min_vulnerability_close_time: Optional[datetime.datetime] = None,
            max_vulnerability_close_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> List[Vulnerability]:

        return list(self.iter_vulnerabilities(
            ids=ids,
            names=names,
            cve_ids=cve_ids,
            locations=locations,
            affects_pci_compliance=affects_pci_compliance,
            include_application_layer_vulnerabilities=include_application_layer_vulnerabilities,
            include_network_layer_vulnerabilities=include_network_layer_vulnerabilities,
            asset_ids=asset_ids,
            asset_names=asset_names,
            asset_tags=asset_tags,
            host_ids=host_ids,
            hostnames=hostnames,
            ip_addresses=ip_addresses,
            os_types=os_types,
            os_versions=os_versions,
            alive=alive,
            min_asset_create_time=min_asset_create_time,
            max_asset_create_time=max_asset_create_time,
            min_asset_update_time=min_asset_update_time,
            max_asset_update_time=max_asset_update_time,
            min_next_assessment_time=min_next_assessment_time,
            max_next_assessment_time=max_next_assessment_time,
            min_last_assessment_time=min_last_assessment_time,
            max_last_assessment_time=max_last_assessment_time,
            min_last_host_scan_time=min_last_host_scan_time,
            max_last_host_scan_time=max_last_host_scan_time,
            min_host_last_seen_time=min_host_last_seen_time,
            max_host_last_seen_time=max_host_last_seen_time,
            min_vulnerability_create_time=min_vulnerability_create_time,
            max_vulnerability_create_time=max_vulnerability_create_time,
            min_vulnerability_update_time=min_vulnerability_update_time,
            max_vulnerability_update_time=max_vulnerability_update_time,
            min_vulnerability_open_time=min_vulnerability_open_time,
            max_vulnerability_open_time=max_vulnerability_open_time,
            min_vulnerability_close_time=min_vulnerability_close_time,
            max_vulnerability_close_time=max_vulnerability_close_time,
            limit=limit,
        ))

    def iter_vulnerabilities(
            self,
            ids: Optional[Iterable[int]] = None,
            names: Optional[Iterable[str]] = None,
            cve_ids: Optional[Iterable[str]] = None,
            locations: Optional[Iterable[str]] = None,
            affects_pci_compliance: Optional[bool] = None,
            include_application_layer_vulnerabilities: Optional[bool] = True,
            include_network_layer_vulnerabilities: Optional[bool] = True,
            asset_ids: Optional[Iterable[int]] = None,
            asset_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            host_ids: Optional[Iterable[int]] = None,
            hostnames: Optional[Iterable[str]] = None,
            ip_addresses: Optional[Iterable[str]] = None,
            os_types: Optional[Iterable[str]] = None,
            os_versions: Optional[Iterable[str]] = None,
            alive: Optional[bool] = None,
            min_asset_create_time: Optional[datetime.datetime] = None,
            max_asset_create_time: Optional[datetime.datetime] = None,
            min_asset_update_time: Optional[datetime.datetime] = None,
            max_asset_update_time: Optional[datetime.datetime] = None,
            min_next_assessment_time: Optional[datetime.datetime] = None,
            max_next_assessment_time: Optional[datetime.datetime] = None,
            min_last_assessment_time: Optional[datetime.datetime] = None,
            max_last_assessment_time: Optional[datetime.datetime] = None,
            min_last_host_scan_time: Optional[datetime.datetime] = None,
            max_last_host_scan_time: Optional[datetime.datetime] = None,
            min_host_last_seen_time: Optional[datetime.datetime] = None,
            max_host_last_seen_time: Optional[datetime.datetime] = None,
            min_vulnerability_create_time: Optional[datetime.datetime] = None,
            max_vulnerability_create_time: Optional[datetime.datetime] = None,
            min_vulnerability_update_time: Optional[datetime.datetime] = None,
            max_vulnerability_update_time: Optional[datetime.datetime] = None,
            min_vulnerability_open_time: Optional[datetime.datetime] = None,
            max_vulnerability_open_time: Optional[datetime.datetime] = None,
            min_vulnerability_close_time: Optional[datetime.datetime] = None,
            max_vulnerability_close_time: Optional[datetime.datetime] = None,
            limit: Optional[int] = None) -> Iterator[Vulnerability]:

        #: If filtering vulnerabilities based on related assets.
        if asset_ids or asset_tags or host_ids:
            assets = self.iter_assets(
                ids=asset_ids,
                names=asset_names,
                tags=asset_tags,
                host_ids=host_ids,
                hostnames=hostnames,
                ip_addresses=ip_addresses,
                os_types=os_types,
                os_versions=os_versions,
                alive=alive,
                min_host_last_seen_time=min_host_last_seen_time,
                max_host_last_seen_time=max_host_last_seen_time,
                min_asset_create_time=min_asset_create_time,
                max_asset_create_time=max_asset_create_time,
                min_asset_update_time=min_asset_update_time,
                max_asset_update_time=max_asset_update_time,
                min_next_assessment_time=min_next_assessment_time,
                max_next_assessment_time=max_next_assessment_time,
                min_last_assessment_time=min_last_assessment_time,
                max_last_assessment_time=max_last_assessment_time,
                min_last_host_scan_time=min_last_host_scan_time,
                max_last_host_scan_time=max_last_host_scan_time,
            )
            asset_ids = list({asset.id for asset in assets})

        i = 0
        for vulnerability in self._iter_objects(url=self.vulnerabilities_url):
            if not vulnerability.matches(
                ids=ids,
                names=names,
                cve_ids=cve_ids,
                asset_ids=asset_ids,
                locations=locations,
                affects_pci_compliance=affects_pci_compliance,
                include_application_layer_vulnerabilities=include_application_layer_vulnerabilities,
                include_network_layer_vulnerabilities=include_network_layer_vulnerabilities,
                min_create_time=min_vulnerability_create_time,
                max_create_time=max_vulnerability_create_time,
                min_update_time=min_vulnerability_update_time,
                max_update_time=max_vulnerability_update_time,
                min_open_time=min_vulnerability_open_time,
                max_open_time=max_vulnerability_open_time,
                min_close_time=min_vulnerability_close_time,
                max_close_time=max_vulnerability_close_time,
            ):
                continue

            yield vulnerability

            if limit:
                i += 1
                if i >= limit:
                    return

    def count_vulnerabilities(
            self,
            ids: Optional[Iterable[int]] = None,
            names: Optional[Iterable[str]] = None,
            cve_ids: Optional[Iterable[str]] = None,
            locations: Optional[Iterable[str]] = None,
            affects_pci_compliance: Optional[bool] = None,
            include_application_layer_vulnerabilities: Optional[bool] = True,
            include_network_layer_vulnerabilities: Optional[bool] = True,
            asset_ids: Optional[Iterable[int]] = None,
            asset_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            host_ids: Optional[Iterable[int]] = None,
            hostnames: Optional[Iterable[str]] = None,
            ip_addresses: Optional[Iterable[str]] = None,
            os_types: Optional[Iterable[str]] = None,
            os_versions: Optional[Iterable[str]] = None,
            alive: Optional[bool] = None,
            min_asset_create_time: Optional[datetime.datetime] = None,
            max_asset_create_time: Optional[datetime.datetime] = None,
            min_asset_update_time: Optional[datetime.datetime] = None,
            max_asset_update_time: Optional[datetime.datetime] = None,
            min_next_assessment_time: Optional[datetime.datetime] = None,
            max_next_assessment_time: Optional[datetime.datetime] = None,
            min_last_assessment_time: Optional[datetime.datetime] = None,
            max_last_assessment_time: Optional[datetime.datetime] = None,
            min_last_host_scan_time: Optional[datetime.datetime] = None,
            max_last_host_scan_time: Optional[datetime.datetime] = None,
            min_host_last_seen_time: Optional[datetime.datetime] = None,
            max_host_last_seen_time: Optional[datetime.datetime] = None,
            min_vulnerability_create_time: Optional[datetime.datetime] = None,
            max_vulnerability_create_time: Optional[datetime.datetime] = None,
            min_vulnerability_update_time: Optional[datetime.datetime] = None,
            max_vulnerability_update_time: Optional[datetime.datetime] = None,
            min_vulnerability_open_time: Optional[datetime.datetime] = None,
            max_vulnerability_open_time: Optional[datetime.datetime] = None,
            min_vulnerability_close_time: Optional[datetime.datetime] = None,
            max_vulnerability_close_time: Optional[datetime.datetime] = None) -> int:

        vulnerabilities = self.iter_vulnerabilities(
            ids=ids,
            names=names,
            cve_ids=cve_ids,
            locations=locations,
            affects_pci_compliance=affects_pci_compliance,
            include_application_layer_vulnerabilities=include_application_layer_vulnerabilities,
            include_network_layer_vulnerabilities=include_network_layer_vulnerabilities,
            asset_ids=asset_ids,
            asset_names=asset_names,
            asset_tags=asset_tags,
            host_ids=host_ids,
            hostnames=hostnames,
            ip_addresses=ip_addresses,
            os_types=os_types,
            os_versions=os_versions,
            alive=alive,
            min_asset_create_time=min_asset_create_time,
            max_asset_create_time=max_asset_create_time,
            min_asset_update_time=min_asset_update_time,
            max_asset_update_time=max_asset_update_time,
            min_next_assessment_time=min_next_assessment_time,
            max_next_assessment_time=max_next_assessment_time,
            min_last_assessment_time=min_last_assessment_time,
            max_last_assessment_time=max_last_assessment_time,
            min_last_host_scan_time=min_last_host_scan_time,
            max_last_host_scan_time=max_last_host_scan_time,
            min_host_last_seen_time=min_host_last_seen_time,
            max_host_last_seen_time=max_host_last_seen_time,
            min_vulnerability_create_time=min_vulnerability_create_time,
            max_vulnerability_create_time=max_vulnerability_create_time,
            min_vulnerability_update_time=min_vulnerability_update_time,
            max_vulnerability_update_time=max_vulnerability_update_time,
            min_vulnerability_open_time=min_vulnerability_open_time,
            max_vulnerability_open_time=max_vulnerability_open_time,
            min_vulnerability_close_time=min_vulnerability_close_time,
            max_vulnerability_close_time=max_vulnerability_close_time,
        )
        return sum(1 for _ in vulnerabilities)

    def get_license(self, license_id: int) -> Optional[License]:
        return next(self.iter_licenses(ids=[license_id]), None)

    def get_licenses(
            self,
            ids: Optional[Iterable[int]] = None,
            names: Optional[Iterable[str]] = None,
            expired: Optional[bool] = None,
            limit: Optional[int] = None) -> List[License]:

        return list(self.iter_licenses(
            ids=ids,
            names=names,
            expired=expired,
            limit=limit,
        ))

    def iter_licenses(
            self,
            ids: Optional[Iterable[int]] = None,
            names: Optional[Iterable[str]] = None,
            expired: Optional[bool] = None,
            limit: Optional[int] = None) -> Iterator[License]:

        i = 0
        for row in self._iter_licenses():
            if ids and row.id not in ids:
                continue

            if names and not hodgepodge.pattern_matching.str_matches_glob(row.name, names):
                continue

            if expired is not None and row.expired != expired:
                continue

            yield row

            if limit:
                i += 1
                if i >= limit:
                    return

    def _iter_licenses(self) -> Iterator[License]:
        seen = set()
        for asset in self.iter_assets():
            active_license = asset.active_license
            if active_license.id not in seen:
                seen.add(active_license.id)
                yield active_license

    def count_licenses(
            self,
            ids: Optional[Iterable[int]] = None,
            names: Optional[Iterable[str]] = None,
            expired: Optional[bool] = None) -> int:

        licenses = self.iter_licenses(
            ids=ids,
            names=names,
            expired=expired,
        )
        return sum(1 for _ in licenses)

    def get_map_of_asset_to_hosts(
            self,
            asset_ids: Optional[Iterable[int]] = None,
            asset_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            host_ids: Optional[Iterable[int]] = None,
            hostnames: Optional[Iterable[str]] = None,
            ip_addresses: Optional[Iterable[str]] = None,
            os_types: Optional[Iterable[str]] = None,
            os_versions: Optional[Iterable[str]] = None,
            alive: Optional[bool] = None,
            vulnerability_ids: Optional[Iterable[int]] = None,
            vulnerability_names: Optional[Iterable[str]] = None,
            cve_ids: Optional[Iterable[str]] = None,
            min_asset_create_time: Optional[datetime.datetime] = None,
            max_asset_create_time: Optional[datetime.datetime] = None,
            min_asset_update_time: Optional[datetime.datetime] = None,
            max_asset_update_time: Optional[datetime.datetime] = None,
            min_next_assessment_time: Optional[datetime.datetime] = None,
            max_next_assessment_time: Optional[datetime.datetime] = None,
            min_last_assessment_time: Optional[datetime.datetime] = None,
            max_last_assessment_time: Optional[datetime.datetime] = None,
            min_last_host_scan_time: Optional[datetime.datetime] = None,
            max_last_host_scan_time: Optional[datetime.datetime] = None,
            min_host_last_seen_time: Optional[datetime.datetime] = None,
            max_host_last_seen_time: Optional[datetime.datetime] = None,
            min_vulnerability_create_time: Optional[datetime.datetime] = None,
            max_vulnerability_create_time: Optional[datetime.datetime] = None,
            min_vulnerability_update_time: Optional[datetime.datetime] = None,
            max_vulnerability_update_time: Optional[datetime.datetime] = None,
            min_vulnerability_open_time: Optional[datetime.datetime] = None,
            max_vulnerability_open_time: Optional[datetime.datetime] = None,
            min_vulnerability_close_time: Optional[datetime.datetime] = None,
            max_vulnerability_close_time: Optional[datetime.datetime] = None) -> Dict[Asset, List[Host]]:

        #: Lookup assets.
        assets = self.get_assets(
            ids=asset_ids,
            names=asset_names,
            tags=asset_tags,
            min_asset_create_time=min_asset_create_time,
            max_asset_create_time=max_asset_create_time,
            min_asset_update_time=min_asset_update_time,
            max_asset_update_time=max_asset_update_time,
            min_next_assessment_time=min_next_assessment_time,
            max_next_assessment_time=max_next_assessment_time,
            min_last_assessment_time=min_last_assessment_time,
            max_last_assessment_time=max_last_assessment_time,
            min_last_host_scan_time=min_last_host_scan_time,
            max_last_host_scan_time=max_last_host_scan_time,
        )
        assets_by_id = dict((asset.id, asset) for asset in assets)
        asset_ids = set(assets_by_id.keys())

        #: Lookup hosts.
        hosts = self.get_hosts(
            ids=host_ids,
            asset_ids=asset_ids,
            hostnames=hostnames,
            ip_addresses=ip_addresses,
            os_types=os_types,
            os_versions=os_versions,
            alive=alive,
            vulnerability_ids=vulnerability_ids,
            vulnerability_names=vulnerability_names,
            cve_ids=cve_ids,
            min_host_last_seen_time=min_host_last_seen_time,
            max_host_last_seen_time=max_host_last_seen_time,
            min_vulnerability_create_time=min_vulnerability_create_time,
            max_vulnerability_create_time=max_vulnerability_create_time,
            min_vulnerability_update_time=min_vulnerability_update_time,
            max_vulnerability_update_time=max_vulnerability_update_time,
            min_vulnerability_open_time=min_vulnerability_open_time,
            max_vulnerability_open_time=max_vulnerability_open_time,
            min_vulnerability_close_time=min_vulnerability_close_time,
            max_vulnerability_close_time=max_vulnerability_close_time,
        )

        #: Construct a mapping of the form (assets -> hosts).
        hosts_by_asset = collections.defaultdict(list)
        for host in hosts:
            asset = assets_by_id.get(host.asset_id)
            if asset:
                hosts_by_asset[asset].append(host)
        return hosts_by_asset

    def get_map_of_assets_to_vulnerabilities(
            self,
            asset_ids: Optional[Iterable[int]] = None,
            asset_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            vulnerability_ids: Optional[Iterable[int]] = None,
            vulnerability_names: Optional[Iterable[str]] = None,
            vulnerability_affects_pci_compliance: Optional[bool] = None,
            include_application_layer_vulnerabilities: Optional[bool] = True,
            include_network_layer_vulnerabilities: Optional[bool] = True,
            cve_ids: Optional[Iterable[str]] = None,
            host_ids: Optional[Iterable[int]] = None,
            hostnames: Optional[Iterable[str]] = None,
            ip_addresses: Optional[Iterable[str]] = None,
            os_types: Optional[Iterable[str]] = None,
            os_versions: Optional[Iterable[str]] = None,
            alive: Optional[bool] = None,
            min_asset_create_time: Optional[datetime.datetime] = None,
            max_asset_create_time: Optional[datetime.datetime] = None,
            min_asset_update_time: Optional[datetime.datetime] = None,
            max_asset_update_time: Optional[datetime.datetime] = None,
            min_next_assessment_time: Optional[datetime.datetime] = None,
            max_next_assessment_time: Optional[datetime.datetime] = None,
            min_last_assessment_time: Optional[datetime.datetime] = None,
            max_last_assessment_time: Optional[datetime.datetime] = None,
            min_last_host_scan_time: Optional[datetime.datetime] = None,
            max_last_host_scan_time: Optional[datetime.datetime] = None,
            min_host_last_seen_time: Optional[datetime.datetime] = None,
            max_host_last_seen_time: Optional[datetime.datetime] = None,
            min_vulnerability_create_time: Optional[datetime.datetime] = None,
            max_vulnerability_create_time: Optional[datetime.datetime] = None,
            min_vulnerability_update_time: Optional[datetime.datetime] = None,
            max_vulnerability_update_time: Optional[datetime.datetime] = None,
            min_vulnerability_open_time: Optional[datetime.datetime] = None,
            max_vulnerability_open_time: Optional[datetime.datetime] = None,
            min_vulnerability_close_time: Optional[datetime.datetime] = None,
            max_vulnerability_close_time: Optional[datetime.datetime] = None) -> Dict[Asset, List[Vulnerability]]:

        #: Lookup assets.
        assets = self.get_assets(
            ids=asset_ids,
            names=asset_names,
            tags=asset_tags,
            host_ids=host_ids,
            hostnames=hostnames,
            ip_addresses=ip_addresses,
            os_types=os_types,
            os_versions=os_versions,
            alive=alive,
            min_asset_create_time=min_asset_create_time,
            max_asset_create_time=max_asset_create_time,
            min_asset_update_time=min_asset_update_time,
            max_asset_update_time=max_asset_update_time,
            min_next_assessment_time=min_next_assessment_time,
            max_next_assessment_time=max_next_assessment_time,
            min_last_assessment_time=min_last_assessment_time,
            max_last_assessment_time=max_last_assessment_time,
            min_last_host_scan_time=min_last_host_scan_time,
            max_last_host_scan_time=max_last_host_scan_time,
            min_host_last_seen_time=min_host_last_seen_time,
            max_host_last_seen_time=max_host_last_seen_time,
        )
        assets_by_id = dict((asset.id, asset) for asset in assets)
        asset_ids = set(assets_by_id.keys())

        #: Lookup vulnerabilities.
        vulnerabilities = self.get_vulnerabilities(
            ids=vulnerability_ids,
            names=vulnerability_names,
            affects_pci_compliance=vulnerability_affects_pci_compliance,
            include_application_layer_vulnerabilities=include_application_layer_vulnerabilities,
            include_network_layer_vulnerabilities=include_network_layer_vulnerabilities,
            cve_ids=cve_ids,
            asset_ids=asset_ids,
            min_vulnerability_create_time=min_vulnerability_create_time,
            max_vulnerability_create_time=max_vulnerability_create_time,
            min_vulnerability_update_time=min_vulnerability_update_time,
            max_vulnerability_update_time=max_vulnerability_update_time,
            min_vulnerability_open_time=min_vulnerability_open_time,
            max_vulnerability_open_time=max_vulnerability_open_time,
            min_vulnerability_close_time=min_vulnerability_close_time,
            max_vulnerability_close_time=max_vulnerability_close_time,
        )

        #: Construct the mapping between assets and vulnerabilities.
        vulnerabilities_by_asset = collections.defaultdict(list)
        for vulnerability in vulnerabilities:
            asset = assets_by_id.get(vulnerability.asset_id)
            if asset:
                vulnerabilities_by_asset[asset].append(vulnerability)
        return vulnerabilities_by_asset

    def get_map_of_hosts_to_vulnerabilities(
            self,
            host_ids: Optional[Iterable[int]] = None,
            hostnames: Optional[Iterable[str]] = None,
            ip_addresses: Optional[Iterable[str]] = None,
            os_types: Optional[Iterable[str]] = None,
            os_versions: Optional[Iterable[str]] = None,
            alive: Optional[bool] = None,
            vulnerability_ids: Optional[Iterable[int]] = None,
            vulnerability_names: Optional[Iterable[str]] = None,
            vulnerability_affects_pci_compliance: Optional[bool] = None,
            include_application_layer_vulnerabilities: Optional[bool] = True,
            include_network_layer_vulnerabilities: Optional[bool] = True,
            cve_ids: Optional[Iterable[str]] = None,
            asset_ids: Optional[Iterable[int]] = None,
            asset_names: Optional[Iterable[str]] = None,
            asset_tags: Optional[Iterable[str]] = None,
            min_asset_create_time: Optional[datetime.datetime] = None,
            max_asset_create_time: Optional[datetime.datetime] = None,
            min_asset_update_time: Optional[datetime.datetime] = None,
            max_asset_update_time: Optional[datetime.datetime] = None,
            min_next_assessment_time: Optional[datetime.datetime] = None,
            max_next_assessment_time: Optional[datetime.datetime] = None,
            min_last_assessment_time: Optional[datetime.datetime] = None,
            max_last_assessment_time: Optional[datetime.datetime] = None,
            min_last_host_scan_time: Optional[datetime.datetime] = None,
            max_last_host_scan_time: Optional[datetime.datetime] = None,
            min_host_last_seen_time: Optional[datetime.datetime] = None,
            max_host_last_seen_time: Optional[datetime.datetime] = None,
            min_vulnerability_create_time: Optional[datetime.datetime] = None,
            max_vulnerability_create_time: Optional[datetime.datetime] = None,
            min_vulnerability_update_time: Optional[datetime.datetime] = None,
            max_vulnerability_update_time: Optional[datetime.datetime] = None,
            min_vulnerability_open_time: Optional[datetime.datetime] = None,
            max_vulnerability_open_time: Optional[datetime.datetime] = None,
            min_vulnerability_close_time: Optional[datetime.datetime] = None,
            max_vulnerability_close_time: Optional[datetime.datetime] = None) -> Dict[Host, List[Vulnerability]]:

        #: Lookup hosts.
        hosts = self.get_hosts(
            ids=host_ids,
            hostnames=hostnames,
            ip_addresses=ip_addresses,
            os_types=os_types,
            os_versions=os_versions,
            alive=alive,
            asset_ids=asset_ids,
            asset_names=asset_names,
            asset_tags=asset_tags,
            min_asset_create_time=min_asset_create_time,
            max_asset_create_time=max_asset_create_time,
            min_asset_update_time=min_asset_update_time,
            max_asset_update_time=max_asset_update_time,
            min_next_assessment_time=min_next_assessment_time,
            max_next_assessment_time=max_next_assessment_time,
            min_last_assessment_time=min_last_assessment_time,
            max_last_assessment_time=max_last_assessment_time,
            min_last_host_scan_time=min_last_host_scan_time,
            max_last_host_scan_time=max_last_host_scan_time,
            min_host_last_seen_time=min_host_last_seen_time,
            max_host_last_seen_time=max_host_last_seen_time,
        )

        #: Lookup vulnerabilities.
        vulnerabilities = self.get_vulnerabilities(
            ids=vulnerability_ids,
            names=vulnerability_names,
            affects_pci_compliance=vulnerability_affects_pci_compliance,
            include_application_layer_vulnerabilities=include_application_layer_vulnerabilities,
            include_network_layer_vulnerabilities=include_network_layer_vulnerabilities,
            cve_ids=cve_ids,
            asset_ids=asset_ids,
            min_vulnerability_create_time=min_vulnerability_create_time,
            max_vulnerability_create_time=max_vulnerability_create_time,
            min_vulnerability_update_time=min_vulnerability_update_time,
            max_vulnerability_update_time=max_vulnerability_update_time,
            min_vulnerability_open_time=min_vulnerability_open_time,
            max_vulnerability_open_time=max_vulnerability_open_time,
            min_vulnerability_close_time=min_vulnerability_close_time,
            max_vulnerability_close_time=max_vulnerability_close_time,
        )

        #: Construct the mapping between hosts and vulnerabilities.
        hosts_by_location = collections.defaultdict(list)
        for host in hosts:
            hosts_by_location[host.location].append(host)

        vulnerabilities_by_host = collections.defaultdict(list)
        for vulnerability in vulnerabilities:
            for host in hosts_by_location.get(vulnerability.location, []):
                vulnerabilities_by_host[host].append(vulnerability)
        return dict(vulnerabilities_by_host)


def _get_collection_type_from_url(url: str) -> str:
    v = urllib.parse.urlsplit(url).path.split('/')[-1]
    if v.endswith('.json'):
        v = v[:-5]

    if v not in COLLECTION_TYPES:
        raise ValueError("Failed to parse collection type from URL: {} - got '{}' - allowed: {}".format(
            url, v, COLLECTION_TYPES
        ))
    return v

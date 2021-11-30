from typing import Optional
from edgescan.api.client import EdgeScan
from edgescan.constants import DEFAULT_INDENT, SORT_KEYS_BY_DEFAULT

import itertools
import json
import edgescan.cli.cli_helpers as cli
import collections
import ipaddress
import click


@click.group()
@click.pass_context
def assets(_):
    """
    Query or count assets.
    """
    pass


@assets.command()
@click.option('--asset-id', type=int, required=True)
@click.pass_context
def get_asset(ctx: click.Context, asset_id: int):
    api = EdgeScan(**ctx.obj['config']['edgescan']['api'])
    asset = api.get_asset(asset_id)
    if asset:
        click.echo(asset.to_json())


@assets.command()
@click.option('--asset-ids')
@click.option('--asset-names')
@click.option('--asset-tags')
@click.option('--host-ids')
@click.option('--hostnames')
@click.option('--ip-addresses')
@click.option('--os-types')
@click.option('--os-versions')
@click.option('--alive/--dead', default=None)
@click.option('--vulnerability-ids')
@click.option('--vulnerability-names')
@click.option('--cve-ids')
@click.option('--min-asset-create-time')
@click.option('--max-asset-create-time')
@click.option('--min-asset-update-time')
@click.option('--max-asset-update-time')
@click.option('--min-next-assessment-time')
@click.option('--max-next-assessment-time')
@click.option('--min-last-assessment-time')
@click.option('--max-last-assessment-time')
@click.option('--min-last-host-scan-time')
@click.option('--max-last-host-scan-time')
@click.option('--min-host-last-seen-time')
@click.option('--max-host-last-seen-time')
@click.option('--min-vulnerability-create-time')
@click.option('--max-vulnerability-create-time')
@click.option('--min-vulnerability-update-time')
@click.option('--max-vulnerability-update-time')
@click.option('--min-vulnerability-open-time')
@click.option('--max-vulnerability-open-time')
@click.option('--min-vulnerability-close-time')
@click.option('--max-vulnerability-close-time')
@click.option('--limit', type=int)
@click.pass_context
def get_assets(
        ctx: click.Context,
        asset_ids: Optional[str],
        asset_names: Optional[str],
        asset_tags: Optional[str],
        host_ids: Optional[str],
        hostnames: Optional[str],
        ip_addresses: Optional[str],
        os_types: Optional[str],
        os_versions: Optional[str],
        alive: Optional[bool],
        vulnerability_ids: Optional[str],
        vulnerability_names: Optional[str],
        cve_ids: Optional[str],
        min_asset_create_time: Optional[str],
        max_asset_create_time: Optional[str],
        min_asset_update_time: Optional[str],
        max_asset_update_time: Optional[str],
        min_next_assessment_time: Optional[str],
        max_next_assessment_time: Optional[str],
        min_last_assessment_time: Optional[str],
        max_last_assessment_time: Optional[str],
        min_last_host_scan_time: Optional[str],
        max_last_host_scan_time: Optional[str],
        min_host_last_seen_time: Optional[str],
        max_host_last_seen_time: Optional[str],
        min_vulnerability_create_time: Optional[str],
        max_vulnerability_create_time: Optional[str],
        min_vulnerability_update_time: Optional[str],
        max_vulnerability_update_time: Optional[str],
        min_vulnerability_open_time: Optional[str],
        max_vulnerability_open_time: Optional[str],
        min_vulnerability_close_time: Optional[str],
        max_vulnerability_close_time: Optional[str],
        limit: Optional[int] = None):

    api = EdgeScan(**ctx.obj['config']['edgescan']['api'])
    for asset in api.iter_assets(
        ids=cli.str_to_ints(asset_ids),
        names=cli.str_to_strs(asset_names),
        tags=cli.str_to_strs(asset_tags),
        host_ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        vulnerability_ids=cli.str_to_ints(vulnerability_ids),
        vulnerability_names=cli.str_to_strs(vulnerability_names),
        cve_ids=cli.str_to_strs(cve_ids),
        min_asset_create_time=cli.str_to_datetime(min_asset_create_time),
        max_asset_create_time=cli.str_to_datetime(max_asset_create_time),
        min_asset_update_time=cli.str_to_datetime(min_asset_update_time),
        max_asset_update_time=cli.str_to_datetime(max_asset_update_time),
        min_next_assessment_time=cli.str_to_datetime(min_next_assessment_time),
        max_next_assessment_time=cli.str_to_datetime(max_next_assessment_time),
        min_last_assessment_time=cli.str_to_datetime(min_last_assessment_time),
        max_last_assessment_time=cli.str_to_datetime(max_last_assessment_time),
        min_last_host_scan_time=cli.str_to_datetime(min_last_host_scan_time),
        max_last_host_scan_time=cli.str_to_datetime(max_last_host_scan_time),
        min_host_last_seen_time=cli.str_to_datetime(min_host_last_seen_time),
        max_host_last_seen_time=cli.str_to_datetime(max_host_last_seen_time),
        min_vulnerability_create_time=cli.str_to_datetime(min_vulnerability_create_time),
        max_vulnerability_create_time=cli.str_to_datetime(max_vulnerability_create_time),
        min_vulnerability_update_time=cli.str_to_datetime(min_vulnerability_update_time),
        max_vulnerability_update_time=cli.str_to_datetime(max_vulnerability_update_time),
        min_vulnerability_open_time=cli.str_to_datetime(min_vulnerability_open_time),
        max_vulnerability_open_time=cli.str_to_datetime(max_vulnerability_open_time),
        min_vulnerability_close_time=cli.str_to_datetime(min_vulnerability_close_time),
        max_vulnerability_close_time=cli.str_to_datetime(max_vulnerability_close_time),
        limit=limit,
    ):
        click.echo(asset.to_json())


@assets.command()
@click.option('--asset-ids')
@click.option('--asset-names')
@click.option('--asset-tags')
@click.option('--host-ids')
@click.option('--hostnames')
@click.option('--ip-addresses')
@click.option('--os-types')
@click.option('--os-versions')
@click.option('--alive/--dead', default=None)
@click.option('--vulnerability-ids')
@click.option('--vulnerability-names')
@click.option('--cve-ids')
@click.option('--min-asset-create-time')
@click.option('--max-asset-create-time')
@click.option('--min-asset-update-time')
@click.option('--max-asset-update-time')
@click.option('--min-next-assessment-time')
@click.option('--max-next-assessment-time')
@click.option('--min-last-assessment-time')
@click.option('--max-last-assessment-time')
@click.option('--min-last-host-scan-time')
@click.option('--max-last-host-scan-time')
@click.option('--min-host-last-seen-time')
@click.option('--max-host-last-seen-time')
@click.option('--min-vulnerability-create-time')
@click.option('--max-vulnerability-create-time')
@click.option('--min-vulnerability-update-time')
@click.option('--max-vulnerability-update-time')
@click.option('--min-vulnerability-open-time')
@click.option('--max-vulnerability-open-time')
@click.option('--min-vulnerability-close-time')
@click.option('--max-vulnerability-close-time')
@click.pass_context
def get_asset_tags(
        ctx: click.Context,
        asset_ids: Optional[str],
        asset_names: Optional[str],
        asset_tags: Optional[str],
        host_ids: Optional[str],
        hostnames: Optional[str],
        ip_addresses: Optional[str],
        os_types: Optional[str],
        os_versions: Optional[str],
        alive: Optional[bool],
        vulnerability_ids: Optional[str],
        vulnerability_names: Optional[str],
        cve_ids: Optional[str],
        min_asset_create_time: Optional[str],
        max_asset_create_time: Optional[str],
        min_asset_update_time: Optional[str],
        max_asset_update_time: Optional[str],
        min_next_assessment_time: Optional[str],
        max_next_assessment_time: Optional[str],
        min_last_assessment_time: Optional[str],
        max_last_assessment_time: Optional[str],
        min_last_host_scan_time: Optional[str],
        max_last_host_scan_time: Optional[str],
        min_host_last_seen_time: Optional[str],
        max_host_last_seen_time: Optional[str],
        min_vulnerability_create_time: Optional[str],
        max_vulnerability_create_time: Optional[str],
        min_vulnerability_update_time: Optional[str],
        max_vulnerability_update_time: Optional[str],
        min_vulnerability_open_time: Optional[str],
        max_vulnerability_open_time: Optional[str],
        min_vulnerability_close_time: Optional[str],
        max_vulnerability_close_time: Optional[str]):

    api = EdgeScan(**ctx.obj['config']['edgescan']['api'])
    rows = api.iter_assets(
        ids=cli.str_to_ints(asset_ids),
        names=cli.str_to_strs(asset_names),
        tags=cli.str_to_strs(asset_tags),
        host_ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        vulnerability_ids=cli.str_to_ints(vulnerability_ids),
        vulnerability_names=cli.str_to_strs(vulnerability_names),
        cve_ids=cli.str_to_strs(cve_ids),
        min_asset_create_time=cli.str_to_datetime(min_asset_create_time),
        max_asset_create_time=cli.str_to_datetime(max_asset_create_time),
        min_asset_update_time=cli.str_to_datetime(min_asset_update_time),
        max_asset_update_time=cli.str_to_datetime(max_asset_update_time),
        min_next_assessment_time=cli.str_to_datetime(min_next_assessment_time),
        max_next_assessment_time=cli.str_to_datetime(max_next_assessment_time),
        min_last_assessment_time=cli.str_to_datetime(min_last_assessment_time),
        max_last_assessment_time=cli.str_to_datetime(max_last_assessment_time),
        min_last_host_scan_time=cli.str_to_datetime(min_last_host_scan_time),
        max_last_host_scan_time=cli.str_to_datetime(max_last_host_scan_time),
        min_host_last_seen_time=cli.str_to_datetime(min_host_last_seen_time),
        max_host_last_seen_time=cli.str_to_datetime(max_host_last_seen_time),
        min_vulnerability_create_time=cli.str_to_datetime(min_vulnerability_create_time),
        max_vulnerability_create_time=cli.str_to_datetime(max_vulnerability_create_time),
        min_vulnerability_update_time=cli.str_to_datetime(min_vulnerability_update_time),
        max_vulnerability_update_time=cli.str_to_datetime(max_vulnerability_update_time),
        min_vulnerability_open_time=cli.str_to_datetime(min_vulnerability_open_time),
        max_vulnerability_open_time=cli.str_to_datetime(max_vulnerability_open_time),
        min_vulnerability_close_time=cli.str_to_datetime(min_vulnerability_close_time),
        max_vulnerability_close_time=cli.str_to_datetime(max_vulnerability_close_time),
    )
    tags = sorted(set(itertools.chain.from_iterable(row.tags for row in rows)))
    click.echo(json.dumps(tags))


@assets.command()
@click.option('--asset-ids')
@click.option('--asset-names')
@click.option('--asset-tags')
@click.option('--host-ids')
@click.option('--hostnames')
@click.option('--ip-addresses')
@click.option('--os-types')
@click.option('--os-versions')
@click.option('--alive/--dead', default=None)
@click.option('--vulnerability-ids')
@click.option('--vulnerability-names')
@click.option('--cve-ids')
@click.option('--min-asset-create-time')
@click.option('--max-asset-create-time')
@click.option('--min-asset-update-time')
@click.option('--max-asset-update-time')
@click.option('--min-next-assessment-time')
@click.option('--max-next-assessment-time')
@click.option('--min-last-assessment-time')
@click.option('--max-last-assessment-time')
@click.option('--min-last-host-scan-time')
@click.option('--max-last-host-scan-time')
@click.option('--min-host-last-seen-time')
@click.option('--max-host-last-seen-time')
@click.option('--min-vulnerability-create-time')
@click.option('--max-vulnerability-create-time')
@click.option('--min-vulnerability-update-time')
@click.option('--max-vulnerability-update-time')
@click.option('--min-vulnerability-open-time')
@click.option('--max-vulnerability-open-time')
@click.option('--min-vulnerability-close-time')
@click.option('--max-vulnerability-close-time')
@click.pass_context
def count_assets(
        ctx: click.Context,
        asset_ids: Optional[str],
        asset_names: Optional[str],
        asset_tags: Optional[str],
        host_ids: Optional[str],
        hostnames: Optional[str],
        ip_addresses: Optional[str],
        os_types: Optional[str],
        os_versions: Optional[str],
        alive: Optional[bool],
        vulnerability_ids: Optional[str],
        vulnerability_names: Optional[str],
        cve_ids: Optional[str],
        min_asset_create_time: Optional[str],
        max_asset_create_time: Optional[str],
        min_asset_update_time: Optional[str],
        max_asset_update_time: Optional[str],
        min_next_assessment_time: Optional[str],
        max_next_assessment_time: Optional[str],
        min_last_assessment_time: Optional[str],
        max_last_assessment_time: Optional[str],
        min_last_host_scan_time: Optional[str],
        max_last_host_scan_time: Optional[str],
        min_host_last_seen_time: Optional[str],
        max_host_last_seen_time: Optional[str],
        min_vulnerability_create_time: Optional[str],
        max_vulnerability_create_time: Optional[str],
        min_vulnerability_update_time: Optional[str],
        max_vulnerability_update_time: Optional[str],
        min_vulnerability_open_time: Optional[str],
        max_vulnerability_open_time: Optional[str],
        min_vulnerability_close_time: Optional[str],
        max_vulnerability_close_time: Optional[str]):

    api = EdgeScan(**ctx.obj['config']['edgescan']['api'])
    total = api.count_assets(
        ids=cli.str_to_ints(asset_ids),
        names=cli.str_to_strs(asset_names),
        tags=cli.str_to_strs(asset_tags),
        host_ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        vulnerability_ids=cli.str_to_ints(vulnerability_ids),
        vulnerability_names=cli.str_to_strs(vulnerability_names),
        cve_ids=cli.str_to_strs(cve_ids),
        min_asset_create_time=cli.str_to_datetime(min_asset_create_time),
        max_asset_create_time=cli.str_to_datetime(max_asset_create_time),
        min_asset_update_time=cli.str_to_datetime(min_asset_update_time),
        max_asset_update_time=cli.str_to_datetime(max_asset_update_time),
        min_next_assessment_time=cli.str_to_datetime(min_next_assessment_time),
        max_next_assessment_time=cli.str_to_datetime(max_next_assessment_time),
        min_last_assessment_time=cli.str_to_datetime(min_last_assessment_time),
        max_last_assessment_time=cli.str_to_datetime(max_last_assessment_time),
        min_last_host_scan_time=cli.str_to_datetime(min_last_host_scan_time),
        max_last_host_scan_time=cli.str_to_datetime(max_last_host_scan_time),
        min_host_last_seen_time=cli.str_to_datetime(min_host_last_seen_time),
        max_host_last_seen_time=cli.str_to_datetime(max_host_last_seen_time),
        min_vulnerability_create_time=cli.str_to_datetime(min_vulnerability_create_time),
        max_vulnerability_create_time=cli.str_to_datetime(max_vulnerability_create_time),
        min_vulnerability_update_time=cli.str_to_datetime(min_vulnerability_update_time),
        max_vulnerability_update_time=cli.str_to_datetime(max_vulnerability_update_time),
        min_vulnerability_open_time=cli.str_to_datetime(min_vulnerability_open_time),
        max_vulnerability_open_time=cli.str_to_datetime(max_vulnerability_open_time),
        min_vulnerability_close_time=cli.str_to_datetime(min_vulnerability_close_time),
        max_vulnerability_close_time=cli.str_to_datetime(max_vulnerability_close_time)
    )
    click.echo(total)


@assets.command()
@click.option('--asset-ids')
@click.option('--asset-names')
@click.option('--asset-tags')
@click.option('--host-ids')
@click.option('--hostnames')
@click.option('--ip-addresses')
@click.option('--os-types')
@click.option('--os-versions')
@click.option('--alive/--dead', default=None)
@click.option('--vulnerability-ids')
@click.option('--vulnerability-names')
@click.option('--cve-ids')
@click.option('--min-asset-create-time')
@click.option('--max-asset-create-time')
@click.option('--min-asset-update-time')
@click.option('--max-asset-update-time')
@click.option('--min-next-assessment-time')
@click.option('--max-next-assessment-time')
@click.option('--min-last-assessment-time')
@click.option('--max-last-assessment-time')
@click.option('--min-last-host-scan-time')
@click.option('--max-last-host-scan-time')
@click.option('--min-host-last-seen-time')
@click.option('--max-host-last-seen-time')
@click.option('--min-vulnerability-create-time')
@click.option('--max-vulnerability-create-time')
@click.option('--min-vulnerability-update-time')
@click.option('--max-vulnerability-update-time')
@click.option('--min-vulnerability-open-time')
@click.option('--max-vulnerability-open-time')
@click.option('--min-vulnerability-close-time')
@click.option('--max-vulnerability-close-time')
@click.pass_context
def get_hostnames_by_asset_name(
        ctx: click.Context,
        asset_ids: Optional[str],
        asset_names: Optional[str],
        asset_tags: Optional[str],
        host_ids: Optional[str],
        hostnames: Optional[str],
        ip_addresses: Optional[str],
        os_types: Optional[str],
        os_versions: Optional[str],
        alive: Optional[bool],
        vulnerability_ids: Optional[str],
        vulnerability_names: Optional[str],
        cve_ids: Optional[str],
        min_asset_create_time: Optional[str],
        max_asset_create_time: Optional[str],
        min_asset_update_time: Optional[str],
        max_asset_update_time: Optional[str],
        min_next_assessment_time: Optional[str],
        max_next_assessment_time: Optional[str],
        min_last_assessment_time: Optional[str],
        max_last_assessment_time: Optional[str],
        min_last_host_scan_time: Optional[str],
        max_last_host_scan_time: Optional[str],
        min_host_last_seen_time: Optional[str],
        max_host_last_seen_time: Optional[str],
        min_vulnerability_create_time: Optional[str],
        max_vulnerability_create_time: Optional[str],
        min_vulnerability_update_time: Optional[str],
        max_vulnerability_update_time: Optional[str],
        min_vulnerability_open_time: Optional[str],
        max_vulnerability_open_time: Optional[str],
        min_vulnerability_close_time: Optional[str],
        max_vulnerability_close_time: Optional[str]):

    #: Lookup assets.
    api = EdgeScan(**ctx.obj['config']['edgescan']['api'])
    hosts_by_asset = api.get_map_of_asset_to_hosts(
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
        host_ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        vulnerability_ids=cli.str_to_ints(vulnerability_ids),
        vulnerability_names=cli.str_to_strs(vulnerability_names),
        cve_ids=cli.str_to_strs(cve_ids),
        min_asset_create_time=cli.str_to_datetime(min_asset_create_time),
        max_asset_create_time=cli.str_to_datetime(max_asset_create_time),
        min_asset_update_time=cli.str_to_datetime(min_asset_update_time),
        max_asset_update_time=cli.str_to_datetime(max_asset_update_time),
        min_next_assessment_time=cli.str_to_datetime(min_next_assessment_time),
        max_next_assessment_time=cli.str_to_datetime(max_next_assessment_time),
        min_last_assessment_time=cli.str_to_datetime(min_last_assessment_time),
        max_last_assessment_time=cli.str_to_datetime(max_last_assessment_time),
        min_last_host_scan_time=cli.str_to_datetime(min_last_host_scan_time),
        max_last_host_scan_time=cli.str_to_datetime(max_last_host_scan_time),
        min_host_last_seen_time=cli.str_to_datetime(min_host_last_seen_time),
        max_host_last_seen_time=cli.str_to_datetime(max_host_last_seen_time),
        min_vulnerability_create_time=cli.str_to_datetime(min_vulnerability_create_time),
        max_vulnerability_create_time=cli.str_to_datetime(max_vulnerability_create_time),
        min_vulnerability_update_time=cli.str_to_datetime(min_vulnerability_update_time),
        max_vulnerability_update_time=cli.str_to_datetime(max_vulnerability_update_time),
        min_vulnerability_open_time=cli.str_to_datetime(min_vulnerability_open_time),
        max_vulnerability_open_time=cli.str_to_datetime(max_vulnerability_open_time),
        min_vulnerability_close_time=cli.str_to_datetime(min_vulnerability_close_time),
        max_vulnerability_close_time=cli.str_to_datetime(max_vulnerability_close_time)
    )
    hostnames_by_asset_name = collections.defaultdict(list)
    for asset, hosts in hosts_by_asset.items():
        for host in hosts:
            for hostname in host.hostnames:
                if hostname not in hostnames_by_asset_name[asset.name]:
                    hostnames_by_asset_name[asset.name].append(hostname)
    click.echo(json.dumps(hostnames_by_asset_name, indent=DEFAULT_INDENT))


@assets.command()
@click.option('--asset-ids')
@click.option('--asset-names')
@click.option('--asset-tags')
@click.option('--host-ids')
@click.option('--hostnames')
@click.option('--ip-addresses')
@click.option('--os-types')
@click.option('--os-versions')
@click.option('--alive/--dead', default=None)
@click.option('--vulnerability-ids')
@click.option('--vulnerability-names')
@click.option('--cve-ids')
@click.option('--min-asset-create-time')
@click.option('--max-asset-create-time')
@click.option('--min-asset-update-time')
@click.option('--max-asset-update-time')
@click.option('--min-next-assessment-time')
@click.option('--max-next-assessment-time')
@click.option('--min-last-assessment-time')
@click.option('--max-last-assessment-time')
@click.option('--min-last-host-scan-time')
@click.option('--max-last-host-scan-time')
@click.option('--min-host-last-seen-time')
@click.option('--max-host-last-seen-time')
@click.option('--min-vulnerability-create-time')
@click.option('--max-vulnerability-create-time')
@click.option('--min-vulnerability-update-time')
@click.option('--max-vulnerability-update-time')
@click.option('--min-vulnerability-open-time')
@click.option('--max-vulnerability-open-time')
@click.option('--min-vulnerability-close-time')
@click.option('--max-vulnerability-close-time')
@click.pass_context
def get_host_ips_by_asset_name(
        ctx: click.Context,
        asset_ids: Optional[str],
        asset_names: Optional[str],
        asset_tags: Optional[str],
        host_ids: Optional[str],
        hostnames: Optional[str],
        ip_addresses: Optional[str],
        os_types: Optional[str],
        os_versions: Optional[str],
        alive: Optional[bool],
        vulnerability_ids: Optional[str],
        vulnerability_names: Optional[str],
        cve_ids: Optional[str],
        min_asset_create_time: Optional[str],
        max_asset_create_time: Optional[str],
        min_asset_update_time: Optional[str],
        max_asset_update_time: Optional[str],
        min_next_assessment_time: Optional[str],
        max_next_assessment_time: Optional[str],
        min_last_assessment_time: Optional[str],
        max_last_assessment_time: Optional[str],
        min_last_host_scan_time: Optional[str],
        max_last_host_scan_time: Optional[str],
        min_host_last_seen_time: Optional[str],
        max_host_last_seen_time: Optional[str],
        min_vulnerability_create_time: Optional[str],
        max_vulnerability_create_time: Optional[str],
        min_vulnerability_update_time: Optional[str],
        max_vulnerability_update_time: Optional[str],
        min_vulnerability_open_time: Optional[str],
        max_vulnerability_open_time: Optional[str],
        min_vulnerability_close_time: Optional[str],
        max_vulnerability_close_time: Optional[str]):

    #: Lookup assets.
    api = EdgeScan(**ctx.obj['config']['edgescan']['api'])
    hosts_by_asset = api.get_map_of_asset_to_hosts(
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
        host_ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        vulnerability_ids=cli.str_to_ints(vulnerability_ids),
        vulnerability_names=cli.str_to_strs(vulnerability_names),
        cve_ids=cli.str_to_strs(cve_ids),
        min_asset_create_time=cli.str_to_datetime(min_asset_create_time),
        max_asset_create_time=cli.str_to_datetime(max_asset_create_time),
        min_asset_update_time=cli.str_to_datetime(min_asset_update_time),
        max_asset_update_time=cli.str_to_datetime(max_asset_update_time),
        min_next_assessment_time=cli.str_to_datetime(min_next_assessment_time),
        max_next_assessment_time=cli.str_to_datetime(max_next_assessment_time),
        min_last_assessment_time=cli.str_to_datetime(min_last_assessment_time),
        max_last_assessment_time=cli.str_to_datetime(max_last_assessment_time),
        min_last_host_scan_time=cli.str_to_datetime(min_last_host_scan_time),
        max_last_host_scan_time=cli.str_to_datetime(max_last_host_scan_time),
        min_host_last_seen_time=cli.str_to_datetime(min_host_last_seen_time),
        max_host_last_seen_time=cli.str_to_datetime(max_host_last_seen_time),
        min_vulnerability_create_time=cli.str_to_datetime(min_vulnerability_create_time),
        max_vulnerability_create_time=cli.str_to_datetime(max_vulnerability_create_time),
        min_vulnerability_update_time=cli.str_to_datetime(min_vulnerability_update_time),
        max_vulnerability_update_time=cli.str_to_datetime(max_vulnerability_update_time),
        min_vulnerability_open_time=cli.str_to_datetime(min_vulnerability_open_time),
        max_vulnerability_open_time=cli.str_to_datetime(max_vulnerability_open_time),
        min_vulnerability_close_time=cli.str_to_datetime(min_vulnerability_close_time),
        max_vulnerability_close_time=cli.str_to_datetime(max_vulnerability_close_time)
    )
    ips_by_asset_name = collections.defaultdict(set)
    for asset, hosts in hosts_by_asset.items():
        for host in hosts:
            ip = host.ip_address
            if ip:
                ips_by_asset_name[asset.name].add(ip)

    #: Sort each list of IP addresses.
    ips_by_asset_name = dict(ips_by_asset_name)
    for asset_name, ips in ips_by_asset_name.items():
        ips_by_asset_name[asset_name] = sorted(ips, key=lambda _ip: int(ipaddress.ip_address(_ip)))

    click.echo(json.dumps(ips_by_asset_name, indent=DEFAULT_INDENT, sort_keys=SORT_KEYS_BY_DEFAULT))

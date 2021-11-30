from typing import Optional
from edgescan.api.client import EdgeScan
from edgescan.constants import DEFAULT_INDENT, SORT_KEYS_BY_DEFAULT
from hodgepodge.time import HOUR, DAY, MONTH

import hodgepodge.time
import edgescan.cli.cli_helpers as cli
import click
import collections
import json


@click.group()
@click.pass_context
def hosts(_):
    """
    Query or count hosts.
    """
    pass


@hosts.command()
@click.option('--host-id', type=int, required=True)
@click.pass_context
def get_host(ctx: click.Context, host_id: int):
    api = EdgeScan(**ctx.obj['config']['edgescan']['api'])
    host = api.get_host(host_id)
    if host:
        click.echo(host.to_json())


@hosts.command()
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
def get_hosts(
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
        limit: Optional[int]):

    api = EdgeScan(**ctx.obj['config']['edgescan']['api'])
    for host in api.iter_hosts(
        ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
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
        click.echo(host.to_json())


@hosts.command()
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
def count_hosts(
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
    total = api.count_hosts(
        ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
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
    click.echo(total)


@hosts.command()
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
@click.option('--granularity', type=click.Choice(['hour', 'day', 'month']), default='day')
@click.pass_context
def count_hosts_by_last_seen_time(
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
        granularity: str):

    api = EdgeScan(**ctx.obj['config']['edgescan']['api'])
    tally = collections.defaultdict(int)
    for host in api.get_hosts(
        ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
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
    ):
        update_time = host.update_time
        if granularity in [HOUR, DAY, MONTH]:
            update_time = hodgepodge.time.round_datetime(update_time, granularity=granularity)
            if granularity == HOUR:
                update_time = update_time.strftime('%Y-%m-%dT%H:%M')
            else:
                update_time = update_time.date().isoformat()
        else:
            update_time = update_time.isoformat()
        tally[update_time] += 1

    click.echo(json.dumps(tally, indent=DEFAULT_INDENT, sort_keys=SORT_KEYS_BY_DEFAULT))


@hosts.command()
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
def count_hosts_by_status(
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
    tally = collections.defaultdict(int)
    for host in api.get_hosts(
        ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
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
    ):
        tally[host.status] += 1

    click.echo(json.dumps(tally, indent=DEFAULT_INDENT, sort_keys=SORT_KEYS_BY_DEFAULT))


@hosts.command()
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
def count_hosts_by_os_type(
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

    tally = collections.defaultdict(int)
    for host in api.get_hosts(
        ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
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
    ):
        if host.os_type:
            tally[host.os_type] += 1

    click.echo(json.dumps(tally, indent=DEFAULT_INDENT, sort_keys=SORT_KEYS_BY_DEFAULT))


@hosts.command()
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
def count_hosts_by_os_version(
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

    tally = collections.defaultdict(int)
    for host in api.get_hosts(
        ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
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
    ):
        if host.os_version:
            tally[host.os_version] += 1

    click.echo(json.dumps(tally, indent=DEFAULT_INDENT, sort_keys=SORT_KEYS_BY_DEFAULT))


@hosts.command()
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
def count_hosts_by_asset_group_name(
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

    #: Lookup assets.
    assets = api.get_assets(
        ids=cli.str_to_ints(asset_ids),
        names=cli.str_to_strs(asset_names),
        tags=cli.str_to_strs(asset_tags),
    )
    assets_by_id = dict((asset.id, asset) for asset in assets)
    asset_ids = list(assets_by_id.keys())

    #: Lookup and count hosts.
    hosts_by_asset_id = collections.defaultdict(int)
    for host in api.get_hosts(
        ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        asset_ids=asset_ids,
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
    ):
        hosts_by_asset_id[host.asset_id] += 1

    tally = {}
    for asset_id, count in hosts_by_asset_id.items():
        asset_name = assets_by_id[asset_id].name
        tally[asset_name] = count

    click.echo(json.dumps(tally, indent=DEFAULT_INDENT, sort_keys=SORT_KEYS_BY_DEFAULT))

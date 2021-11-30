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
def vulnerabilities(_):
    """
    Query or count vulnerabilities.
    """
    pass


@vulnerabilities.command()
@click.option('--vulnerability-id', type=int, required=True)
@click.pass_context
def get_vulnerability(ctx: click.Context, vulnerability_id: int):
    api = EdgeScan(**ctx.obj['config']['edgescan']['api'])
    vulnerability = api.get_vulnerability(vulnerability_id)
    if vulnerability:
        click.echo(vulnerability.to_json())


@vulnerabilities.command()
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
@click.option('--affects-pci-compliance/--does-not-affect-pci-compliance', default=None)
@click.option('--include-application-layer-vulnerabilities/--exclude-application-layer-vulnerabilities', default=True)
@click.option('--include-network-layer-vulnerabilities/--exclude-network-layer-vulnerabilities', default=True)
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
def get_vulnerabilities(
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
        affects_pci_compliance: Optional[bool],
        include_application_layer_vulnerabilities: Optional[bool],
        include_network_layer_vulnerabilities: Optional[bool],
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
        limit: int):

    api = EdgeScan(**ctx.obj['config']['edgescan']['api'])
    for vulnerability in api.iter_vulnerabilities(
        ids=cli.str_to_ints(vulnerability_ids),
        names=cli.str_to_strs(vulnerability_names),
        cve_ids=cli.str_to_strs(cve_ids),
        affects_pci_compliance=affects_pci_compliance,
        include_application_layer_vulnerabilities=include_application_layer_vulnerabilities,
        include_network_layer_vulnerabilities=include_network_layer_vulnerabilities,
        host_ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
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
        click.echo(vulnerability.to_json())


@vulnerabilities.command()
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
@click.option('--affects-pci-compliance/--does-not-affect-pci-compliance', default=None)
@click.option('--include-application-layer-vulnerabilities/--exclude-application-layer-vulnerabilities', default=True)
@click.option('--include-network-layer-vulnerabilities/--exclude-network-layer-vulnerabilities', default=True)
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
def count_vulnerabilities(
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
        affects_pci_compliance: Optional[bool],
        include_application_layer_vulnerabilities: Optional[bool],
        include_network_layer_vulnerabilities: Optional[bool],
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
    total = api.count_vulnerabilities(
        ids=cli.str_to_ints(vulnerability_ids),
        names=cli.str_to_strs(vulnerability_names),
        cve_ids=cli.str_to_strs(cve_ids),
        affects_pci_compliance=affects_pci_compliance,
        include_application_layer_vulnerabilities=include_application_layer_vulnerabilities,
        include_network_layer_vulnerabilities=include_network_layer_vulnerabilities,
        host_ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
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


@vulnerabilities.command()
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
@click.option('--affects-pci-compliance/--does-not-affect-pci-compliance', default=None)
@click.option('--include-application-layer-vulnerabilities/--exclude-application-layer-vulnerabilities', default=True)
@click.option('--include-network-layer-vulnerabilities/--exclude-network-layer-vulnerabilities', default=True)
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
def count_vulnerabilities_by_asset_group_name(
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
        affects_pci_compliance: Optional[bool],
        include_application_layer_vulnerabilities: Optional[bool],
        include_network_layer_vulnerabilities: Optional[bool],
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

    vulnerabilities_by_asset = api.get_map_of_assets_to_vulnerabilities(
        cve_ids=cli.str_to_strs(cve_ids),
        vulnerability_ids=cli.str_to_ints(vulnerability_ids),
        vulnerability_names=cli.str_to_strs(vulnerability_names),
        vulnerability_affects_pci_compliance=affects_pci_compliance,
        include_application_layer_vulnerabilities=include_application_layer_vulnerabilities,
        include_network_layer_vulnerabilities=include_network_layer_vulnerabilities,
        host_ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
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
    vulnerabilities_by_asset_name = {}
    for asset, vulns in vulnerabilities_by_asset.items():
        vulnerabilities_by_asset_name[asset.name] = len(vulns)
    click.echo(json.dumps(vulnerabilities_by_asset_name, indent=DEFAULT_INDENT, sort_keys=SORT_KEYS_BY_DEFAULT))


@vulnerabilities.command()
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
@click.option('--affects-pci-compliance/--does-not-affect-pci-compliance', default=None)
@click.option('--include-application-layer-vulnerabilities/--exclude-application-layer-vulnerabilities', default=True)
@click.option('--include-network-layer-vulnerabilities/--exclude-network-layer-vulnerabilities', default=True)
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
def count_vulnerabilities_by_location(
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
        affects_pci_compliance: Optional[bool],
        include_application_layer_vulnerabilities: Optional[bool],
        include_network_layer_vulnerabilities: Optional[bool],
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

    vulnerabilities_by_location = collections.defaultdict(int)
    for vulnerability in api.get_vulnerabilities(
        ids=cli.str_to_ints(vulnerability_ids),
        names=cli.str_to_strs(vulnerability_names),
        cve_ids=cli.str_to_strs(cve_ids),
        affects_pci_compliance=affects_pci_compliance,
        include_application_layer_vulnerabilities=include_application_layer_vulnerabilities,
        include_network_layer_vulnerabilities=include_network_layer_vulnerabilities,
        host_ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
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
        vulnerabilities_by_location[vulnerability.location] += 1
    click.echo(json.dumps(vulnerabilities_by_location, indent=DEFAULT_INDENT, sort_keys=SORT_KEYS_BY_DEFAULT))


@vulnerabilities.command()
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
@click.option('--affects-pci-compliance/--does-not-affect-pci-compliance', default=None)
@click.option('--include-application-layer-vulnerabilities/--exclude-application-layer-vulnerabilities', default=True)
@click.option('--include-network-layer-vulnerabilities/--exclude-network-layer-vulnerabilities', default=True)
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
def count_vulnerabilities_by_cve_id(
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
        affects_pci_compliance: Optional[bool],
        include_application_layer_vulnerabilities: Optional[bool],
        include_network_layer_vulnerabilities: Optional[bool],
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

    vulnerabilities_by_cve_id = collections.defaultdict(int)
    for vulnerability in api.get_vulnerabilities(
        ids=cli.str_to_ints(vulnerability_ids),
        names=cli.str_to_strs(vulnerability_names),
        cve_ids=cli.str_to_strs(cve_ids),
        affects_pci_compliance=affects_pci_compliance,
        include_application_layer_vulnerabilities=include_application_layer_vulnerabilities,
        include_network_layer_vulnerabilities=include_network_layer_vulnerabilities,
        host_ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
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
        for cve in vulnerability.cves:
            vulnerabilities_by_cve_id[cve] += 1
    click.echo(json.dumps(vulnerabilities_by_cve_id, indent=DEFAULT_INDENT, sort_keys=SORT_KEYS_BY_DEFAULT))


@vulnerabilities.command()
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
@click.option('--affects-pci-compliance/--does-not-affect-pci-compliance', default=None)
@click.option('--include-application-layer-vulnerabilities/--exclude-application-layer-vulnerabilities', default=True)
@click.option('--include-network-layer-vulnerabilities/--exclude-network-layer-vulnerabilities', default=True)
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
def count_vulnerabilities_by_os_type(
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
        affects_pci_compliance: Optional[bool],
        include_application_layer_vulnerabilities: Optional[bool],
        include_network_layer_vulnerabilities: Optional[bool],
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

    vulnerabilities_by_host = api.get_map_of_hosts_to_vulnerabilities(
        cve_ids=cli.str_to_strs(cve_ids),
        vulnerability_ids=cli.str_to_ints(vulnerability_ids),
        vulnerability_names=cli.str_to_strs(vulnerability_names),
        vulnerability_affects_pci_compliance=affects_pci_compliance,
        include_application_layer_vulnerabilities=include_application_layer_vulnerabilities,
        include_network_layer_vulnerabilities=include_network_layer_vulnerabilities,
        host_ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
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
    vulnerabilities_by_os_type = collections.defaultdict(int)
    for host, vulns in vulnerabilities_by_host.items():
        if host.os_type:
            vulnerabilities_by_os_type[host.os_type] += len(vulns)
    click.echo(json.dumps(vulnerabilities_by_os_type, indent=DEFAULT_INDENT, sort_keys=SORT_KEYS_BY_DEFAULT))


@vulnerabilities.command()
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
@click.option('--affects-pci-compliance/--does-not-affect-pci-compliance', default=None)
@click.option('--include-application-layer-vulnerabilities/--exclude-application-layer-vulnerabilities', default=True)
@click.option('--include-network-layer-vulnerabilities/--exclude-network-layer-vulnerabilities', default=True)
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
def count_vulnerabilities_by_os_version(
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
        affects_pci_compliance: Optional[bool],
        include_application_layer_vulnerabilities: Optional[bool],
        include_network_layer_vulnerabilities: Optional[bool],
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

    vulnerabilities_by_host = api.get_map_of_hosts_to_vulnerabilities(
        cve_ids=cli.str_to_strs(cve_ids),
        vulnerability_ids=cli.str_to_ints(vulnerability_ids),
        vulnerability_names=cli.str_to_strs(vulnerability_names),
        vulnerability_affects_pci_compliance=affects_pci_compliance,
        include_application_layer_vulnerabilities=include_application_layer_vulnerabilities,
        include_network_layer_vulnerabilities=include_network_layer_vulnerabilities,
        host_ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
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
    vulnerabilities_by_os_version = collections.defaultdict(int)
    for host, vulns in vulnerabilities_by_host.items():
        if host.os_version:
            vulnerabilities_by_os_version[host.os_version] += len(vulns)
    click.echo(json.dumps(vulnerabilities_by_os_version, indent=DEFAULT_INDENT, sort_keys=SORT_KEYS_BY_DEFAULT))


@vulnerabilities.command()
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
@click.option('--affects-pci-compliance/--does-not-affect-pci-compliance', default=None)
@click.option('--include-application-layer-vulnerabilities/--exclude-application-layer-vulnerabilities', default=True)
@click.option('--include-network-layer-vulnerabilities/--exclude-network-layer-vulnerabilities', default=True)
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
def count_vulnerabilities_by_open_time(
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
        affects_pci_compliance: Optional[bool],
        include_application_layer_vulnerabilities: Optional[bool],
        include_network_layer_vulnerabilities: Optional[bool],
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
    for vulnerability in api.get_vulnerabilities(
        ids=cli.str_to_ints(vulnerability_ids),
        names=cli.str_to_strs(vulnerability_names),
        cve_ids=cli.str_to_strs(cve_ids),
        affects_pci_compliance=affects_pci_compliance,
        include_application_layer_vulnerabilities=include_application_layer_vulnerabilities,
        include_network_layer_vulnerabilities=include_network_layer_vulnerabilities,
        host_ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
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
        open_time = vulnerability.open_time
        if granularity in [HOUR, DAY, MONTH]:
            open_time = hodgepodge.time.round_datetime(open_time, granularity=granularity)
            if granularity == HOUR:
                open_time = open_time.strftime('%Y-%m-%dT%H:%M')
            else:
                open_time = open_time.date().isoformat()
        else:
            open_time = open_time.isoformat()
        tally[open_time] += 1

    click.echo(json.dumps(tally, indent=DEFAULT_INDENT, sort_keys=SORT_KEYS_BY_DEFAULT))


@vulnerabilities.command()
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
@click.option('--affects-pci-compliance/--does-not-affect-pci-compliance', default=None)
@click.option('--include-application-layer-vulnerabilities/--exclude-application-layer-vulnerabilities', default=True)
@click.option('--include-network-layer-vulnerabilities/--exclude-network-layer-vulnerabilities', default=True)
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
def count_vulnerabilities_by_close_time(
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
        affects_pci_compliance: Optional[bool],
        include_application_layer_vulnerabilities: Optional[bool],
        include_network_layer_vulnerabilities: Optional[bool],
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
    for vulnerability in api.get_vulnerabilities(
        ids=cli.str_to_ints(vulnerability_ids),
        names=cli.str_to_strs(vulnerability_names),
        cve_ids=cli.str_to_strs(cve_ids),
        affects_pci_compliance=affects_pci_compliance,
        include_application_layer_vulnerabilities=include_application_layer_vulnerabilities,
        include_network_layer_vulnerabilities=include_network_layer_vulnerabilities,
        host_ids=cli.str_to_ints(host_ids),
        hostnames=cli.str_to_strs(hostnames),
        ip_addresses=cli.str_to_strs(ip_addresses),
        os_types=cli.str_to_strs(os_types),
        os_versions=cli.str_to_strs(os_versions),
        alive=alive,
        asset_ids=cli.str_to_ints(asset_ids),
        asset_names=cli.str_to_strs(asset_names),
        asset_tags=cli.str_to_strs(asset_tags),
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
        close_time = vulnerability.close_time
        if not close_time:
            continue

        if granularity in [HOUR, DAY, MONTH]:
            close_time = hodgepodge.time.round_datetime(close_time, granularity=granularity)
            if granularity == HOUR:
                close_time = close_time.strftime('%Y-%m-%dT%H:%M')
            else:
                close_time = close_time.date().isoformat()
        else:
            close_time = close_time.isoformat()
        tally[close_time] += 1

    click.echo(json.dumps(tally, indent=DEFAULT_INDENT, sort_keys=SORT_KEYS_BY_DEFAULT))

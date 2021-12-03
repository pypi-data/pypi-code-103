from datetime import datetime
from typing import Any, Dict, IO, Optional

import click
from click import ClickException
import tabulate
import yaml
from yaml.loader import SafeLoader

from anyscale.api import get_anyscale_api_client, get_api_client
from anyscale.cli_logger import _CliLogger
from anyscale.client.openapi_client.api.default_api import DefaultApi
from anyscale.cluster_compute import get_cluster_compute_from_name
from anyscale.sdk.anyscale_client.api.default_api import DefaultApi as AnyscaleApi
from anyscale.sdk.anyscale_client.models.cluster_compute_config import (
    ClusterComputeConfig,
)
from anyscale.sdk.anyscale_client.models.cluster_computes_query import (
    ClusterComputesQuery,
)
from anyscale.sdk.anyscale_client.models.clustercompute_list_response import (
    ClustercomputeListResponse,
)
from anyscale.sdk.anyscale_client.models.create_cluster_compute import (
    CreateClusterCompute,
)
from anyscale.sdk.anyscale_client.models.text_query import TextQuery
from anyscale.util import get_endpoint


log = _CliLogger()  # Anyscale CLI Logger


class ClusterComputeController:
    """
    This controller powers functionalities related to Anyscale
    cluster compute configuration.
    """

    def __init__(
        self,
        api_client: DefaultApi = None,
        anyscale_api_client: AnyscaleApi = None,
        log: _CliLogger = _CliLogger(),
    ):
        if api_client is None:
            api_client = get_api_client()
        self.api_client = api_client
        if anyscale_api_client is None:
            anyscale_api_client = get_anyscale_api_client()
        self.anyscale_api_client = anyscale_api_client
        self.log = log

    def create(self, cluster_compute_file: IO[bytes], name: Optional[str]) -> None:
        """Builds a new cluster compute template
        If name is not provided, a default cluster-compute-name will be used and returned in the command output

        Information in output: Link to cluster compute in UI, cluster compute id
        """

        try:
            cluster_compute: Dict[str, Any] = yaml.load(
                cluster_compute_file, Loader=SafeLoader
            )
        except Exception as e:
            raise ClickException(f"Could not load cluster compute file: {e}")

        cluster_compute_config = ClusterComputeConfig(**cluster_compute)
        if name is None:
            name = "cli-config-{}".format(datetime.now().isoformat())
        cluster_compute_response = self.anyscale_api_client.create_cluster_compute(
            CreateClusterCompute(name=name, config=cluster_compute_config)
        )
        created_cluster_compute = cluster_compute_response.result
        cluster_compute_id = created_cluster_compute.id
        cluster_compute_name = created_cluster_compute.name
        url = get_endpoint(f"/configurations/cluster-computes/{cluster_compute_id}")
        log.info(f"View this cluster compute at: {url}")
        log.info(f"Cluster compute id: {cluster_compute_id}")
        log.info(f"Cluster compute name: {cluster_compute_name}")

    def delete(self, cluster_compute_name: Optional[str], id: Optional[str]) -> None:
        """Deletes the cluster compute with the given name or id.
        Exactly one of cluster_compute_name or id must be provided.
        """

        if int(bool(cluster_compute_name)) + int(bool(id)) != 1:
            raise ClickException(
                "Not deleted. Please provide exactly one of: cluster compute name, id."
            )

        if id:
            self.anyscale_api_client.get_cluster_compute(id)
            cluster_compute_id = id
        else:
            # find the cluster compute id from the name
            query = ClusterComputesQuery(name=TextQuery(equals=cluster_compute_name))
            query_response: ClustercomputeListResponse = self.anyscale_api_client.search_cluster_computes(
                query
            )
            cluster_results = query_response.results
            if len(cluster_results) != 1:
                raise ClickException(
                    f"Not deleted. No cluster compute template exists with the name {cluster_compute_name}."
                )
            cluster_compute_id = cluster_results[0].id
        self.anyscale_api_client.delete_cluster_compute(cluster_compute_id)
        log.info("Cluster compute deleted.")

    def list(
        self,
        cluster_compute_name: Optional[str],
        cluster_compute_id: Optional[str],
        include_shared: bool,
        max_items: int,
    ) -> None:
        cluster_compute_list = []
        if cluster_compute_id:
            cluster_compute_list = [
                self.anyscale_api_client.get_cluster_compute(cluster_compute_id).result
            ]
        elif cluster_compute_name:
            cluster_compute_list = self.anyscale_api_client.search_cluster_computes(
                {"name": {"equals": cluster_compute_name}, "paging": {"count": 1}}
            ).results
        else:
            creator_id = (
                self.api_client.get_user_info_api_v2_userinfo_get().result.id
                if not include_shared
                else None
            )
            has_more = len(cluster_compute_list) < max_items
            while has_more:
                resp = self.anyscale_api_client.search_cluster_computes(
                    {"creator_id": creator_id}
                )
                cluster_compute_list.extend(resp.results)
                paging_token = resp.metadata.next_paging_token
                has_more = (paging_token is not None) and (
                    len(cluster_compute_list) < max_items
                )
            cluster_compute_list = cluster_compute_list[:max_items]

        cluster_compute_table = [
            [
                cluster_compute.id,
                cluster_compute.name,
                self.anyscale_api_client.get_cloud(
                    cluster_compute.config.cloud_id
                ).result.name
                if cluster_compute.config.cloud_id
                else None,
                cluster_compute.last_modified_at.strftime("%m/%d/%Y, %H:%M:%S"),
                get_endpoint(f"configurations/cluster-computes/{cluster_compute.id}"),
            ]
            for cluster_compute in cluster_compute_list
        ]

        table = tabulate.tabulate(
            cluster_compute_table,
            headers=["ID", "NAME", "CLOUD", "LAST MODIFIED AT", "URL"],
            tablefmt="plain",
        )
        print(f"Cluster computes:\n{table}")

    def get(
        self, cluster_compute_name: Optional[str], cluster_compute_id: Optional[str],
    ) -> None:
        if (
            int(cluster_compute_name is not None) + int(cluster_compute_id is not None)
            != 1
        ):
            raise click.ClickException(
                "Please only provide one of `cluster-compute-name` or `--id`."
            )
        if cluster_compute_name:
            cluster_compute_id = get_cluster_compute_from_name(
                cluster_compute_name, self.api_client
            ).id
        config = self.api_client.get_compute_template_api_v2_compute_templates_template_id_get(
            cluster_compute_id
        ).result.config
        # TODO(nikita): Improve formatting here
        print(config)

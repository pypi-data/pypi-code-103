"""
Client used to schedule queries on BigQuery.
"""

import logging
from enum import Enum
from typing import Optional

from google.cloud import bigquery_datatransfer
from google.cloud.bigquery.enums import WriteDisposition

logger = logging.getLogger(__name__)


class DestTableNameTemplate(Enum):
    """Enum used to define BigQuery's table names templates, when applicable."""

    run_date = "_{run_date}"
    run_time = "_{run_time}"
    no_template = ""


class BigQueryDataTransfer:
    """Client used to manipulate BigQuery Data Transfer Service."""

    def __init__(self, project_id: str, service_account: str) -> None:
        """Initializes the class.

        :param project_id: a string containing the Google's project identification
        :type project_id: str
        :param service_account: a string containing a service account e-mail
        :type service_account: str
        """

        self._project_id = project_id
        self._service_account = service_account
        self._bq_datatransfer_client: Optional[
            bigquery_datatransfer.DataTransferServiceClient
        ] = None

    @property
    def bq_datatransfer_client(self) -> bigquery_datatransfer.DataTransferServiceClient:
        """Sets up the BigQuery's DataTransferServiceClient over the class if not present. If
        it is, returns it.

        :return: The Data Transfer Client.
        :rtype: bigquery_datatransfer.DataTransferServiceClient
        """

        if not self._bq_datatransfer_client:
            self._bq_datatransfer_client = (
                bigquery_datatransfer.DataTransferServiceClient()
            )
            self._parent = self._bq_datatransfer_client.common_project_path(
                self._project_id
            )

        return self._bq_datatransfer_client

    def create_or_update_transfer_config(
        self,
        query_str: str,
        dest_dataset_id: str,
        dest_table_id: str,
        squeduled_query_name: str,
        schedule: str,
        dest_table_name_template: str = DestTableNameTemplate.no_template.value,  # noqa: E501
        write_disposition: str = WriteDisposition.WRITE_TRUNCATE,
        partitioning_field: str = "",
    ) -> None:
        """Creates the transfer configuration on Google.

        :param query_str: the SQL statement.
        :type query_str: str
        :param dest_dataset_id: the dataset which will hold the destination data.
        :type dest_dataset_id: str
        :param dest_table_id: the table which will hold the destination data under the
            defined dest_dataset_id.
        :type dest_table_id: str
        :param squeduled_query_name: the query's display name.
        :type squeduled_query_name: str
        :param schedule: string in BigQuery's expected format, such as
            'every mon,wed 09:00'
        :type schedule: str
        :param dest_table_name_template: an optional template to add to a table name,
            useful when using sharded tables. Pass an empty string to ignore,
            defaults to DestTableNameTemplate.no_template.value.
        :type dest_table_name_template: str, optional
        :param partitioning_field: a column name to partition the data. Use empty
            string to not partition the data, defaults to "".
        :type partitioning_field: str, optional
        """

        # List transfers. Store name and display name
        configs = self.bq_datatransfer_client.list_transfer_configs(parent=self._parent)
        config_names = {config.display_name: config.name for config in configs}  # type: ignore # noqa: E501

        # If display name matches one of the already existent display_names, deletes it
        # first by recovering the actual transfer name (which is different from the
        # display name)
        if squeduled_query_name in config_names.keys():
            logger.info(
                f"Deleting old version of scheduled query {squeduled_query_name}."
            )
            already_squeduled_query_name = config_names.get(squeduled_query_name)
            self.bq_datatransfer_client.delete_transfer_config(
                name=already_squeduled_query_name
            )

        # The recreates it (or just create the first time)
        transfer_config = bigquery_datatransfer.TransferConfig(
            destination_dataset_id=dest_dataset_id,
            display_name=squeduled_query_name,
            data_source_id="scheduled_query",
            params={
                "query": query_str,
                "destination_table_name_template": f"{dest_table_id}{dest_table_name_template}",  # noqa: E501
                "write_disposition": write_disposition,
                "partitioning_field": partitioning_field,
            },
            schedule=schedule,
        )

        transfer_config_request = self.bq_datatransfer_client.create_transfer_config(
            bigquery_datatransfer.CreateTransferConfigRequest(
                parent=self._parent,
                transfer_config=transfer_config,
                service_account_name=self._service_account,
            )
        )
        logger.info(f"Created scheduled query {transfer_config_request.name}")

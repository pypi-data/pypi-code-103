"""
Module used for BigQuery interactions.
"""
import logging
import re
from typing import Optional

from yawl.clients.bigquery_datatransfer import BigQueryDataTransfer, DestTableNameTemplate
from yawl.shared.constants import SERVICE_ACCOUNT_EMAIL
from yawl.workflows.base import WorkFlowStep

logger = logging.getLogger(__name__)


class BigQueryWorkflowStep(WorkFlowStep):
    """This class inherits from the abstract class WorkFlowStep and expands its behavior
    to operate with Google's BigQuery.
    """

    def __init__(
        self, sql: str, dest_table: str, squeduled_query_name: str, schedule: str
    ) -> None:
        """Initializes the class.

        :param sql: a string containing a SQL statement or the path to a .sql file
        :type sql: str
        :param dest_table: contains fully qualified table as "project.dataset.table"
        :type dest_table: str
        :param squeduled_query_name: the scheduled query display name
        :type squeduled_query_name: str
        :param schedule: a string in BigQuery's expected format, such as
            'every mon,wed 09:00'
        :type schedule: str
        """

        self.__sql = sql
        self.__project_id = dest_table.split(".")[0]
        self.__dataset = dest_table.split(".")[1]
        self.__dest_table = dest_table.split(".")[2]
        self.__squeduled_query_name = squeduled_query_name
        self.__schedule = schedule
        self.__upstream = None

        self.__client = BigQueryDataTransfer(
            project_id=self.__project_id,
            service_account=SERVICE_ACCOUNT_EMAIL,  # type: ignore
        )

    @property
    def dest_table(self) -> str:
        """Returns the destination table id.

        :return: The destination table id as string.
        :rtype: str
        """
        return self.__dest_table

    @property
    def upstream(self) -> Optional[str]:
        """Returns the upstream table id.

        :return: The upstream table id as string.
        :rtype: Optional[str]
        """

        return self.__upstream

    @upstream.setter
    def upstream(self, upstream: Optional[str]) -> None:
        self.__upstream = upstream  # type: ignore

    def get_sql_file(self) -> None:
        """Reads a sql file cleaning up extra spaces and new lines making it
        up a single, long, string.
        """

        with open(self.__sql, "r") as f:
            file = f.read()
        self.__sql = re.sub(r"[\s]{2,}|\n", " ", file)

    def execute(self) -> None:
        """Adds the scheduled query into BigQuery."""

        if self.__sql.endswith(".sql"):
            self.get_sql_file()

        self.__client.create_or_update_transfer_config(
            query_str=self.__sql,
            dest_dataset_id=self.__dataset,
            dest_table_id=self.dest_table,
            squeduled_query_name=self.__squeduled_query_name,
            schedule=self.__schedule,
            dest_table_name_template=DestTableNameTemplate.no_template.value,
            write_disposition="WRITE_TRUNCATE",
            partitioning_field="",
        )
        logger.info(
            (
                f"Executing step of upstream {self.upstream}"
                f" and destination {self.dest_table}"
            )
        )

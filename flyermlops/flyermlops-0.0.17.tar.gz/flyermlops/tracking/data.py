from data.connector import AuroraHelper, AthenaHelper, TeradataHelper, DataConnector
from base.tracking_base import TrackingBase
from tracking_utils import (
    get_or_create_table,
    log_data,
    check_for_existing_record,
)
from base.sql_base import (
    SqlPipelineTrackingRegistrySchema,
    SqlDataRegistrySchema,
)
from base.params import DataMetrics
import uuid
import datetime
import time


class DataTrackingObject(TrackingBase):
    """Connect to aurora database to log data metrics"""

    def __init__(
        self,
        host,
        user,
        password,
        port,
        database,
        project_name,
        pipeline_id=None,
        tracking_schema=None,
    ):
        super().__init__(
            host, user, password, port, database, project_name,
        )
        self.client = self.set_connection()
        self.aurora_client = self.set_tracking_connection()
        self.pipeline_id = pipeline_id
        self.tracking_schema = tracking_schema

    def set_tracking_connection(self, style):
        if style == "postgres":
            data_sess = DataConnector(style).client
            self.tracking_client = AuroraHelper(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.database,
            )
            return self.tracking_client

    def get_athena_client(self, **kwargs):
        self.athena_client = AthenaHelper(**kwargs)

    def get_teradata_client(self, **kwargs):
        self.teradata_client = TeradataHelper(**kwargs)

    def start_tracking(self):

        # Check if pipeline tracking table exists and create if not
        get_or_create_table(
            self.aurora_client, data_model=SqlPipelineTrackingRegistrySchema,
        )

        # Check if data tracking table exists and create if not
        get_or_create_table(
            self.aurora_client, data_model=SqlDataRegistrySchema,
        )

        # pull latest record from table
        record = check_for_existing_record(
            self.aurora_client,
            pipeline_sql_schema=SqlPipelineTrackingRegistrySchema,
            stage_sql_schema=SqlDataRegistrySchema,
            pipeline_id=self.pipeline_id,
        )

        # if record is None:

        # pipeline tracking start() - can be nullable
        # data tracking start() - pull pipeline tracking id()
        # data tracking end()
        # Training tracking start() - pull pipeline tracking id()
        # training tracking end()

        # all records can be traced to a given pipeline
        # data ids get unique ids
        #
        # pipeline tracking end()
        # has been created and get latest record if exists

    def log_table_metadata(
        self,
        engine=None,
        table_name: str = None,
        cols: dict = None,
        database_location: str = None,
        schema: str = None,
        registry_schema: str = None,
        git_link: str = None,
    ):

        date_ = datetime.datetime.now()
        metadata_dict = {
            "date": date_.strftime("%Y-%m-%d"),
            "timestamp": time.time(),
            "project": self.project_name,
            "table_name": table_name,
            "cols": cols,
            "location": database_location,
            "schema": schema,
            "git_link": git_link,
        }
        if engine is None:
            engine = self.aurora_client.set_connection("sqlalchemy")

        log_data(
            engine,
            registry_schema=registry_schema,
            data_model=SqlDataRegistrySchema,
            data=DataMetrics(**metadata_dict),
        )


# pip uninstall flyerops
# python setup.py sdist bdist_wheel
# python setup.py install

from abc import ABC, abstractmethod

from ..tracking_utils import get_or_create_table, set_tracking_id
from flyermlops.data.connector import DataConnector
from .sql_base import (
    SqlDataRegistrySchema,
    SqlFlightArtifactRegistrySchema,
    SqlFlightRegistrySchema,
    SqlModelRegistrySchema,
    SqlMetricRegistrySchema,
    SqlParamRegistrySchema,
    SqlDataMetricSchema,
)
import datetime
import time


class TrackingBase(ABC):
    def __init__(
        self,
        project_name: str,
        host: str = None,
        user: str = None,
        password: str = None,
        port: int = None,
        database: str = None,
        flight_tracking_id: str = None,
        tracking_id: str = None,
        code_link: str = None,
        tracking_uri: str = None,
        part_of_flight: bool = None,
        tracking_schema: str = None,
        tracker_type: str = None,
        s3_bucket: str = None,
        **kwargs
    ):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.database = database
        self.project_name = project_name
        self.flight_tracking_id = flight_tracking_id
        self.tracking_id = tracking_id
        self.code_link = code_link
        self.tracking_uri = tracking_uri
        self.part_of_flight = part_of_flight
        self.tracking_schema = tracking_schema
        self.tracker_type = tracker_type
        self.s3_bucket = s3_bucket

        self.registries = {}
        self.registries["flight"] = SqlFlightRegistrySchema

        if tracker_type == "data":
            self.registries["tracker"] = SqlDataRegistrySchema
            self.registries["metric"] = SqlDataMetricSchema

        elif tracker_type == "model":
            self.registries["tracker"] = SqlModelRegistrySchema
            self.registries["metric"] = SqlMetricRegistrySchema
            self.registries["param"] = SqlParamRegistrySchema

        elif tracker_type == "flight":
            self.registries["tracker"] = SqlFlightArtifactRegistrySchema

    @abstractmethod
    def set_tracking_connection(
        self, engine="postgres", flight_tracking_id=None, tracking_id=None,
    ):
        """ Establishes connection to postgres database and schema.
            Creates 

        Args:
            uri: Postgres connection uri.
            tracking_schema: Schema where tracking client writes data to.
            pipeline: Whether data tracking object is part of pipeline (True or False).
            If True, the pipeline registery is searched for an active pipeline associated with the project.
            If an active pipeline is not found, a new pipeline tracking id is created.
        """
        if engine == "postgres":
            data_sess = DataConnector(engine).client
            if self.tracking_uri is not None:
                self.tracking_engine = data_sess(uri=self.tracking_uri).set_connection(
                    connector="sqlalchemy"
                )
            else:
                self.tracking_engine = data_sess(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    port=self.port,
                    database=self.database,
                ).set_connection(connector="sqlalchemy")

        # Set postgres schema and metric schema
        for registry, schema in self.registries.items():

            # Set tracking schema
            schema.__table__.schema = self.tracking_schema

            # create table
            get_or_create_table(self.tracking_engine, schema)

        if flight_tracking_id is None:
            if self.part_of_flight:
                self.set_flight_tracking_id()

        if tracking_id is None:
            if "flight" not in self.registries["tracker"].__name__.lower():
                self.set_tracking_id()

    def set_tracking_id(self):
        self.tracking_id = set_tracking_id(
            project_name=self.project_name,
            engine=self.tracking_engine,
            registry_schema=self.registries["tracker"],
            flight_registry_schema=self.registries["flight"],
            flight_tracking_id=self.flight_tracking_id,
            code_link=self.code_link,
        )

    def set_flight_tracking_id(self):
        # if pipeline
        self.flight_tracking_id = set_tracking_id(
            project_name=self.project_name,
            engine=self.tracking_engine,
            registry_schema=self.registries["flight"],
        )


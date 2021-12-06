from sqlalchemy import create_engine, MetaData, Table, desc, select, insert, update
from sqlalchemy.orm import sessionmaker, Session
from flyermlops.tracking.base.params import (
    FlightParams,
    Metrics,
    Params,
    FlightArtifacts,
)
import uuid
from typing import Type, Dict, Any, Callable
from sqlalchemy.ext.declarative import declarative_base
import datetime
import time
from re import search
from .. import exceptions

base = declarative_base()


def set_registry_type(registry_schema):
    schema_name = registry_schema.__name__.lower()
    # Identify schema type
    for schema_type in ["data", "model", "flight", "param", "metric"]:
        if schema_type in schema_name:
            if schema_type == "flight":
                if "artifact" in schema_name:
                    registry_type = "artifact"
                else:
                    registry_type = schema_type
            else:
                registry_type = schema_type

    return registry_type


def select_sql_statement(registry_type, registry_schema):

    if registry_type == "data":
        return select(registry_schema.data_tracking_id, registry_schema.in_flight)

    elif registry_type == "model":
        return select(registry_schema.model_tracking_id, registry_schema.in_flight)

    elif registry_type == "flight":
        return select(registry_schema.flight_tracking_id, registry_schema.in_flight)


def clean_data(registry_type, data):

    if any(x in registry_type for x in ["data", "model", "flight"]):
        data = FlightParams(data).get_params()

    elif "params" in registry_type:
        data = Params(data).get_params()

    elif "metric" in registry_type:
        data = Metrics(data).get_params()

    elif "artifact" in registry_type:
        data = FlightArtifacts(data).get_params()

    return data


def update_registry_sql(
    registry_type, registry_schema, data_to_log, tracking_id,
):
    if registry_type == "data":
        sql = update(registry_schema).where(
            registry_schema.data_tracking_id == tracking_id
        )
    elif registry_type == "model":
        sql = update(registry_schema).where(
            registry_schema.model_tracking_id == tracking_id
        )
    elif registry_type == "flight":
        sql = update(registry_schema).where(
            registry_schema.flight_tracking_id == tracking_id
        )
    return sql.values(**data_to_log)


def get_or_create_table(engine, sql_schema):
    sql_schema.__table__.create(bind=engine, checkfirst=True)


def check_for_existing_record(
    project_name,
    engine,
    registry_schema,
    flight_registry_schema=None,
    flight_tracking_id=None,
):

    """Checks metadata table for an existing data or model tracking id.
    If a pipeline id is provided, the pipeline registry is checked for an existing tracking id for an active pipeline.

    Args:
        project_name: Name of project
        engine: Sqlaclhemy engine.
        registry_schema: Registry schema.
        flight_registry_schema: Pipeline registry schema.
        flight_tracking_id: Optional unique id associated with a pipeline run.

    Returns:
        Returns either "None" or a data or model tracking id.
    """
    registry_type = set_registry_type(registry_schema)

    if flight_tracking_id is not None:
        sql_statement = (
            select_sql_statement(registry_type, flight_registry_schema)
            .where(flight_registry_schema.flight_tracking_id == flight_tracking_id)
            .limit(1)
        )

    else:
        sql_statement = (
            select_sql_statement(registry_type, registry_schema)
            .where(registry_schema.in_flight == True)
            .where(registry_schema.project_name == project_name)
            .limit(1)
        )
    return engine.execute(sql_statement).scalar()


def check_if_id_active(engine, tracking_id, registry_schema):
    registry_type = set_registry_type(registry_schema)

    if registry_type == "data":
        sql_statement = (
            select(registry_schema.in_flight)
            .where(registry_schema.data_tracking_id == tracking_id)
            .where(registry_schema.in_flight == True)
        )

    elif registry_type == "model":
        sql_statement = (
            select(registry_schema.in_flight)
            .where(registry_schema.model_tracking_id == tracking_id)
            .where(registry_schema.in_flight == True)
        )

    elif registry_type == "flight":
        sql_statement = (
            select(registry_schema.in_flight)
            .where(registry_schema.flight_tracking_id == tracking_id)
            .where(registry_schema.in_flight == True)
        )
    return engine.execute(sql_statement).scalar()


def set_tracking_id(
    project_name: str,
    engine: Callable,
    registry_schema: Callable,
    flight_registry_schema: Callable = None,
    flight_tracking_id: str = None,
    code_link: str = None,
) -> str or None:

    """Creates a new tracking id if there is no active id available.
    registry_schema is used to determine which tracking registry to search and record id to.
    If a pipeline id is provided, the pipeline registry is checked for an existing tracking id.

    Args:
        project_name: Name of project.
        engine: Sqlaclhemy engine.
        registry_schema: Registry schema. This table schema is used to determine which registry is searched for an active id.
        pipeline_registry_schema: Pipeline registry table schema.
        pipeline_tracking_id: Optional unique id associated with a pipeline run
        code_link: Link to code repository

    Returns:
        Returns either "None" or a tracking id.
    """

    hex_id = uuid.uuid4().hex
    id_dict = {
        "data": {"data_tracking_id": hex_id},
        "model": {"model_tracking_id": hex_id},
        "flight": {"flight_tracking_id": hex_id},
    }

    # Identify schema type
    registry_type = set_registry_type(registry_schema)

    # check for existing record first
    if registry_type == "flight":
        existing_id = check_for_existing_record(
            project_name,
            engine,
            registry_schema,
            flight_registry_schema,
            flight_tracking_id,
        )
    else:
        existing_id = None

    if existing_id is None:
        new_id = id_dict[registry_type]

        # if flight id is not none add to flight registry
        if flight_tracking_id is not None:
            log_registry_values(
                engine, flight_registry_schema, new_id, tracking_id=flight_tracking_id,
            )

        # Add to registry
        values = {
            **new_id,
            **{
                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "timestamp": time.time(),
                "project_name": project_name,
                "git_link": code_link,
            },
        }

        if registry_type == "flight":
            values = {**values, **{"in_flight": 1}}
        log_registry_values(engine, registry_schema, values)

    return existing_id or new_id[f"{registry_type}_tracking_id"]


def log_registry_values(
    engine: Callable,
    registry_schema: Type[base],
    data: Dict[str, Any],
    tracking_id: str = None,
) -> None:

    """
    Logs values to registry table. Sql_schema is used to determine which registry to write to.
    Function defaults to insert statements unless a tracking id is provided, which then defaults to an update.
    """
    registry_type = set_registry_type(registry_schema)
    data_to_log = clean_data(registry_type, data)

    # id is only provided for updates
    if tracking_id is None:
        engine.execute(registry_schema.__table__.insert(data_to_log))

    else:
        sql_statement = update_registry_sql(
            registry_type, registry_schema, data_to_log, tracking_id,
        )
        result = engine.execute(sql_statement)
        result.close()


def log_metrics(
    engine: Callable, registry_schema: Type[base], data: Dict[str, Any],
) -> None:

    data_to_log = clean_data(registry_type="metric", data=data)
    engine.execute(registry_schema.__table__.insert(data_to_log))


def log_params(
    engine: Callable, registry_schema: Type[base], data: Dict[str, Any],
) -> None:

    data_to_log = clean_data(registry_type="params", data=data)
    engine.execute(registry_schema.__table__.insert(data_to_log))


# log params should always use model registry
def log_model_metadata(
    engine: Callable,
    data: Dict[str, Any],
    project_name: str,
    model_tracking_id: str,
    params_schema: Type[base],
    model_registry_schema: Type[base],
):

    # check if model tracking id is active
    active = check_if_id_active(engine, model_tracking_id, model_registry_schema)

    if active:
        # This funtion should always receive a model tracking id

        data = {
            **{
                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "timestamp": time.time(),
                "project_name": project_name,
                "model_tracking_id": model_tracking_id,
            },
            **data,
        }

        # Insert to table
        log_registry_values(
            engine, registry_schema=params_schema, data=data,
        )
    else:
        raise exceptions.NonActiveModelTrackingID


# log metrics should always use model registry
# def log_metrics(engine, data, registry_schema, stage):


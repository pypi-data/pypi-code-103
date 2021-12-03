import sys

import fire
from psycopg2 import ProgrammingError, connect
from psycopg2.extras import RealDictCursor
from requests import HTTPError

from fhir_cli import (
    DBT_SCHEMA,
    FHIR_COLUMN_NAME,
    POSTGRES_HOST,
    POSTGRES_PORT,
    PROJECT_DB,
    PROJECT_USER,
    PROJECT_USER_PASSWORD,
)
from fhir_cli.admin import Admin
from fhir_cli.dbt import Dbt
from fhir_cli.fhir_resource import FhirResource, FhirValidationError
from fhir_cli.utils.compact import dict_compact
from fhir_cli.utils.number_print import number_print


def get_resource_from_model(model: str) -> dict:
    """get_resource_from_model looks for a fhir model file and retrieves a Fhir resource"""
    conn = connect(
        host=POSTGRES_HOST,
        dbname=PROJECT_DB,
        port=POSTGRES_PORT,
        user=PROJECT_USER,
        password=PROJECT_USER_PASSWORD,
        cursor_factory=RealDictCursor,
    )
    with conn.cursor() as curs:
        curs.itersize = 1
        curs.execute(f"SET search_path TO {DBT_SCHEMA},{DBT_SCHEMA}_fhir")
        curs.execute(f"SELECT {FHIR_COLUMN_NAME} FROM {model}")
        curs.commit()
        row = curs.fetchone()

    resource = dict_compact(row[FHIR_COLUMN_NAME])
    return resource


class Cli:
    """FhirResource cli to manage your DbtOnFhir project"""

    def __init__(self):
        self.dbt = Dbt()
        self.admin = Admin()

    @staticmethod
    def validate(model: str):
        """The validate method extract a fhir model row and validates the Fhir resource
        against a Fhir server

        Args:
            model (str): should be a valid DBT Fhir model name such as `observation_heartrate`
        """
        try:
            resource = get_resource_from_model(model)
        except ProgrammingError as e:
            print(e, file=sys.stderr)
            return
        fhir = FhirResource(resource)
        number_print(repr(fhir))
        try:
            fhir.validate()
            print("\U0001F525 resource is valid")
        except (HTTPError, FhirValidationError) as e:
            print(e, file=sys.stderr)


def run():
    cli = Cli()
    fire.Fire(cli)


if __name__ == "__main__":
    run()

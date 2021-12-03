import os

from dotenv import load_dotenv
from jinja2 import Environment, PackageLoader, select_autoescape

load_dotenv()

# DBT
DBT_SCHEMA = os.environ["DBT_SCHEMA"]
DBT_INCREMENTAL_MODEL_TEMPLATE = "dbt_incremental_model.sql.j2"
DBT_INIT_DB_TEMPLATE = "dbt_init_db.sql.j2"
DBT_REF_PATTERN = r"(FROM\s+)(\w+\b)(.*)\b[ \t]*--[ \t]*dbt-ref\b.*"
DBT_MODELS_DIR = "models"
DBT_META_TABLE = "_meta"

# CDMs
CDM_LIST = ["fhir", "omop"]
FHIR_API_URL = os.environ.get("FHIR_API_URL")
FHIR_TAG = "fhir"
FHIR_COLUMN_NAME = "fhir"

# Project
PROJECT_NAME = os.environ["PROJECT_NAME"]
JINJA_ENV = Environment(loader=PackageLoader("fhir_cli"), autoescape=select_autoescape())
MAPPING_DIR = os.environ.get("MAPPING_DIR", "schemas")
PROJECT_DB = os.environ.get("PROJECT_DB")
PROJECT_USER = os.environ.get("PROJECT_USER")
PROJECT_USER_PASSWORD = os.environ.get("PROJECT_USER_PASSWORD")

# Postgres
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT"))
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_SERVER_NAME = os.environ.get("POSTGRES_SERVER_NAME", "postgres")

# Connect
CONNECT_URL = os.environ.get("CONNECT_URL")
CONNECT_CONFIG_TEMPLATE = "connect_config.json.j2"

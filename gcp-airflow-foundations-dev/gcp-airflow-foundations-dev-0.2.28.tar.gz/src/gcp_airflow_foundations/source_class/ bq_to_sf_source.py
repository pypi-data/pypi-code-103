from dataclasses import fields
from urllib.parse import urlparse
import logging

from airflow.models.dag import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator

from gcp_airflow_foundations.base_class.salesforce_ingestion_config import SalesforceIngestionConfig

from gcp_airflow_foundations.operators.api.operators.sf_to_gcs_query_operator import SalesforceToGcsQueryOperator
from gcp_airflow_foundations.base_class.data_source_table_config import DataSourceTablesConfig
from gcp_airflow_foundations.source_class.source import DagBuilder
from gcp_airflow_foundations.common.gcp.load_builder import load_builder


class SalesforcetoBQDagBuilder(DagBuilder):
    """
    Builds DAGs to load a CSV file from GCS to a BigQuery Table.
    """
    source_type = "SALESFORCE"

    def build_dags(self):
        data_source = self.config.source
        logging.info(f"Building DAG for GCS {data_source.name}")

        # GCP Parameters
        gcp_project = data_source.gcp_project
        gcs_bucket = data_source.extra_options["gcs_bucket"]
        gcs_object = data_source.extra_options["gcs_objects"]
        landing_dataset = data_source.landing_zone_options.landing_zone_dataset

        dags = []
        for table_config in self.config.tables:
            table_default_task_args = self.default_task_args_for_table(
                self.config, table_config
            )
            logging.info(f"table_default_task_args {table_default_task_args}")

            start_date = table_default_task_args["start_date"]

            with DAG(
                dag_id=f"sf_to_bq_{table_config.table_name}",
                description=f"Salesforce to BigQuery load for {table_config.table_name}",
                schedule_interval="@daily",
                default_args=table_default_task_args
            ) as dag:

                # BigQuery parameters
                destination_table = f"{gcp_project}:{landing_dataset}.{table_config.landing_zone_table_name_override}"

                # Salesforce parameters
                object_name = table_config.table_name
                ingest_all_columns = table_config.extra_options.get("ingest_all_columns")
                fields_to_omit = table_config.extra_options.get("fields_to_omit")
                field_names = table_config.extra_options.get("field_names")
                    



                gcs_upload_task >> load_to_bq_landing >> taskgroups

                logging.info(f"Created dag for {table_config}, {dag}")

                dags.append(dag)

        return dags

    def validate_extra_options(self):
        pass
    
def gcs_to_sf():

    # get files matching name from GCS

    # download them all

    #
    
    # connect to SF
    sf = Salesforce(username=username, password=password, security_token=security_token)

    for i in range(num_files):
        # read each csv into several pandas DFs in chunk
        dfs = pd.read_csv(f"test{i}.csv", chunksize=chunksize, low_memory=False)
        for df in dfs:
            # convert to json format for upload
            x = df.to_json(orient='records')
            rows = json.loads(x)
            # Specific adjustments as per Rami
            for row in rows:
                row["Company"] = "X"
                row["Status"] = "Open"
                row["LastName"] = "Unknown"
            logging.info("got rows")
            # do a bulk upsert
            sf.bulk.Lead.upsert(rows, 'mad_uuid__c', batch_size=5000)
            logging.info("uploaded chunk to sf")
    

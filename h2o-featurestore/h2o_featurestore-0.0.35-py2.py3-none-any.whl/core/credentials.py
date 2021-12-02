import os
from urllib.parse import urlparse

from . import CoreService_pb2 as pb


class CredentialsHelper:
    @staticmethod
    def set_credentials(request, raw_data_location):
        source = getattr(raw_data_location, raw_data_location.WhichOneof("source"))
        if isinstance(source, pb.CSVFileSpec):
            url_path = raw_data_location.csv.path
            CredentialsHelper.get_credentials_based_on_cloud(request, url_path)
        elif isinstance(source, pb.CSVFolderSpec):
            url_path = raw_data_location.csv_folder.root_folder
            CredentialsHelper.get_credentials_based_on_cloud(request, url_path)
        elif isinstance(source, pb.JSONFolderSpec):
            url_path = raw_data_location.json_folder.root_folder
            CredentialsHelper.get_credentials_based_on_cloud(request, url_path)
        elif isinstance(source, pb.JSONFileSpec):
            url_path = raw_data_location.json.path
            CredentialsHelper.get_credentials_based_on_cloud(request, url_path)
        elif isinstance(source, pb.ParquetFileSpec):
            url_path = raw_data_location.parquet.path
            CredentialsHelper.get_credentials_based_on_cloud(request, url_path)
        elif isinstance(source, pb.ParquetFolderSpec):
            url_path = raw_data_location.parquet_folder.root_folder
            CredentialsHelper.get_credentials_based_on_cloud(request, url_path)
        elif isinstance(source, pb.DeltaTableSpec):
            url_path = raw_data_location.delta_table.path
            CredentialsHelper.get_credentials_based_on_cloud(request, url_path)
        elif isinstance(source, pb.SnowflakeTableSpec):
            CredentialsHelper.set_snowflake_credentials(request)
        elif isinstance(source, pb.JDBCTableSpec):
            CredentialsHelper.set_jdbc_credentials(request, source.connection_url)
        elif isinstance(source, pb.DriverlessAIMOJOSpec):
            CredentialsHelper.set_driverless_ai_license(request)
        elif isinstance(source, pb.SparkPipelineSpec):
            pass
        elif isinstance(source, pb.JoinedFeatureSetsSpec):
            pass
        elif isinstance(source, pb.TempParquetFileSpec):
            pass
        else:
            raise Exception("Unsupported external data spec!")

    @staticmethod
    def get_credentials_based_on_cloud(request, url_path):
        if url_path.lower().startswith("s3"):
            CredentialsHelper.set_aws_credentials(request)
        elif url_path.lower().startswith("wasb") or url_path.lower().startswith("abfs"):
            CredentialsHelper.set_azure_credentials(request, url_path)
        else:
            raise Exception("Unsupported external data spec!")

    @staticmethod
    def set_azure_credentials(request, url_path):
        account_name = os.getenv("AZURE_ACCOUNT_NAME")
        account_key = os.getenv("AZURE_ACCOUNT_KEY")
        sas_token = os.getenv("AZURE_SAS_TOKEN")

        sp_client = os.getenv("AZURE_SP_CLIENT_ID")
        sp_tenant = os.getenv("AZURE_SP_TENANT_ID")
        sp_secret = os.getenv("AZURE_SP_SECRET")

        if account_name is None:
            raise Exception(
                "Azure account name must be defined for registering and obtaining data stored in "
                "Azure Blob storage! "
            )

        request.cred.azure.account_name = account_name

        if account_key:
            request.cred.azure.account_key = account_key
        elif sas_token:
            sas_container = urlparse(url_path).netloc.split("@")[0]
            request.cred.azure.sas_container = sas_container
            request.cred.azure.sas_token = sas_token
        elif sp_client and sp_tenant and sp_secret:
            sas_container = urlparse(url_path).netloc.split("@")[0]
            request.cred.azure.sas_container = sas_container
            request.cred.azure.sp_client_id = sp_client
            request.cred.azure.sp_tenant_id = sp_tenant
            request.cred.azure.sp_secret = sp_secret
        else:
            raise Exception(
                "Either Azure SAS token or Azure account key or Service Credentials must be "
                "specified for registering and "
                " obtaining data stored in Azure storage!"
            )

    @staticmethod
    def set_aws_credentials(request):
        request.cred.aws.access_token = CredentialsHelper.get_aws_access_token()
        request.cred.aws.secret_token = CredentialsHelper.get_aws_secret_token()
        request.cred.aws.region = CredentialsHelper.get_aws_region()

    @staticmethod
    def set_snowflake_credentials(request):
        request.cred.snowflake.user = CredentialsHelper.get_snowflake_user()
        request.cred.snowflake.password = CredentialsHelper.get_snowflake_password()

    @staticmethod
    def set_jdbc_credentials(request, connection_url):
        database_type = connection_url.split(":")[1]
        if database_type == "teradata":
            username = CredentialsHelper.get_jdbc_teradata_user()
            password = CredentialsHelper.get_jdbc_teradata_password()
        else:
            username = CredentialsHelper.get_jdbc_postgres_user()
            password = CredentialsHelper.get_jdbc_postgres_password()
        request.cred.jdbc_database.user = username
        request.cred.jdbc_database.password = password

    @staticmethod
    def set_driverless_ai_license(request):
        request.cred.driverless_ai_license = CredentialsHelper.get_dai_license()

    @staticmethod
    def get_aws_access_token():
        access_key = os.getenv("AWS_ACCESS_KEY")
        if access_key is None:
            raise Exception(
                "AWS access key must be defined for registering features and obtaining data "
                "stored in S3! "
            )
        return access_key

    @staticmethod
    def get_aws_secret_token():
        secret_key = os.getenv("AWS_SECRET_KEY")
        if secret_key is None:
            raise Exception(
                "AWS secret key must be defined for registering features and obtaining data "
                "stored in S3! "
            )
        return secret_key

    @staticmethod
    def get_aws_region():
        region = os.getenv("AWS_REGION")
        if region is None:
            raise Exception(
                "AWS region must be defined for registering features and obtaining data "
                "stored in S3! "
            )
        return region

    @staticmethod
    def get_snowflake_user():
        user = os.getenv("SNOWFLAKE_USER")
        if user is None:
            raise Exception(
                "Snowflake user name must be defined for registering features and obtaining "
                "data stored in Snowflake storage! "
            )
        return user

    @staticmethod
    def get_snowflake_password():
        password = os.getenv("SNOWFLAKE_PASSWORD")
        if password is None:
            raise Exception(
                "Snowflake password must be defined for registering features and obtaining "
                "data stored in Snowflake storage! "
            )
        return password

    @staticmethod
    def get_jdbc_postgres_user():
        password = os.getenv("JDBC_POSTGRES_USER")
        if password is None:
            raise Exception(
                "Username for accessing Postgres database must be defined for registering "
                "features from it! "
            )
        return password

    @staticmethod
    def get_jdbc_postgres_password():
        password = os.getenv("JDBC_POSTGRES_PASSWORD")
        if password is None:
            raise Exception(
                "Password for accessing Postgres database must be defined for registering "
                "features from it! "
            )
        return password

    @staticmethod
    def get_jdbc_teradata_user():
        password = os.getenv("JDBC_TERADATA_USER")
        if password is None:
            raise Exception(
                "Username for accessing Teradata database must be defined for registering "
                "features from it! "
            )
        return password

    @staticmethod
    def get_jdbc_teradata_password():
        password = os.getenv("JDBC_TERADATA_PASSWORD")
        if password is None:
            raise Exception(
                "Password for accessing Teradata database must be defined for registering features from it!"
            )
        return password

    @staticmethod
    def get_dai_license():
        license = os.getenv("DRIVERLESS_AI_LICENSE_KEY")
        if license is None:
            raise Exception(
                "License for Driverless AI is missing for registering features using DAI MOJO!"
            )
        return license

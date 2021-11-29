import snowflake.connector
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import serialization

class make_connection:
    # Read Private ssh key from .p8 file
    def connection_1(self,username,location,account_identifier,encryption_key,warehouse,database,schema):
        try:
            with open(location, "rb") as key:
                p_key= serialization.load_pem_private_key(
                    key.read(),
                    password=encryption_key.encode(),
                    backend=default_backend()
                )

            pkb = p_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption())

            # Connect to snowflake using the Provaiet key created above
            ctx = snowflake.connector.connect(
                user=username,
                account=account_identifier,
                private_key=pkb,
                warehouse=warehouse,
                database=database,
                schema=schema
                )
            return ctx
        except Exception as e:
            return e;
    def connection_2(self,username,account_identifier,password,warehouse,database,schema):
        try:
            ctx = snowflake.connector.connect(
                user=username,
                account=account_identifier,
                password=password,
                warehouse=warehouse,
                database=database,
                schema=schema
                )
            return ctx
        except Exception as e:
            return e;

class run_query:
    def run_select_query(self,con,sql_query):
        try:
            resultset = con.cursor().execute(sql_query)
            df = resultset.fetch_pandas_all()
            return df;
        except Exception as e:
            return e;
    
    def query(self,con,sql_query):
        try:
            resultset = con.cursor().execute(sql_query)
            df = resultset.fetchone()
            return df;
        except Exception as e:
            return e;


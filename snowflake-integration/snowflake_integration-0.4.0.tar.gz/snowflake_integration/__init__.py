import snowflake.connector
from snowflake.connector import ProgrammingError
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import serialization

class make_connection:
    def __init__(self):
        pass
    def connection_username_pass(self,username,pw,account_identifier,wh,db,sch):
        try:
            connection=snowflake.connector.connect(
            user=username,
            password=pw,
            account=account_identifier,
            warehouse=wh,
            database=db,
            sechema=sch
            )
            return connection
        except:
            return "Invalid Crediential"

    def private_key_encoder(self,private_key_file_name,pass_code):
        with open(private_key_file_name, "rb") as key:
            p_key= serialization.load_pem_private_key(
                key.read(),
                password=pass_code.encode(),
                backend=default_backend())

        pkb = p_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption())

        return pkb
    def connection_using_key_pair(self,username,account_identifier,private_key_file_name,pass_code,wh,db,sch):
        try:
            ctx = snowflake.connector.connect(
                                    user=username,
                                    account=account_identifier,
                                    private_key=self.private_key_encoder(private_key_file_name,pass_code),
                                    warehouse=wh,
                                    database=db,
                                    schema=sch )
            return ctx
        except:
            return "Invalid Crediential"
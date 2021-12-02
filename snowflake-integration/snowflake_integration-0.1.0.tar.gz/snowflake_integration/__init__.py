import snowflake.connector
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

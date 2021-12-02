class DB_Config(object):
    def __init__(self, server,database,user=None,password=None,trust=False,port=1433,driver="ODBC Driver 17 for SQL Server"):
        self.driver=driver
        self.server=server
        self.trust=trust
        self.user=user
        self.password=password
        self.database=database
        self.port=port

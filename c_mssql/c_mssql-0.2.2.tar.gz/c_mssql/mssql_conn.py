import pyodbc
from c_mssql.mssql_sql import odbc_type_to_db_type

class Mssql_Conn(object):
    def __init__(self,db_config,autocommit=False):
        self.db_config=db_config
        self.autocommit=autocommit
        self.conn=None
        self.cursor=None
    
    def open(self):
        # print('DRIVER={'+self.db_config.driver+'};SERVER='+self.db_config.server+','+str(self.db_config.port)+';DATABASE='+self.db_config.database+';UID='+self.db_config.user+';PWD='+ self.db_config.password+';')
        if self.db_config.trust:
            self.conn = pyodbc.connect('DRIVER={'+self.db_config.driver+'};SERVER='+self.db_config.server+','+str(self.db_config.port)+';DATABASE='+self.db_config.database+';Trusted_Connection=yes;',autocommit=self.autocommit)
        else:
            self.conn = pyodbc.connect('DRIVER={'+self.db_config.driver+'};SERVER='+self.db_config.server+','+str(self.db_config.port)+';DATABASE='+self.db_config.database+';UID='+self.db_config.user+';PWD='+ self.db_config.password+';',autocommit=self.autocommit)
        self.cursor = self.conn.cursor()

    def execute(self,sql_str):
        if bool(sql_str):
            try:
                self.cursor.execute(sql_str)
            except Exception as error_message:
                raise Exception(str(error_message)+"\nsql_str:"+sql_str)
            else:
                pass
        return self.cursor

    def column_dict(self):
        column_dict={}
        for column in self.cursor.description:
            column_dict[column[0]]=odbc_type_to_db_type(column[1])
        return column_dict

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()




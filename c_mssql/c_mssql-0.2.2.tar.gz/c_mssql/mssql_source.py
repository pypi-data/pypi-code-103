from c_mssql.mssql_conn import Mssql_Conn

class Mssql_Source(object):
    def __init__(self,db_config):
        self.db_config=db_config

    def get_column_dict(self,sql_str):
        conx=Mssql_Conn(self.db_config)
        conx.open()
        conx.execute(sql_str)
        column_dict=conx.column_dict()
        conx.close()
        return column_dict

    def get_datalist(self,sql_str,with_title=False):
        conx=Mssql_Conn(self.db_config)
        conx.open()
        cursor=conx.execute(sql_str)
        # 第一种
        # rows = cursor.fetchall()
        # for row in rows:
        #     print(row)
        # 第二种
        # for row in cursor:
        #     print(row)
        # # 第三种 内存性能较高
        # row=cursor.fetchone()
        # while row:
        #     print(row)
        #     row=cursor.fetchone()
        column_dict=conx.column_dict()
        if bool(cursor):
            data_list=[dict(zip(column_dict,row)) for row in cursor]
        else:
            data_list=[]
        conx.close()
        if with_title:
            return column_dict,data_list
        else:
            return data_list


    def get_rowdict(self,sql_str):
        conx=Mssql_Conn(self.db_config)
        conx.open()
        cursor=conx.execute(sql_str)
        row=cursor.fetchone()
        column_dict=conx.column_dict()
        conx.close()
        return dict(zip(column_dict,row))     

    def get_value(self,sql_str):
        conx=Mssql_Conn(self.db_config)
        conx.open()
        cursor=conx.execute(sql_str)
        result=cursor.fetchval()
        conx.close()
        return result
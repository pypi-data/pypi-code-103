import time, threading
from c_mssql.mssql_conn import Mssql_Conn
from c_mssql.mssql_source import Mssql_Source
from c_mssql.mssql_sql import get_insert_title_str,get_select_row_str
lock = threading.Lock()
taskcount=0




class Mssql_Dst(object):
    """description of class"""
    def __init__(self,db_config,run_task=2):
        self.db_config=db_config
        self.run_task=run_task
        
    #行数据处理
    def row_process(self,dict_row):
        return dict_row

    #带锁的数据插入
    def run_import(self,dst_db,titleStr,sql_datastr_list):
        global taskcount
        taskcount+=1
        lock.acquire()
        try:
            #标题和数据行
            sql_str_data="Union All\n".join(sql_datastr_list)
            conx=Mssql_Conn(dst_db,autocommit=True)
            conx.open()
            conx.execute(titleStr+"\n"+ sql_str_data)
            conx.close()
        finally:
            lock.release()
            taskcount-=1
            

    
    def import_into_dst(self,source_data,dst_table,dst_title=None,source_title=None,batch=1000):
        dst_db=Mssql_Source(self.db_config)
        #如果目标表字段未给定
        if dst_title is None:
            sql_str=f"""select c.column_id,c.name,ct.name,c.max_length,c.is_identity,c.is_nullable from sys.all_columns c with(nolock)
                        inner join sys.all_objects t with(nolock) on c.object_id=t.object_id
                        inner join sys.types ct with(nolock) on c.system_type_id=ct.system_type_id and c.user_type_id=ct.user_type_id
                        where t.name='{table_name}'
                        and c.is_identity =0
                        order by column_id"""
            dst_title_tmp=dst_db.get_column_dict(sql_str)
            dst_title={}
            if bool(source_data):
                for title in dst_title_tmp:
                    if title in source_data[0]:
                        dst_title[title]=dst_title_tmp[title]

        elif type(dst_title)==list:
            sql_str=f"""select {",".join(dst_title)} from {dst_table} with(nolock) where 1=2"""
            dst_title_temp=dst_db.get_column_dict(sql_str)
            dst_title_dict={}
            for title in dst_title:
                dst_title_dict[title]=dst_title_temp[title]
            dst_title=dst_title_dict

        if source_title is None:
            source_title=dst_title

        elif type(source_title)==list:
            source_title_dict={}
            for title in source_title:
                if title in dst_title:
                    source_title_dict[title]=dst_title[title]
                else:
                    source_title_dict[title]="string"
            source_title=source_title_dict

        #插入数据的Insert头部语句
        title_str=get_insert_title_str(dst_table,dst_title)
        #待插入的数据
        sql_str_data_list=[]
        #行计数 
        rowcount=0
        global taskcount
        for row in source_data:
            rowcount+=1
            dict_source_row={}
            #获取数据单行
            for title in source_title:
                dict_source_row[title]=row[title]
            #对每行数据进行处理
            dst_row_dict=self.row_process(dict_source_row)
            sql_str_data=get_select_row_str(dst_title, dst_row_dict)+"\n"
            sql_str_data_list.append(sql_str_data)
            if len(sql_str_data_list)==batch and len(str(sql_str_data_list))>8192:
                while taskcount>self.run_task:
                    time.sleep(0.01)
                t1 = threading.Thread(target=self.run_import, args=(self.db_config,title_str,sql_str_data_list,))
                t1.start()
                sql_str_data_list=[]


        if len(sql_str_data_list)>0:
            t1 = threading.Thread(target=self.run_import, args=(self.db_config,title_str,sql_str_data_list,))
            t1.start()
        #等待任务结束
        while taskcount>0:
            time.sleep(0.01)
            pass
        return rowcount




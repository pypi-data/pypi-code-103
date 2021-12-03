#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2
import requests
import json
import time
import base64
from datacanvas.aps import dc
from sqlalchemy import create_engine
import pandas as pd
import copy

# put your code here

tianti_check_api = 'http://10.18.5.113:8070/sky-ladder/sql-check-syntax'
tianti_evaluate_api = 'http://10.18.5.113:8070/sky-ladder/sql-evaluate'
tianti_extract_api = 'http://10.18.5.113:8070/sky-ladder/sql-extract-table-column'

log_table = 'public.db_operator_log'

request_from = 'APS'
db_name = 'zybdb'
db_host = '10.18.18.152'

db_port = '25308'
log_user = 'sys_user'
log_password_str = 'Gaussdba@Mpp'
pg_log_flag = 'true'

operator_name = dc.conf.global_params.user_name
operator_name = operator_name.replace('TP=', '')
project_id = dc.conf.global_params.project_id
tenant_id = dc.conf.global_params.tenant_id

check_params = {"dbType": "elk", "requestFrom": request_from, "scriptName": "APS.sql", 'operatorName': operator_name,
                'scriptName': project_id}
evaluate_params = {"userType": "11", "dbType": "elk", "requestFrom": request_from,
                   "dataSource": "aps_elk", 'operatorName': operator_name, 'scriptName': project_id}

log_sql = "INSERT INTO " + log_table + "(tenant_id,aps_user,db_user,db_name,schema_table,sql,result,date_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"


def jiemi_password(jiami_password):
    jiamihou_bytes = jiami_password[6:].encode(encoding='utf-8')
    jiemi_bytes = base64.decodebytes(jiamihou_bytes)
    jiemi_str = jiemi_bytes.decode(encoding='utf-8')
    password_str = jiemi_str
    return password_str


def insert_sql_to_pg(flag, tenant_id, username, schema_table, sql, result, now_time):
    try:
        if flag == "true":
            conn_log = psycopg2.connect(
                database=db_name,
                user=log_user,
                password=log_password_str,
                host=db_host,
                port=db_port
            )
            cur_log = conn_log.cursor()
            cur_log.execute(
                log_sql,
                (tenant_id, operator_name, username, db_name, schema_table, sql, result, now_time))
            conn_log.commit()
    except Exception as err:
        dc.logger.error("记录用户sql到pg数据库失败，%s" % err)
    finally:
        try:
            cur_log.close()
            conn_log.close()
        except Exception as error:
            dc.logger.error("数据库连接关闭异常，%s" % error)


def check_sql(sql):
    res = True
    result = ""
    try:
        check_params['sqlScript'] = sql
        evaluate_params['sqlScript'] = sql
        # 调用天梯检测sql接口
        response = requests.post(tianti_check_api, json.dumps(check_params))
        res2 = json.loads(response.text)
        if res2['code'] != 1001:
            res = False
            dc.logger.error("sql检测未通过, 请检查sql语句")
            return res
        # 调用天梯评分接口
        response2 = requests.post(tianti_evaluate_api, json.dumps(evaluate_params))
        res3 = json.loads(response2.text)
        if res3['code'] != 1001:
            dc.logger.error(res3['msg'])
            res = False
            return res
        res_data = res3['resData']
        score = res_data['score']
        type_reports = res_data['typeReports']
        if score < 60:
            dc.logger.error("sql得分: " + str(score) + ", 评分不合格")
            for report in type_reports:
                if report['score'] < 60:
                    report_modules = report['reportModules']
                    module = report_modules[0]
                    module_name = module['moduleName']
                    result = result.join(module_name) + ', '
                    dc.logger.error(result)
                    res = False
    except Exception as err:
        dc.logger.error("通过天梯系统校验sql失败，%s" % err)
        return False
    return res


def extract_table(sql):
    result = ''
    try:
        evaluate_params['sqlScript'] = sql
        # 调用天梯检测sql接口
        response = requests.post(tianti_extract_api, json.dumps(evaluate_params))
        res = json.loads(response.text)
        if res['code'] == 1001:
            res_data = res['resData']
            for index in range(len(res_data)):
                table = res_data[index]
                if index != len(res_data) - 1:
                    result = result + table['schema'] + '.' + table['table'] + ','
                else:
                    result = result + table['schema'] + '.' + table['table']
    except Exception as err:
        dc.logger.error("通过天梯系统抽取表名失败，%s" % err)
        return result
    return result


class PGUtils:
    def __init__(self, username, jiami_password):
        self.username = username
        self.password = jiemi_password(jiami_password)

    def get_engine(self):
        conn_str = "postgresql://{users}:{password}@{host}:{port}/{dbname}"
        conn_str = conn_str.format(users=self.username, password=self.password, host=db_host, port=db_port,
                                   dbname=db_name)
        engine = create_engine(conn_str)
        return engine

    def df_to_db(self, df, schema, table_name):
        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            schema_table = schema + '.' + table_name
            engine = self.get_engine()
            df.to_sql(table_name, con=engine, schema=schema, index=False, if_exists='append')
            insert_sql_to_pg("true", tenant_id, self.username, schema_table, "df_to_db", "success", now_time)
        except Exception as err:
            dc.logger.error("插入dataframe到表错误，%s" % err)

    def db_to_df(self, sql, schema, table_name):
        global df
        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            schema_table = schema + '.' + table_name
            conn = self.get_connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            data = pd.read_sql(sql, conn)
            df = copy.deepcopy(data)
            insert_sql_to_pg("true", tenant_id, self.username, schema_table, "db_to_df", "success", now_time)

        except Exception as err:
            dc.logger.error("读取dataframe错误，%s" % err)
        return df

    def get_connect(self):
        conn_connect = False
        try:
            conn_connect = psycopg2.connect(
                database=db_name,
                user=self.username,
                password=self.password,
                host=db_host,
                port=db_port
            )
        except Exception as err:
            dc.logger.error("连接数据库失败，%s" % err)
        return conn_connect

    def exec_query(self, sql):
        cur_query = ''
        conn_query = ''
        res = ""
        close_con = False
        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            conn_query = self.get_connect()
            close_con = True
            cur_query = conn_query.cursor()
            success = check_sql(sql)

            schema_table = extract_table(sql)
            # if schema_table == '':
            #     schema_table = 'null'
            if success:
                cur_query.execute(sql)
                res = cur_query.fetchall()
                insert_sql_to_pg(pg_log_flag, tenant_id, self.username, schema_table, sql, "success", now_time)
                # insert_sql_to_oracle(oracle_log_flag, sql, schema_table, now_time, 'success')
            else:
                insert_sql_to_pg(pg_log_flag, tenant_id, self.username, schema_table, sql, "fail", now_time)
                # insert_sql_to_oracle(oracle_log_flag, sql, schema_table, now_time, 'fail')
        except Exception as err:
            dc.logger.error("查询失败，%s" % err)
        finally:
            if close_con:
                try:
                    cur_query.close()
                    conn_query.close()
                except Exception as error:
                    dc.logger.error("数据库连接关闭异常，%s" % error)
        return res

    def exec_non_query(self, sql):
        flag = False
        close_con = False
        conn_non = ''
        cur_non = ''
        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            conn_non = self.get_connect()
            close_con = True
            cur_non = conn_non.cursor()

            schema_table = extract_table(sql)
            # if schema_table == ' ':
            #     schema_table = 'null'
            success = check_sql(sql)
            if success:
                cur_non.execute(sql)
                conn_non.commit()
                flag = True
                dc.logger.info("sql执行完毕")
                insert_sql_to_pg(pg_log_flag, tenant_id, self.username, schema_table, sql, "success", now_time)
                # insert_sql_to_oracle(oracle_log_flag, sql, schema_table, now_time, 'success')
            else:
                insert_sql_to_pg(pg_log_flag, tenant_id, self.username, schema_table, sql, "fail", now_time)
                # insert_sql_to_oracle(oracle_log_flag, sql, schema_table, now_time, 'fail')
        except Exception as err:
            dc.logger.error("执行失败，%s" % err)
            conn_non.rollback()
        finally:
            if close_con:
                try:
                    cur_non.close()
                    conn_non.close()
                except Exception as error:
                    dc.logger.error("数据库连接关闭异常，%s" % error)
        return flag


if __name__ == "__main__":
    dc.logger.info("APS is ready !")

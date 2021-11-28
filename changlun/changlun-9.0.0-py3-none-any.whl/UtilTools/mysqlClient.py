import traceback

import pandas as pd
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.types import NVARCHAR, Float, Integer, DATE, DATETIME,BIGINT
import numpy as np

mysql_host = '192.168.101.102'
mysql_user = 'root'
mysql_password = 'bdp@mysql'

dbDic = {}

def getCursor(db):
    connection = pymysql.connect(host=mysql_host,
                                 port=3306,
                                 user=mysql_user,
                                 password=mysql_password,
                                 db=db,
                                 charset='utf8mb4')
    return connection, connection.cursor()


def getEngine(db):
    if dbDic.__contains__(db):
        return dbDic.get(db)
    engine = create_engine("mysql+mysqlconnector://%s:%s@%s:%s/%s?charset=utf8mb4" % (
        mysql_user, mysql_password, mysql_host,'3306', db))
    dbDic[db] = engine
    return engine


def getDfFromSql(db, sql):
    return pd.read_sql(sql, getEngine(db))

def getMaxId(db,table):
    sql = 'select max(auto_id) from %s' % (table)
    df = getDfFromSql(db,sql)
    return df.iloc[0,0]

def getDfFromTable(db, table):
    return pd.read_sql("select * from " + table, getEngine(db))


def executeSql(db, sql):
    con, cursor = getCursor(db)
    try:
        cursor.execute(sql)
        con.commit()
    except:
        con.rollback()
        traceback.print_exc()
    finally:
        cursor.close()
        con.close()


def dropTable(db, tableName):
    executeSql(db, "drop table if exists %s" % tableName)


def mapping_df_types(df):
    dtypeDict = {}
    for i, j in zip(df.columns, df.dtypes):
        if "object" in str(j):
            if i in ['stock_id', 'code']:
                dtypeDict.update({i: NVARCHAR(length=12)})
            elif i in ['date']:
                dtypeDict.update({i: NVARCHAR(length=12)})
            elif 'date' in i:
                dtypeDict.update({i: NVARCHAR(length=12)})
            else:
                dtypeDict.update({i: NVARCHAR(length=255)})
        if "float" in str(j):
            dtypeDict.update({i: Float(precision=2, asdecimal=True)})
        if "int" in str(j):
            dtypeDict.update({i: BIGINT})
    dtypeDict['stock_id'] = NVARCHAR(length=12)
    dtypeDict['code'] = NVARCHAR(length=12)
    dtypeDict['date'] = DATETIME
    dtypeDict['trade_date'] = DATE
    dtypeDict['ds'] = NVARCHAR(length=12)
    return dtypeDict


def saveDf(df, db, tableName, isAppend=True, index=None):
    engine = getEngine(db)
    assert isinstance(df, pd.DataFrame)
    df = df.replace([np.inf, -np.inf], np.NaN)
    df = df.fillna(np.NaN)
    saveIndex = True
    if index is None:
        saveIndex = False
    else:
        # df.reset_index(inplace=True)
        df = df.set_index(index)
        # df.drop(columns='index')
    mode = 'append' if isAppend else 'replace'
    df.to_sql(tableName, engine, if_exists=mode, dtype=mapping_df_types(df), index=saveIndex, index_label=index,chunksize=1000)

def getTablesWithAutoIncrement(db):
    sql = "SELECT table_name from information_schema.TABLES where table_schema = '%s' and auto_increment is null" % (db)
    df = getDfFromSql(db,sql)
    if df is None or df.empty:
        print('all table has increment')
        return []
    tables = df['TABLE_NAME'].tolist()
    return tables

def getTables(db):
    sql = "SELECT table_name from information_schema.TABLES where table_schema = '%s' and auto_increment is not null" % (db)
    df = getDfFromSql(db,sql)
    if df is None or df.empty:
        print('all table has increment')
        return []
    tables = df['TABLE_NAME'].tolist()
    return tables

def addAutoIncrementToDb(db):
    tables = getTablesWithAutoIncrement(db)
    step = 1
    for table in tables:
        print('add auto_id to %s : %d / %d' % (table,step, len(tables)) )
        sql = 'alter table %s add auto_id int not null primary key auto_increment first' % (table)
        executeSql(db,sql)
        step += 1

def quote(x):
    return "'" + x + "'" if isinstance(x, str) else str(x)


def insertIntoMysql(database, table, columns, values):
    if isinstance(columns, str):
        columns, values = [columns], [values]
    columns = ", ".join(columns)
    values = ", ".join([quote(value) for value in values])
    sql = "insert into %s (%s) values (%s)" % (table, columns, values)
    executeSql(database, sql)


def updateRowMysql(database, table, columns, values, primaryCol=None, primaryValue=None):
    setClause = []
    for col, val in zip(columns, values):
        if val is not None:
            setClause.append("%s = %s" % (col, quote(val)))
    sql = "update %s set " % table
    sql = sql + ", ".join(setClause)
    if primaryCol is not None and primaryValue is not None:
        if isinstance(primaryCol, str):
            sql = sql + " where %s = %s" % (primaryCol, quote(primaryValue))
        elif isinstance(primaryCol, list):
            con = []
            for col, val in zip(primaryCol, primaryValue):
                con.append("%s = %s" % (col, quote(val)))
            sql = sql + " where " + " and ".join(con)
    executeSql(database, sql)

if __name__ == '__main__':
    addAutoIncrementToDb('ods')

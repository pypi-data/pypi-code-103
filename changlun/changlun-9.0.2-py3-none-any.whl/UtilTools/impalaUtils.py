from impala.dbapi import connect
from impala.util import as_pandas


def getDfFromSql(db,sql):
    conn = connect(host="node1", port=21050, database=db)
    cursor = conn.cursor()
    cursor.execute(sql)
    df = as_pandas(cursor)
    print(df)
    cursor.close()
    conn.close()
    return df

def refreshTable(db,table):
    sql = 'refresh %s.%s' % (db,table)
    conn = connect(host="node1", port=21050, database=db)
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.close()
    conn.close()
import pymysql


def generate_table(database, table, generate_sql, table_comment, sql_ip, sql_user, sql_pass):
    db = pymysql.connect(sql_ip, sql_user, sql_pass, database)

    cursor = db.cursor()

    sql = 'create table `' + table + '` ' + generate_sql + ' comment=\'' + table_comment + '\''
    cursor.execute(sql)
    db.close()


def build_field_sql(field_names):
    field_str = ''
    for column in field_names:
        field_str = field_str + column + ','
    return field_str[:-1]


def build_end_sql(uq_field_names, field_names):
    uq_field_str = ''
    for uq_field_name in uq_field_names:
        uq_field_str = uq_field_str + uq_field_name + ','

    end_sql = ' on conflict (' + (uq_field_str[:-1]) + ') do update set '
    for column in field_names:
        end_sql = end_sql + (column + '=' + 'excluded.' + column) + ','
    return end_sql[:-1]


def batch_insert(table_name, field_names, uq_field_names, list_data):
    sql_head = 'INSERT INTO ' + table_name + ' (' + build_field_sql(field_names) + ') VALUES '
    sql_items = ''
    for row in list_data:
        sql_items = sql_items + '( '
        for column in field_names:
            val = row[column]
            if isinstance(val, str):
                val = "'" + val + "'"
            else:
                val = str(val)
            sql_items = sql_items + val + ','
        sql_items = sql_items[:-1] + '),'

    sql_items = sql_items[:-1]
    sql_end = build_end_sql(uq_field_names, field_names)
    sql = sql_head + sql_items + sql_end
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute(sql, None)

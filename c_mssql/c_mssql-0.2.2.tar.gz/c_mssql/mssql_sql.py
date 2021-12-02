import binascii
from c_sql import Sql_Query
import datetime,decimal,uuid


def odbc_type_to_db_type(odbc_type):
    dict_db_type={str:"string"}
    dict_db_type[bytes]="binary"
    dict_db_type[bytearray]="binary"
    dict_db_type[datetime.date]="date"
    dict_db_type[datetime.time]="binary"
    dict_db_type[datetime.datetime]="datetime"
    dict_db_type[int]="int"
    dict_db_type[float]="float"
    dict_db_type[decimal.Decimal]="numeric"
    dict_db_type[uuid.UUID]="UUID"
    dict_db_type["expression"]="expression"
    if odbc_type in dict_db_type:
        db_type=dict_db_type[odbc_type]
    else:
        db_type="string"
    return db_type

def get_colums_value_str( column_value, column_type):
    if str(column_value).upper() == "NULL" or column_value is None:
        column_value = f"Null"
    elif column_type in ("string", "text", "datetime", "date", "time"):
        if column_type in ["string", "text"] and "'" in str(column_value):
            column_value = str(str(column_value).rstrip()
                                ).replace("'", "''")
        elif column_type == "datetime" and len(str(column_value)) > 23:
            column_value = f"""{str(column_value)[0:23]}"""
        column_value = f"""'{column_value}'"""
    elif column_type in ("binary", "bolean", "float", "int", "expression"):
        if column_type == "binary":
            column_value = f"{binary_to_str(column_value)}"
        elif column_type == "bolean":
            if column_value == False or str(column_value).upper() == 'FALSE':
                column_value = "0"
            elif column_type == True or str(column_value).upper() == "TRUE":
                column_value = "1"
        else:
            column_value = str(column_value)
    return column_value




def get_select_colum_str( column_name, column_value, column_type,is_expression=True, with_col_name=False):
    value_str = get_colums_value_str(column_value, column_type)
    if with_col_name:
        column_str = f"""{value_str} AS [{column_name}]"""
    else:
        column_str = value_str
    return column_str

def get_update_colum_str( column_name, column_value, column_type):
    value_str = get_colums_value_str(column_value, column_type)
    column_str = f"""[{column_name}]={value_str}"""
    return column_str

def get_condition_colum_str( column_name, column_value, column_type):
    value_str = get_colums_value_str(column_value, column_type)
    if value_str == "Null":
        column_str = f"""[{column_name}] is {value_str}"""
    else:
        column_str = f"""[{column_name}]={value_str}"""
    return column_str

# Condition的条件,用与1：判断是否存在，2：更新时的Where
def get_condition_str( title_dict, row_dict, key_list):
    condition_str_list = []
    for column_name in key_list:
        # 获取该列的值类型
        column_type = title_dict[column_name]
        # 获取Value
        column_value = row_dict[column_name]
        column_str = get_condition_colum_str(
            column_name, column_value, column_type)
        condition_str_list.append(column_str)
    # 返回Where语句的条件
    return ' and '.join(condition_str_list)

# 获取需要更新的列，排除主键
def get_update_str( title_dict, row_dict, key_list):
    update_str_list = []
    for column_name in row_dict:
        # 主键列不需要更新
        if column_name not in key_list and column_name in title_dict:
            # 获取该列的值类型
            column_type = title_dict[column_name]
            # 获取Value
            column_value = row_dict[column_name]
            column_str = get_update_colum_str(
                column_name, column_value, column_type)
            update_str_list.append(column_str)
    if len(update_str_list) > 0:
        columStr = ','.join(update_str_list)
    else:
        columStr = ""
    return columStr

# 更新数据
def get_update_sql( table_name, title_dict, row_dict, key_list):
    condition_str = get_condition_str(title_dict, row_dict, key_list)
    update_str = get_update_str(title_dict, row_dict, key_list)
    if update_str == "":
        update_sql = ""
    else:
        update_sql = f"""update t set {update_str} from {table_name} t with(nolock) 
    where {condition_str}
    """
    return update_sql

def get_insert_title_str( table_name, dict_title):
    title_list = []
    for title in dict_title:
        title_list.append(f"[{title}]")
    insert_title_str = f"""Insert Into {table_name} ({','.join(title_list)})"""
    return insert_title_str

# 从字典中生成数据行
def get_select_row_str( title_dict, row_dict,expression_list=[]):
    list_column = []
    for column_name in title_dict:
        if column_name in row_dict:
            column_value = row_dict[column_name]
            column_type = title_dict[column_name]
            coumn_str = get_select_colum_str(
                column_name, column_value, column_type)
            list_column.append(str(coumn_str))
    select_str = "Select "+",".join(list_column)
    return select_str

# 将数据字典中的行，拼接入sql语句中
def get_select_data_str( data_sql, title_dict, row_dict):
    select_data_str = ""
    select_row_str = get_select_row_str(title_dict, row_dict)
    select_data_str += f"{select_row_str}\n" if data_sql == "" else f"""Union All\n" {select_row_str}"""
    return data_sql

def binary_to_str(binary):
    if binary is not None and binary != 0:
        binarystr = str('0x'.encode('ascii') + binascii.hexlify(binary))
        binarystr = binarystr[2:len(binarystr)-1]
    else:
        binarystr = "0"
    return binarystr
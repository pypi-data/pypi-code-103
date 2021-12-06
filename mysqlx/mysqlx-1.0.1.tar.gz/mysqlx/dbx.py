import os
import re
from mysqlx import db
from jinja2 import Template
from mysqlx.model import SqlModel
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

_SQL_CONTAINER = dict()


def init_db(user, password, database, host='127.0.0.1', port=3306, use_unicode=True, mapper_path='mapper', default_dynamic=False, **kw):
    _load_sql(mapper_path, default_dynamic)
    db.init_db(user, password, database, host, port, use_unicode, **kw)


def insert(table, **kw):
    return db.insert(table, **kw)


def execute(sql_id, *args):
    sql = get_sql(sql_id)
    return db.execute(sql, *args)


def batch_execute(sql_id, args: list):
    sql = get_sql(sql_id)
    return db.batch_execute(sql, args)


def get(sql_id, *args):
    sql = get_sql(sql_id)
    return db.get(sql, *args)


def select_one(sql_id, *args):
    sql = get_sql(sql_id)
    return db.select_one(sql, *args)


def select(sql_id, *args):
    sql = get_sql(sql_id)
    return db.select(sql, *args)


def named_execute(sql_id, **kwargs):
    sql = get_named_sql(sql_id, **kwargs)
    return db.named_execute(sql, **kwargs)


def named_get(sql_id, **kwargs):
    sql = get_named_sql(sql_id, **kwargs)
    return db.named_get(sql, **kwargs)


def named_select_one(sql_id, **kwargs):
    sql = get_named_sql(sql_id, **kwargs)
    return db.named_select_one(sql, **kwargs)


def named_select(sql_id, **kwargs):
    sql = get_named_sql(sql_id, **kwargs)
    return db.named_select(sql, **kwargs)


def get_connection():
    return db.get_connection()


def _get_path(path):
    if path.startswith("../"):
        rpath = ''.join(re.findall("../", path))
        os.chdir(rpath)
        path = path[len(rpath):]
    elif path.startswith("./"):
        path = path[2:]
    return os.path.join(os.getcwd(), path)


def _load_sql(path, default_dynamic):
    if not os.path.isabs(path):
        path = _get_path(path)

    for f in os.listdir(path):
        file = os.path.join(path, f)
        if os.path.isfile(file) and f.endswith(".xml"):
            _read_mapper(file, default_dynamic)
        elif os.path.isdir(file):
            _load_sql(file, default_dynamic)


def _read_mapper(file, default_dynamic):
    global _SQL_CONTAINER
    tree = ET.parse(file)
    root = tree.getroot()
    namespace = root.attrib.get('namespace', '')
    for child in root:
        key = namespace + "." + child.attrib.get('id')
        dynamic = child.attrib.get('dynamic')
        if (dynamic and dynamic.lower() == 'true') or default_dynamic:
            _SQL_CONTAINER[key] = SqlModel(sql=Template(child.text), dynamic=True)
        else:
            _SQL_CONTAINER[key] = SqlModel(sql=child.text)


def get_sql(sql_id):
    sql_model = _get_sql_model(sql_id)
    return sql_model.sql


def get_named_sql(sql_id, **kwargs):
    sql_model = _get_sql_model(sql_id)
    return sql_model.sql.render(**kwargs) if sql_model.dynamic else sql_model.sql


def _get_sql_model(sql_id):
    global _SQL_CONTAINER
    sql_model = _SQL_CONTAINER.get(sql_id)
    if sql_model:
        return sql_model
    else:
        raise KeyError(f"invalid sql id: {sql_id}.")


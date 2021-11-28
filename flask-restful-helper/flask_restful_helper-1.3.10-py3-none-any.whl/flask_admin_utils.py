import os
import random
import shutil
import sqlite3
import string
from getpass import getpass
from pathlib import Path
from string import Template

import pymysql
import yaml

from flask_restful_helper.restful_helper.utils import get_uuid


def build_start_project_prompt():
    allow_dbs = ['mysql', 'sqlite']
    db_host = ''
    db_username = ''
    db_password = ''
    db_port = ''
    db_database = ''
    while True:
        db_type = input('DB TYPE:  mysql | sqlite ：')

        if db_type not in allow_dbs:
            continue
        if db_type == 'sqlite':
            break
        else:
            db_host = input("MYSQL IP：")
            db_port = input("MYSQL PORT：")
            db_username = input("MYSQL USERNAME：")
            db_password = input("MYSQL PASSWORD：")
            db_database = input("MYSQL DATABASE：")
            break

    prompt = {'db_type': db_type,
              'db_host': db_host,
              'db_port': db_port,
              'db_username': db_username,
              'db_password': db_password,
              'db_database': db_database}
    return prompt


def build_create_superuser_prompt():
    username = input('Username: ')
    while True:
        password1 = getpass('Password1: ')
        password2 = getpass('Password2: ')
        if password1 == password2:
            break
        else:
            print('密碼不一致')

    email = input('Email: ')

    prompt = {
        'username': username,
        'password': password1,
        'email': email
    }
    return prompt


def read_template(filename, **kwargs):
    """讀入template"""
    with open(filename, 'r', encoding='utf-8') as f:
        template = Template(f.read())
        return template.substitute(**kwargs)


def write2file(path, py_string):
    """寫入py"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(py_string)


def copy_config(project_base_dir, working_dir, prompt_args):
    working_dir.joinpath('config').mkdir(parents=True, exist_ok=True)
    yaml_string = read_template(project_base_dir.joinpath('config', 'dev.template'),
                                db_type=prompt_args.get('db_type'),
                                db_host=prompt_args.get('db_host'),
                                db_username=prompt_args.get('db_username'),
                                db_password=prompt_args.get('db_password'),
                                db_port=prompt_args.get('db_port'),
                                db_database=prompt_args.get('db_database'),
                                jwt_secret_key=generate_random_string(30))
    write2file(working_dir.joinpath('config', 'dev.yaml'), yaml_string)


def generate_random_string(length):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))


def copy_and_overwrite(src: Path, dst: Path, tree=False):
    if tree:
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)


def update_installed_apps_conf(app_name):
    installed_apps_conf_path = Path.cwd().joinpath('config', 'installed_apps.yaml')
    if installed_apps_conf_path.exists():
        with open(installed_apps_conf_path, 'r', encoding='utf-8') as f:
            installed_apps = yaml.safe_load(f.read())
    else:
        installed_apps = []
    installed_apps += [app_name]

    with open(installed_apps_conf_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(installed_apps, f)


def get_installed_apps_conf():
    installed_apps_conf_path = Path.cwd().joinpath('config', 'installed_apps.yaml')
    if installed_apps_conf_path.exists():
        with open(installed_apps_conf_path, 'r', encoding='utf-8') as f:
            installed_apps = yaml.safe_load(f.read())
    else:
        installed_apps = []
    return installed_apps


def load_config():
    with open(Path.cwd().joinpath('config', f'{os.getenv("CONFIG_TYPE", "dev")}.yaml')) as f:
        return yaml.safe_load(f.read())


def insert_superuser_to_database(data):
    config = load_config()
    if config['DB_TYPE'] == 'mysql':
        conn = pymysql.connect(host=str(config['DB_HOST']),
                               port=int(config['DB_PORT']),
                               user=str(config['DB_USERNAME']),
                               password=str(config['DB_PASSWORD']),
                               db=str(config['DB_DATABASE']),
                               )
        with conn:
            with conn.cursor() as cursor:
                sql = """
                         INSERT INTO system_user (id,username,password,email,date_added,is_superuser) 
                         VALUES (%s,%s,%s,%s,now(),1)
                      """
                cursor.execute(sql, (get_uuid(), data['username'], data['password'], data['email']))
            conn.commit()
    elif config.get('DB_TYPE') == 'sqlite':
        conn = sqlite3.connect(Path.cwd().joinpath('sqlite.db'))
        cursor = conn.cursor()
        sql = "INSERT INTO system_user (id,username,password,email,date_added,is_superuser,locale) VALUES (?,?,?,?,date(),1,'en_us')"
        cursor.execute(sql, (get_uuid(), data['username'], data['password'], data['email']))
        conn.commit()
        conn.close()
    print('創建完成')


def copy_app(app_name):
    package_dir = Path(__file__).parent
    shutil.copytree(package_dir.joinpath('app_base', app_name), Path.cwd().joinpath('apps', app_name))

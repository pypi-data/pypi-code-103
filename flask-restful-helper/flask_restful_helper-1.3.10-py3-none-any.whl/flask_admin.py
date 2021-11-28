import shutil
from pathlib import Path
import click

from flask_restful_helper.flask_admin_utils import read_template, write2file, \
    copy_config, copy_and_overwrite, update_installed_apps_conf, build_create_superuser_prompt, \
    get_installed_apps_conf, build_start_project_prompt, insert_superuser_to_database, copy_app


@click.group()
def cli():
    """
    快速專案建置工具.
    """
    pass


@cli.command()
@click.option('-f', '--force', 'force', help='強制重開專案', default=False)
def start_project(force):
    prompt_args = build_start_project_prompt()
    package_dir = Path(__file__).parent
    print(Path.cwd())
    if not force and Path.cwd().joinpath('main').exists():
        print('main 已經存在， 如果依然要執行初始化請加入參數 --force')
        return

    if force:
        shutil.rmtree(Path.cwd().joinpath('main'))
        shutil.rmtree(Path.cwd().joinpath('tests'))
        Path.cwd().joinpath('manage.py').unlink()

    copy_and_overwrite(package_dir.joinpath('project_base', 'main'), Path.cwd().joinpath('main'), tree=True)
    copy_and_overwrite(package_dir.joinpath('test_base', 'tests'), Path.cwd().joinpath('tests'), tree=True)
    Path.cwd().joinpath('tests', 'functions', 'db', 'sqls').mkdir(parents=True, exist_ok=True)
    shutil.copy(package_dir.joinpath('project_base', 'manage.py'), Path.cwd().joinpath('manage.py'))
    shutil.copy(package_dir.joinpath('project_base', 'wsgi.py'), Path.cwd().joinpath('wsgi.py'))

    copy_config(package_dir.joinpath('project_base'), Path.cwd(), prompt_args)
    print('執行開發伺服器 : python manage.py dev')


@cli.command()
@click.option('-a', '--app', type=click.Choice(['system', 'task', 'frontend','file']), required=False)
def start_app(app):
    if app in ['system', 'frontend','file']:
        copy_app(app)
        update_installed_apps_conf(app)
    elif app == 'task':
        copy_app(app)
        shutil.copy(Path(__file__).parent.joinpath('project_base', 'task.py'), Path.cwd().joinpath('task.py'))
        update_installed_apps_conf(app)
        print('請將任務程式碼寫入 task/schedules 下')
        print('排程執行器 : celery -A task.celery beat')
        print('啟用worker : celery -A task.celery worker -P gevant')
    else:
        start_new_app()
    print('app已建立，請進行遷移資料庫')





def start_new_app():
    package_dir = Path(__file__).parent
    while True:
        app_name = input('輸入 App 名稱：')
        if app_name[0].isnumeric():
            print('請勿以數字開頭')
            continue
        break

    Path.cwd().joinpath('apps', app_name).mkdir(parents=True, exist_ok=True)
    for category in ['api_view', 'logic', 'manager', 'model', 'schema', 'test']:
        print(f'creating {category}')
        py_string = read_template(package_dir.joinpath('app_base', 'clean', f'{category}s', f'{category}.template'),
                                  app_name=app_name)
        Path.cwd().joinpath('apps', app_name, f'{category}s').mkdir(exist_ok=True)
        write2file(Path.cwd().joinpath('apps', app_name, f'{category}s', f'{category}.py'), py_string)

    for category in ['router']:
        print(f'creating {category}')
        py_string = read_template(package_dir.joinpath('app_base', 'clean', f'{category}.template'), app_name=app_name)
        write2file(Path.cwd().joinpath('apps', app_name, f'{category}.py'), py_string)
    shutil.copy(package_dir.joinpath('app_base', 'clean', '__init__.py'),
                Path.cwd().joinpath('apps', app_name, '__init__.py'))
    update_installed_apps_conf(app_name)


@cli.command()
def create_superuser():
    from flask_bcrypt import Bcrypt
    installed_apps = get_installed_apps_conf()

    if 'system' not in installed_apps:
        print('請先啟用system app')

    prompt_args = build_create_superuser_prompt()
    bcrypt = Bcrypt()
    prompt_args['password'] = bcrypt.generate_password_hash(prompt_args.get('password'))

    insert_superuser_to_database(prompt_args)


if __name__ == '__main__':
    cli()

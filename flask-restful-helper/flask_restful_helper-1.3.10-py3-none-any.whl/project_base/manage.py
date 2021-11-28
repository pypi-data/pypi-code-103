"""
開發環境CLI
"""
import click
import os
import unittest
import inspect
import importlib
from main import create_app

app = create_app(os.getenv('config_type', 'dev'))


@click.group()
def cli():
    """
    預設CLI
    """


@cli.command()
def dev():
    """
    執行開發環境
    """

    app.run(port=5000)


@cli.command()
def test():
    from tests.metaclass import AvoidSameMethodNameMetaclass
    if app.config['TEST_EXECUTE_ALL_TEST']:
        # region 取得apps底下所有test class
        app_items = os.listdir('apps')
        app_test_classes = []
        for app_item in app_items:
            test_file_path = f'apps.{app_item}.tests.test'
            for name, cls in inspect.getmembers(importlib.import_module(test_file_path), inspect.isclass):
                # 為了在所有test function名稱後面加上module名以及class名（為了讓test function名稱不重複）
                # 因為一旦重複，只會執行先繼承的那個
                test_class_with_metaclass = AvoidSameMethodNameMetaclass(name, (object,), cls.__dict__)
                app_test_classes.append(test_class_with_metaclass)
        app_test_classes = tuple(app_test_classes)
        # endregion
        # region 取得roles底下所有class，並繼承所有test class
        role_classes = []
        for file in os.listdir(os.path.join('tests', 'roles')):
            if file.endswith(".py"):
                role_file_path = f'tests.roles.{file.split(".")[0]}'
                for name, cls in inspect.getmembers(importlib.import_module(role_file_path), inspect.isclass):
                    if cls.__module__ == role_file_path:
                        cls.__bases__ += app_test_classes
                        role_classes.append(cls)
        # endregion
        role_classes_to_run = role_classes
        loader = unittest.TestLoader()
        suites_list = []
        for role_class_to_run in role_classes_to_run:
            suite = loader.loadTestsFromTestCase(role_class_to_run)
            suites_list.append(suite)
        result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(suites_list))
    else:
        from tests.roles.superuser_test import SuperuserTests
        from apps.system.tests.test import User
        SuperuserTests.__bases__ += (User,)
        single_test = unittest.TestSuite()
        single_test.addTest(SuperuserTests('test_list_all_users_return_200_or_204'))
        result = unittest.TextTestRunner(verbosity=2).run(single_test)

    # 為了讓runner知道成功或失敗
    return exit(1) if result.errors else exit(0)


if __name__ == '__main__':
    cli()

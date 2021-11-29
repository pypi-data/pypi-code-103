import os.path
import sys

run_content = """
import argparse
import pytest
from qrunner import Browser
from qrunner import AndroidDriver


# 获取命令行输入的数据
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--serial_no', dest='serial_no',
                    type=str, default='', help='设备id')
parser.add_argument('-p', '--pkg_name', dest='pkg_name',
                    type=str, default='', help='应用包名')
parser.add_argument('-b', '--browser_name', dest='browser_name',
                    type=str, default='', help='浏览器类型: chrome、safari、firefox、ie、edge')
parser.add_argument('-c', '--case_name', dest='case_name',
                    type=str, default='', help='用例模块名、类名、方法名')
parser.add_argument('-r', '--rerun', dest='rerun',
                    type=str, default='0', help='重试次数')

# 将数据写入全局变量
args = parser.parse_args()
Browser.serial_no = args.serial_no
Browser.pkg_name = args.pkg_name
Browser.browser_name = args.browser_name
Browser.alert_config = []

# driver初始化
Browser.driver = AndroidDriver.get_instance(args.serial_no)

# 执行用例
case_path = 'tests'
pytest.main([case_path, '-sv', '-k', args.case_name, '--reruns', args.rerun,
             '--alluredir', 'allure-results', '--clean-alluredir', '--html=report.html', '--self-contained-html'])
"""

page_adr_content = """
from qrunner import AdrPage, AdrElement


class HomePage(AdrPage):
    my_entry = AdrElement(resourceId='id/bottom_view', index=3)
"""

case_android_content = """
import allure
import time
from qrunner import Browser
from pages.home_page import HomePage


@allure.feature('首页')
class TestHome:
    def setup_method(self):
        Browser.driver.app_start()
    
    def teardown_method(self):
        Browser.driver.app_stop()
    
    @allure.title('进入我的')
    def test_01(self):
        page = HomePage()
        page.my_entry.click()
        time.sleep(3)
"""

require_content = """qrunner
"""

ignore_content = "\n".join(
    ["allure-results/*", "__pycache__/*", "*.pyc", "report.html", ".idea/*"]
)


def init_scaffold_project(subparsers):
    parser = subparsers.add_parser(
        "create", help="Create a new project with template structure."
    )
    parser.add_argument(
        "project_name", type=str, nargs="?", help="Specify new project name."
    )
    return parser


def create_scaffold(project_name):
    """ create scaffold with specified project name.
    """

    def create_folder(path):
        os.makedirs(path)
        msg = f"created folder: {path}"
        print(msg)

    def create_file(path, file_content=""):
        with open(path, "w", encoding="utf-8") as f:
            f.write(file_content)
        msg = f"created file: {path}"
        print(msg)

    create_folder(project_name)
    create_folder(os.path.join(project_name, "tests"))
    create_folder(os.path.join(project_name, "pages"))
    create_file(
        os.path.join(project_name, "run.py"),
        run_content,
    )
    create_file(
        os.path.join(project_name, ".gitignore"),
        ignore_content,
    )
    create_file(
        os.path.join(project_name, "requirements.txt"),
        require_content,
    )

    create_file(
        os.path.join(project_name, "pages", "home_page.py"),
        page_adr_content,
    )
    create_file(
        os.path.join(project_name, "tests", "test_login.py"),
        case_android_content,
    )
    # show_tree(project_name)
    return 0


def main_scaffold_project(args):
    sys.exit(create_scaffold(args.project_name))


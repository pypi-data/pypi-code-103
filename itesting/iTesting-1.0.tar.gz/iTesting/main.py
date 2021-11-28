# main.py
import argparse
import codecs
import inspect
import json
import os
import shlex
import sys
import glob
import importlib.util
import yaml
from functools import wraps


class TestMark(object):
    def __init__(self, mark=None):
        self.mark = mark

    def __call__(self, func):
        @wraps(func)
        def wrapper():
            return func

        setattr(wrapper, "__test_case_mark__", self.mark)
        return wrapper


def parse_options(user_options=None):
    parser = argparse.ArgumentParser(prog='iTesting',
                                     usage='Demo Automation Framework, Search wechat account iTesting for more information')
    parser.add_argument("-env", default='dev', type=str, choices=['dev', 'qa', 'staging', 'prod'], help="Env parameter")
    parser.add_argument("-k", default=None, action="store", help="only run tests which match the given substring expression")
    parser.add_argument("-m", default=None, action="store", help="only run tests with same marks")

    if not user_options:
        args = sys.argv[1:]
    else:
        args = shlex.split(user_options)

    options, un_known = parser.parse_known_args(args)
    if options.env:
        print("\n想了解更多测试框架内容吗？请关注公众号iTesting")
        print('Currently the env are set to: %s' % options.env)

    if options.k:
        print("你设置了-k参数，将会运行所有包括'%s'的测试文件，测试类，测试函数" % options.k)

    if options.m:
        print("你设置了-m参数，将会运行所有标签为'%s'的测试类，测试函数" % options.m)

    return options


def find_modules_from_folder(folder):
    absolute_f = os.path.abspath(folder)
    md = glob.glob(os.path.join(absolute_f, "*.py"))
    return [(os.path.basename(f)[:-3], f) for f in md if os.path.isfile(f) and not f.endswith('__init__.py')]


def import_modules_dynamically(mod, file_path):
    spec = importlib.util.spec_from_file_location(mod, file_path)
    md = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(md)
    return md


def get_tests_and_data_folder_via_env(env):
    # 此方法入口函数不同，获取到的值就不同, 此为命令行执行入口
    test_root = os.path.join(os.getcwd(), 'iTesting' + os.sep + 'tests')
    test_data_root = os.path.join(os.getcwd(), 'iTesting' + os.sep + 'test_data' + os.sep + env)

    # # # 此方法入口函数不同，获取到的值就不同, 此为if __name__ == "__main__":执行
    # current_folder, current_file = os.path.split(os.path.realpath(__file__))
    # test_data_root = os.path.join(current_folder, 'test_data' + os.sep + env)
    # test_root = os.path.join(current_folder, 'tests')
    return test_root, test_data_root


def load_data_from_json_yaml(yaml_file):
    _is_yaml_file = yaml_file.endswith((".yml", ".yaml"))

    with codecs.open(yaml_file, 'r', 'utf-8') as f:
        # Load the data from YAML or JSON
        if _is_yaml_file:
            data = yaml.safe_load(f)
        else:
            data = json.load(f)

    return data


def run(test_folder, test_data_folder, args):
    module_pair_list = find_modules_from_folder(test_folder)
    for m in module_pair_list:
        mod = import_modules_dynamically(m[0], m[1])
        # 解析测试文件
        test_data_file = os.path.join(test_data_folder, mod.__name__ + '.yaml')
        test_data = load_data_from_json_yaml(test_data_file)
        if args.k:
            # 找出module名中含有-k参数值的测试module
            if args.k in mod.__name__:
                # test_data_file = os.path.join(test_data_folder, mod.__name__ + '.yaml')
                for cls_name, cls in inspect.getmembers(mod, inspect.isclass):
                    if cls_name.startswith('Test'):
                        for item in inspect.getmembers(cls, lambda fc: inspect.isfunction(fc)):
                            func_name, func = item
                            if func_name.startswith('test'):
                                if args.m:
                                    if getattr(func, "__test_case_mark__", None) == args.m:
                                        # 这里先不写具体怎么执行，单纯打印出待执行的测试用例名
                                        print("指定-k，也指定了-m。测试module {0}包含{1}，将会运行{0}下的所有带-m标签且值为{2}的用例".format(mod.__name__, args.k, args.m))
                                        print(mod.__name__ + '.' + cls_name + '.' + func_name)
                                        # print("\n想了解更多测试框架内容吗？请关注公众号iTesting")
                                else:
                                    # 这里先不写具体怎么执行，单纯打印出待执行的测试用例名
                                    print("指定-k，没有指定-m。测试module {0}包含{1}，将会运行{0}下的所有测试用例".format(mod.__name__, args.k))
                                    print(mod.__name__ + '.' + cls_name + '.' + func_name)
                                    # print("\n想了解更多测试框架内容吗？请关注公众号iTesting")

            else:
                # test_data_file = os.path.join(test_data_folder, mod.__name__ + '.yaml')
                for cls_name, cls in inspect.getmembers(mod, inspect.isclass):
                    if cls_name.startswith('Test'):
                        # 找出测试类名中含有-k参数值的测试类
                        if args.k in cls_name:
                            for item in inspect.getmembers(cls, lambda fc: inspect.isfunction(fc)):
                                func_name, func = item
                                if func_name.startswith('test'):
                                    if args.m:
                                        if getattr(func, "__test_case_mark__", None) == args.m:
                                            # 这里先不写具体怎么执行，单纯打印出待执行的测试用例名
                                            print("指定-k，也指定了-m。测试类 {0}包含{1}，将会运行{0}下的所有带-m标签且值为{2}的用例".format(
                                                cls_name, args.k, args.m))
                                            print(mod.__name__ + '.' + cls_name + '.' + func_name)
                                            # print("\n想了解更多测试框架内容吗？请关注公众号iTesting")
                                    else:
                                        # 这里先不写具体怎么执行，单纯打印出待执行的测试用例名
                                        print(
                                            "指定-k，没有指定-m。测试类 {0}包含{1}，将会运行{0}下的所有测试用例".format(cls_name, args.k))
                                        print(mod.__name__ + '.' + cls_name + '.' + func_name)
                                        # print("\n想了解更多测试框架内容吗？请关注公众号iTesting")
                        else:
                            for item in inspect.getmembers(cls, lambda fc: inspect.isfunction(fc)):
                                func_name, func = item
                                if func_name.startswith('test'):
                                    if args.k in func_name:
                                        if args.m:
                                            if getattr(func, "__test_case_mark__", None) == args.m:
                                                # 这里先不写具体怎么执行，单纯打印出待执行的测试用例名
                                                print("指定-k，也指定了-m。测试方法 {0}包含{1}，且带-m标签，运行此用例".format(
                                                    func_name, args.k))
                                                print(mod.__name__ + '.' + cls_name + '.' + func_name)
                                                # print("\n想了解更多测试框架内容吗？请关注公众号iTesting")
                                        else:
                                            # 这里先不写具体怎么执行，单纯打印出待执行的测试用例名
                                            print("指定-k，没有指定-m。测试方法 {0}包含{1}运行此用例".format(
                                                func_name, args.k))
                                            print(mod.__name__ + '.' + cls_name + '.' + func_name)
                                            # print("\n想了解更多测试框架内容吗？请关注公众号iTesting")
        else:
            # test_data_file = os.path.join(test_data_folder, mod.__name__ + '.yaml')
            for cls_name, cls in inspect.getmembers(mod, inspect.isclass):
                if cls_name.startswith('Test'):
                    for item in inspect.getmembers(cls, lambda fc: inspect.isfunction(fc)):
                        func_name, func = item
                        if func_name.startswith('test'):
                            if args.m:
                                if getattr(func, "__test_case_mark__", None) == args.m:
                                    # 这里先不写具体怎么执行，单纯打印出待执行的测试用例名
                                    print("没有指定-k，但是指定了-m，运行带-m标签的用例")
                                    print(mod.__name__ + '.' + cls_name + '.' + func_name)
                                    # print("\n想了解更多测试框架内容吗？请关注公众号iTesting")
                            else:
                                # 这里先不写具体怎么执行，单纯打印出待执行的测试用例名
                                print("没有指定-k，也没有指定-m，运行所有测试用例")
                                print(mod.__name__ + '.' + cls_name + '.' + func_name)
                                # print("\n想了解更多测试框架内容吗？请关注公众号iTesting")


def main(user_options=None):
    args = parse_options(user_options)
    test_root, test_data_root = get_tests_and_data_folder_via_env(args.env)

    run(test_root, test_data_root, args)


if __name__ == "__main__":
    main('-env dev -k login -m myMark')
    # pytest.main(["--alluredir", "./allure-results"])
    # os.system(r"allure generate --clean allure-results -o allure-report")

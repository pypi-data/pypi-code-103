import csv
import json
import os
import random
import string
import time

import jsonpath
import pymysql
import yaml

_DEFAULT_ENCODING_UTF8 = "utf-8"
_CHARACTER_COMMA = ","
_CHARACTER_SLASH = "/"
_CHARACTER_DOT = "."
_LEVEL_FROM_PROJECT_ROOT = "../"
_SQUARE_BRACKETS_LEFT = "["
_SQUARE_BRACKETS_RIGHT = "]"
_CHARACTER_COLON = ":"

""" 私有方法，本文件使用 """


def _is_decimal_string(num_string):
    """
    判断是否数值组成的字符串
    :param num_string:
    :return:
        如果 num_string 是空值，False
        如果是：纯数值组成的字符串， True
        否则：False
    """
    if not num_string:
        return False

    result = True
    # 开始判断：一个个字符来检查，只要不是
    # "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
    # 循环 num_sting，一个个检查是不是个数字

    # 如果以数字 0 开头，返回 False
    if num_string.startswith("0"):
        return False

    # 如果有大于1个 的 ".", 返回 False
    if num_string.count(".") > 1:
        return False

    # 如果第一位是 "-", 移除第一位，继续

    if len(num_string) > 0 and num_string[0] == "-":
        num_string = num_string[1:]

    # 如果有一位小数点，把小数点去掉
    if num_string.count(".") == 1:
        num_string = num_string.replace(".", "")

    # 遍历每一位，判断是否在 0-9
    for char in num_string:
        # 任意一位不是 0-9，就退出循环
        if not _is_digital(char):
            result = False
            break

    return result


def _is_digital(char):
    """
    判断 char 是否是以下任意一个：
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
    :param char: 一位字符
    :return:
        如果是
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
        任意一个，返回 True
        否则，False
    """
    # 判断 char 是否是 "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
    # 的任意一个
    # if char not in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):

    return "0" <= char <= "9"


def _string_to_decimal(num_string):
    """
    把代表数值的字符串转成实际的数值
    :param num_string:
    :return:
        _string_to_decimal("123"), 返回 123
        _string_to_decimal("123.098"), 返回 123.098
        _string_to_decimal("-123"), 返回 -123
        _string_to_decimal("-123.098"), 返回 -123.098

    """

    is_negative = False

    # 处理正负
    if num_string[0] == "-":
        is_negative = True
        num_string = num_string[1:]

    # 处理整数
    num_int = num_string.split(".")[0]
    result = _calc_string(num_int)

    # 判断小数位
    if "." in num_string:
        num_float = num_string.split(".")[1]
        # 处理小数
        result += _calc_string(num_float, True)

    # 处理负数运算
    if is_negative:
        result = -1 * result
    return result


def _calc_string(num_string, is_float=False):
    """
    处理数位
    :param num_string:
    :param is_float: 默认是 False，代表是处理整数部分
    :return:
        is_float 是 False：处理整数
            123 = 1 * 10^2 + 2 * 10^1 + 3 * 10^0
        is_float 是 True： 处理小数
            123 = 1 * 10^-1 + 2 * 10^-2 + 3 * 10^-3
    """
    if is_float:
        # 处理小数
        digit_length = -1
    else:
        digit_length = len(num_string) - 1

    re_value = 0
    for digit in num_string:
        digit_int = ord(digit) - 48
        re_value += digit_int * pow(10, digit_length)
        digit_length -= 1

    return re_value


def _parse_file_name(filename):
    """
    处理文件路径，如果是 "\"， 就改成 "/"，
    如果以 "/" 开头，要改成 "./" 开头
    :param filename:
    :return:
    """
    if filename is not None and isinstance(filename, str) and len(filename) > 0:
        filename = filename.replace("\\", _CHARACTER_SLASH)

        if filename[0] == _CHARACTER_SLASH:
            filename = ".%s" % filename

    return filename


def _get_dict_value(dict_data: dict, data_key: str):
    """
    根据字典的 key，解析字典的 value，支持递归调用
    :param dict_data:
    :param data_key:
    :return:
    """
    if dict_data is not None and isinstance(dict_data, dict) and data_key is not None and data_key != "":
        data_key = data_key.strip()
        # 如果 data_key 是当前 dict_data 的，直接返回 value
        if data_key in dict_data.keys():
            return dict_data.get(data_key)

        # 如果没有直接返回 value，并且 data_key 中有 "."，则拆分左边的部分，读取左边部分的 value，右边部分作为新的 key，递归调用
        if _CHARACTER_DOT in data_key:
            new_dict_data_key = data_key.split(_CHARACTER_DOT)[0]
            new_data_key = data_key.replace("%s." % new_dict_data_key, "", 1)
            new_dict_data = dict_data.get(new_dict_data_key)

            # 如果左边部分的 value 不是 None，直接递归调用
            if new_dict_data is not None:
                return _get_dict_value(dict_data=new_dict_data, data_key=new_data_key)

            # 如果左边部分的 value 是 None，先看是否有 “.”，如果没有“.” 再看有没有中括号
            # 如果左边部分的 value 是 None，判断是否有中括号 "[]"，如果有就继续拆分中括号
            if _SQUARE_BRACKETS_LEFT in new_dict_data_key and _SQUARE_BRACKETS_RIGHT in new_dict_data_key:
                real_new_dict_data_key = new_dict_data_key.split(_SQUARE_BRACKETS_LEFT)[0]
                real_new_dict_data_key_index = _string_to_decimal(
                    new_dict_data_key.split(_SQUARE_BRACKETS_LEFT)[1].replace(_SQUARE_BRACKETS_RIGHT, "", 1)
                )
                real_new_dict_data_value = dict_data.get(real_new_dict_data_key)

                # 使用具体下标进行，读取真实的值，并继续递归使用
                if real_new_dict_data_value is not None and isinstance(real_new_dict_data_value, list):
                    if len(real_new_dict_data_value) - real_new_dict_data_key_index >= 1:
                        new_dict_data = real_new_dict_data_value[real_new_dict_data_key_index]

            return _get_dict_value(dict_data=new_dict_data, data_key=new_data_key)
        else:
            if _SQUARE_BRACKETS_LEFT in data_key and _SQUARE_BRACKETS_RIGHT in data_key:
                real_new_dict_data_key = data_key.split(_SQUARE_BRACKETS_LEFT)[0]
                real_new_dict_data_key_index = _string_to_decimal(
                    data_key.split(_SQUARE_BRACKETS_LEFT)[1].replace(_SQUARE_BRACKETS_RIGHT, "", 1)
                )
                real_new_dict_data_value = dict_data.get(real_new_dict_data_key)

                # 使用具体下标进行，读取真实的值，并继续递归使用
                if real_new_dict_data_value is not None and isinstance(real_new_dict_data_value, list):
                    if len(real_new_dict_data_value) - real_new_dict_data_key_index >= 1:
                        new_dict_data = real_new_dict_data_value[real_new_dict_data_key_index]
                        return new_dict_data


def _str_random(digits=True, lower=True, upper=True, punctuation=False, length=20):
    """
    生成指定长度的随机字符串，只包含大小写和数字
    :param punctuation:
    :param upper:
    :param lower:
    :param digits:
    :param length:
    :return:
    """
    all_char = ""
    if digits:
        all_char += string.digits
    if lower:
        all_char += string.ascii_lowercase
    if upper:
        all_char += string.ascii_uppercase
    if punctuation:
        all_char += string.punctuation

    return "".join(random.choice(all_char) for _ in range(length))


class Path(object):
    """
    Desc: Encapsulation of requests library
    Date: 20191127
    Author: Linty Liu (Tingli)
    Email: liu.tingli@outlook.com
    """

    @staticmethod
    def get_actual_path_by_current_file(current: str, file_path: str):
        """
        获取绝对路径
        从项目根目录与执行文件的相对路径中获取绝对路径
        :param current: 当前文件的真实绝对路径
        :param file_path: 被访问文件与当前文件的相对路径
        :return: 路径
        """
        current_file_path = os.path.dirname(current)
        name_file_path = _parse_file_name(file_path)
        abspath = os.path.abspath(os.path.join(current_file_path, name_file_path))
        return abspath

    @staticmethod
    def get_actual_path_by_project_root(filename: str):
        """
        获取绝对路径
        从项目根目录与执行文件的相对路径中获取绝对路径
        :param filename: 被访问文件与当前项目的根目录的相对路径
        :return: 路径
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filename = _parse_file_name(filename)
        abspath = os.path.abspath(os.path.join(base_dir, _LEVEL_FROM_PROJECT_ROOT, filename))
        return abspath

    @staticmethod
    def file_is_exist(filename: str):
        """
        file is exist
        :param filename:
        :return:
        """
        if filename is not None and filename != "":
            return os.path.exists(filename)


class Csv(object):

    @staticmethod
    def read_for_parametrize(f, encoding=_DEFAULT_ENCODING_UTF8):
        """
        读csv文件作为普通 Dict List
        :param f:
        :param encoding:
        :return:
        """
        data_ret = []
        with open(f, encoding=encoding, mode='r') as csv_file:
            csv_dict = csv.DictReader(csv_file)

            for row in csv_dict:
                row_dict = {}
                for key, value in row.items():
                    key = key.strip()
                    if value is not None and isinstance(value, str):
                        value = value.strip()

                        # 如果在 csv 中写的字符串是变成小写以后 是 "null", 就认定要给参数传递 None 值
                        if value.lower() in ["null", "none"]:
                            row_dict[key] = None
                        elif value.lower() in ["false", "true"]:
                            if value.lower() == "false":
                                row_dict[key] = False
                            elif value.lower() == "true":
                                row_dict[key] = True
                        else:
                            row_dict[key] = parse_digit(value)
                    else:
                        row_dict[key] = value
                data_ret.append(row_dict)

        return data_ret


class Db(object):
    """
    MySQL 数据库帮助类
    # 使用方法
    # 1. 实例化对象
    # 2. 查询，得到结果
    # 3. 关闭对象
    """

    __connect = None

    def __init__(self, host, port, user, password, database, charset=_DEFAULT_ENCODING_UTF8):
        """
        构造方法
        :param host: 数据库的主机地址
        :param port: 数据库的端口号
        :param user: 用户名
        :param password: 密码
        :param database: 选择的数据库
        :param charset: 字符集
        """
        self.__connect = pymysql.connect(host=host, port=port,
                                         user=user, password=password,
                                         db=database, charset=charset)

    @staticmethod
    def read_sql(file, encoding=_DEFAULT_ENCODING_UTF8):
        """
        从 文件中读取 SQL 脚本
        :param file: 文件名 + 文件路径
        :param encoding:
        :return:
        """
        sql_file = open(file, "r", encoding=encoding)
        sql = sql_file.read()
        sql_file.close()
        return sql

    def query(self, sql):
        """
        执行 SQL 脚本查询并返回结果
        :param sql: 需要查询的 SQL 语句
        :return: 字典类型
            data 是数据，本身也是个字典类型
            count 是行数
        """
        if self.__connect is not None:
            with self.__connect.cursor() as cursor:
                row_count = cursor.execute(sql)
                rows_data = cursor.fetchall()
                return dict(
                    count=row_count,
                    data=rows_data
                )

    def execute(self, sql):
        """
        执行 SQL 脚本查询并返回结果
        :param sql: 需要查询的 SQL 语句
        :return: 字典类型
            data 是数据，本身也是个字典类型
            count 是行数
        """
        if self.__connect is not None:
            with self.__connect.cursor() as cursor:
                cursor.execute(sql)
                self.__connect.commit()

    def close(self):
        """
        关闭数据库连接
        :return:
        """
        self.__connect.close()


class Yaml(object):

    @staticmethod
    def get_config_as_dict(file, key=None):
        """
        获取所有配置 作为 Dict
        :param key: yaml 文件需要读取的  key
        :param file:
        :return: 如果没有传递 key，则返回整个文档
        """
        with open(file, mode='r', encoding='utf8') as file_config:
            config_dict = yaml.load(file_config.read(), Loader=yaml.FullLoader)
            if key and config_dict and isinstance(config_dict, dict):
                return _get_dict_value(config_dict, key)

            return config_dict

    @staticmethod
    def dict_to_yaml(yaml_dict: dict):
        """
        字典转 yaml 文件流
        :param yaml_dict:
        :return:
        """
        return yaml.dump(yaml_dict)


class Dict(object):

    @staticmethod
    def parse_dict_value(json_dict: dict, data_key, index=None, sub_key=None):
        """
        get json dict value
        :param json_dict:
        :param sub_key:
        :param data_key:
        :param index: 从 0 开始，默认值是 None
        :return:
        """
        if json_dict is not None:

            ret_dict = _get_dict_value(json_dict, data_key)
            if index is None:
                index = -1

            if (index >= 0) and isinstance(ret_dict, list) and (len(ret_dict) > index):
                ret_dict = ret_dict[index]

            if sub_key is not None:
                ret_dict = _get_dict_value(ret_dict, sub_key)

            return ret_dict

    @staticmethod
    def convert_dict_to_json_str(json_dict):
        """
        转换 Python Dict 为 Json 格式
        :param json_dict:
        :return: str
        """
        if json_dict is not None and isinstance(json_dict, dict):
            return json.dumps(json_dict)

        return None

    @staticmethod
    def convert_json_str_to_dict(json_str_to_convert):
        """
        转 json 格式的 字符串 为 Python 字典 dict 类型
        建议使用 bejson.com 编写 json，然后 压缩成为字符串，复制到变量
        :param json_str_to_convert:
        :return: str
        """
        if json_str_to_convert is not None and isinstance(json_str_to_convert, str):
            return json.loads(json_str_to_convert)

        return None

    @staticmethod
    def read_json_file_as_dict(json_file):
        """
        读 json 文件，然后把文件中的字符串转换为 python 字典 dict 类型
        ：:param json_file:
        :return:
        """
        if json_file is not None and isinstance(json_file, str):
            with open(json_file, mode="r", encoding=_DEFAULT_ENCODING_UTF8) as f:
                json_string = f.read()
                return json.loads(json_string)

        return None

    @staticmethod
    def merge_dict(first_dict: dict, second_dict: dict):
        """
        合并两个字典，作为一个字典，使用 update()
        :param first_dict:
        :param second_dict:
        :return: 两个字典的并集
        """
        # update() 是直接更新了 first_resp 这个字典（合并了 second_resp)
        # 注意 update() 返回值是 None，直接使用 first_resp 就可以了
        res = {}
        if first_dict is not None and second_dict is not None:
            res.update(first_dict)
            res.update(second_dict)
        # self.info("[%s] - 合并了两个字典，first=%r, second=%r" % (__name__, first_dict, second_dict))
        return res

    @staticmethod
    def remove_none_dict_value(params: dict):
        """
        移除掉参数字典中，值是 None 的元素，保证做到参数不传
        :param params:
        :return:
        """
        if params is not None:
            keys = params.keys()

            keys_to_remove = []
            for k in keys:
                if params[k] is None:
                    keys_to_remove.append(k)

            for ktr in keys_to_remove:
                params.pop(ktr)

        return params

    @staticmethod
    def parse_data_dict(data_input: dict, yml_data: dict, yml_data_key: str):
        """
        处理和解析 yaml 用例数据
        :param data_input:
        :param yml_data:
        :param yml_data_key:
        :return:
        """
        dict_map = parse_dict(yml_data, data_key=yml_data_key)
        ret_dict = {}

        if dict_map is not None and isinstance(dict_map, dict):
            for key, value in dict_map.items():
                ret_dict[key] = parse_dict(data_input, value)

        return ret_dict

    @staticmethod
    def dump_json(dict_to_dump: dict):
        """
        字典 dict 转为 json
        :return:
        """
        if dict_to_dump is not None and isinstance(dict_to_dump, dict):

            json_string = json.dumps(dict_to_dump,
                                     indent=4,
                                     separators=(_CHARACTER_COMMA, _CHARACTER_COLON))
            if json_string is not None and isinstance(json_string, str):
                json_string = json_string.encode('utf-8').decode('unicode_escape')

            return json_string

    @staticmethod
    def parse_dict_jsonpath(data_input: dict, jp: str):
        """
        处理和解析 yaml 用例数据
        :param data_input:
        :param jp: jsonpath
        :return:
        """
        ret_data = []
        if data_input is not None and isinstance(data_input, dict):
            ret_data = jsonpath.jsonpath(data_input, jp)

            if not ret_data:
                ret_data = []

        return ret_data


class Snowflake:
    """
    雪花算法，获取唯一的 ID
    """
    __start = None
    __last = None
    __count_id = None
    __data_id = None

    def __init__(self, data_id):
        """
        构建方法
        :param data_id:
        """
        self.__start = int(time.mktime(time.strptime('2018-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")))
        self.__last = int(time.time())
        self.__count_id = 0
        # 数据ID，这个自定义或是映射
        self.__data_id = data_id

    def get_id(self):
        """
        获取 唯一 ID
        :return:
        """
        # 时间差部分
        now = int(time.time())
        temp = now - self.__start

        # 时间差不够9位的在前面补0
        if len(str(temp)) < 9:
            length = len(str(temp))
            s = "0" * (9 - length)
            temp = s + str(temp)

        if now == self.__last:
            # 同一时间差，序列号自增
            self.__count_id += 1
        else:
            # 不同时间差，序列号重新置为0
            self.__count_id = 0
            self.__last = now

        # 标识ID部分
        if len(str(self.__data_id)) < 2:
            length = len(str(self.__data_id))
            s = "0" * (2 - length)
            self.__data_id = s + str(self.__data_id)

        # 自增序列号部分
        if self.__count_id == 99999:  # 序列号自增5位满了，睡眠一秒钟
            time.sleep(1)

        count_id_data = str(self.__count_id)
        if len(count_id_data) < 5:  # 序列号不够5位的在前面补0
            length = len(count_id_data)
            s = "0" * (5 - length)
            count_id_data = s + count_id_data

        return str(temp) + str(self.__data_id) + count_id_data


""" 公共方法，对外提供使用 """


def parse_digit(string_to_parse: str):
    """
    根据输入的 字符串，判断
    - 字符串是否是数字
        - 如果字符串是数字，判断是否是整数
            - 如果是整数就返回整数
            - 否则返回小数
        - 如果字符串不是数字，返回字符串本身

    :param string_to_parse:
    :return:
    """
    if not isinstance(string_to_parse, str):
        return string_to_parse

    if string_to_parse is not None and string_to_parse != "":
        string_to_parse = string_to_parse.strip()
        if string_to_parse == "0":
            return 0

        if _is_decimal_string(string_to_parse):
            return _string_to_decimal(string_to_parse)

    return string_to_parse


def parse_dict(dict_data: dict, data_key: str, index=None, sub_key=None):
    """
    解析 JSON
    :param dict_data: 被解析的 JSON 的字典格式
    :param data_key: 请用 "." 隔开路径
    :param index:
    :param sub_key:
    :return:
    """
    if dict_data is not None and data_key is not None:
        return Dict.parse_dict_value(
            json_dict=dict_data,
            data_key=data_key,
            index=index,
            sub_key=sub_key
        )


def parse_jp(data_input: dict, jp: str):
    """
    按照 jsonpath 的方式解析 python dict
    :param data_input:
    :param jp:
    :return:
    """
    return Dict.parse_dict_jsonpath(data_input=data_input, jp=jp)


def parse_case_data_dict(data_input: dict, yml_data: dict, yml_data_key: str):
    """
    处理和解析 yaml 配置，从 data_input 解析得到用例数据
    :param data_input:
    :param yml_data:
    :param yml_data_key:
    :return:
    """
    dict_map = parse_dict(yml_data, data_key=yml_data_key)
    ret_dict = {}

    if dict_map is not None and isinstance(dict_map, dict):
        for key, value in dict_map.items():
            ret_dict[key] = parse_dict(data_input, value)

    return ret_dict


def read_txt(current: str, file_path: str):
    """
    读纯文本文件
    :param current:
    :param file_path:
    :return:
    """
    txt_file = Path.get_actual_path_by_current_file(current, file_path)
    if Path.file_is_exist(txt_file):
        with open(file_path, mode="r", encoding=_DEFAULT_ENCODING_UTF8) as file:
            return file.read()


def read_csv(current, file_path):
    """
    读 CSV 文件，CSV 文件必须有标题
    :param current: 读 CSV 文件的绝对路径，直接填写 __file__ 就可以了
    :param file_path: CSV 文件相对当前的路径（是相对路径），当前文件通过相对路径访问 csv 所需要的路径字符串
    :return: list 列表，列表中的元素是 dict，dict 的 key 是 csv 的第一行的标题
    """
    csv_file = Path.get_actual_path_by_current_file(current=current, file_path=file_path)
    return Csv.read_for_parametrize(csv_file)


def read_yaml(current, file_path, key=None):
    """
    读 YAML 文件，YAML 文件必须有标题
    :param current: 读 YAML 文件的绝对路径，直接填写 __file__ 就可以了
    :param file_path: YAML 文件相对当前的路径（是相对路径）
    :param key: 读 YAML 文件中制定的 key
    :return: dict，dict 的内容是 YAML 对应的 key 的 value
    """
    yml_file = Path.get_actual_path_by_current_file(current=current, file_path=file_path)
    return Yaml.get_config_as_dict(file=yml_file, key=key)


def read_json(current_file_path, json_to_current):
    """
    读 Json 文件，然后转化为 dict
    :param current_file_path:
    :param json_to_current:
    :return:
    """
    json_file = Path.get_actual_path_by_current_file(current_file_path, json_to_current)
    return Dict.read_json_file_as_dict(json_file)


def get_project_path(file_name: str):
    """
    根据项目根目录获取文件的路径
    :param file_name:
    :return:
    """
    return Path.get_actual_path_by_project_root(file_name)


def get_file_name(name: str):
    """
    获取文件文件的名字，不包含扩展名，不包含路径
    :param name:
    :return:
    """
    if name is not None and name != "":
        if _CHARACTER_DOT in name:
            names = name.strip().split(_CHARACTER_DOT)
            return names[-1]
        return name


def str_to_decimal(digit_str, digits=None):
    """
    转变 字符串（数字组成的字符串）为数字
    :param digits: 数值的小数位数，默认是 None
    :param digit_str: 数字组成的字符串
        规则：
            接受整型 "123"
            接受负数 "-123"
            接受小数 "-123.88"， "123.88"

    :return:
        如果 digit_str 是字符串 str 格式，就转化
        否则，返回 原样的值
    """
    ret_decimal = digit_str
    if digit_str is not None and isinstance(digit_str, str):
        ret_decimal = parse_digit(digit_str)
    if digits is not None and isinstance(ret_decimal, float) and isinstance(digits, int):
        ret_decimal = round(ret_decimal, digits)
    return ret_decimal


def json_to_dict(json_str_to_convert):
    """
    转 json 格式的 字符串 为 Python 字典 dict 类型
    建议使用 bejson.com 编写 json，然后 压缩成为字符串，复制到变量
    :param json_str_to_convert:
    :return: dict
    """

    if json_str_to_convert is not None and isinstance(json_str_to_convert, str):
        return Dict.convert_json_str_to_dict(json_str_to_convert)

    return None


def dict_to_yaml(dict_to_convert):
    """
    字典转 yaml 格式
    :param dict_to_convert:
    :return:
    """
    if dict_to_convert is not None and isinstance(dict_to_convert, dict):
        return Yaml.dict_to_yaml(dict_to_convert)

    return None


def random_string(length: int):
    """
    随机指定长度的字符串，包含大小写，数字，不包含特殊符号
    :param length: 长度
    :return: str
    """
    return _str_random(length=length)


def random_string_letters(length: int):
    """
    随机指定长度的字符串，只包含大小写，不包含数字，不包含特殊字符
    :param length: 长度
    :return: str
    """
    return _str_random(digits=False, length=length)


def random_string_with_punctuation(length: int):
    """
    随机指定长度的字符串，只包含大小写、数字和特殊字符
    :param length: 长度
    :return: str
    """
    return _str_random(punctuation=True, length=length)


def random_string_lower(length: int):
    """
    随机指定长度的字符串，只包含小写
    :param length: 长度
    :return: str
    """
    return _str_random(upper=False, digits=False, punctuation=False, length=length)


def random_string_digits(length: int):
    """
    随机指定长度的字符串，只包含数字
    :param length: 长度
    :return: str
    """
    return _str_random(upper=False, lower=False, punctuation=False, length=length)


def wait(seconds=5):
    """
    让 python 等待，默认 5 秒钟
    :param seconds: int， 大于 0
    :return:
    """
    if not isinstance(seconds, int) or seconds <= 0:
        seconds = 5

    time.sleep(seconds)


def get_snowflake_id(data_id: str = "00"):
    """
    获取 雪花算法 Id
    :param data_id:
    :return:
    """
    sl = Snowflake(data_id=data_id)
    return sl.get_id()

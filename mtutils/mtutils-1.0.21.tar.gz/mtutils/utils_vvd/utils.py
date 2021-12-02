# -*- coding: utf-8 -*-
# @Author: Zhang Yiwei
# @Date:   2020-07-18 02:40:35
# @Last Modified by:   Zhang Yiwei
# @Last Modified time: 2020-08-18 15:51:06
#
# vvd Tool functions
#

# 整合常用os操作
import os.path as osp
from os.path import basename as OS_basename
from os.path import join as OS_join
from os.path import exists as OS_exists
from os.path import isdir as OS_isdir
from os.path import dirname as OS_dirname
from numpy.lib.function_base import iterable

import pypinyin

from pathlib2 import Path as Path2
from pathlib import Path
import PIL.Image as Image

import matplotlib.pyplot as plt

from glob import glob
import string
import numpy as np
import inspect
import json
import time
import sys
import cv2 as cv
import logging
import os
import platform
import hashlib
import pickle
import uuid
import shutil

from tqdm import tqdm

from collections import OrderedDict
from functools import wraps
from functools import reduce



def get_list_from_list(data_list, call_back, absolutely=False):
    """[make a list through a input list,
    while the output list will collect the output of a function dealing with every item of the input list]

    Args:
        data_list ([list/np.ndarray]): [original input list]
        call_back ([function]): [a call back function to do sth with every item of input list]
        absolutely([bool]): add result of call_back function to output_list whatever it is
    Returns:
        output_list[list]: [collection of output of call_back function]
    """
    output_list = list()
    if isinstance(data_list, np.ndarray):
        data_list = data_list.tolist()
    if isinstance(data_list, list):
        for data in data_list:
            res = call_back(data)
            if res is not None or absolutely:
                output_list.append(res)
    elif isinstance(data_list, dict):
        for key, data in data_list.items():
            res = call_back(data)
            if res is not None or absolutely:
                output_list.append(res)
    else:
        raise RuntimeError('input should be list or dict')
    return output_list


def segment_intersection(seg_1, seg_2):
    assert len(seg_1) == len(seg_2) == 2
    inter_dis = max(0, min(max(seg_1), max(seg_2)) - max(min(seg_1), min(seg_2)))
    return inter_dis


def get_mac_address():
    mac = uuid.UUID(int = uuid.getnode()).hex[-12:].upper()
    # return '%s:%s:%s:%s:%s:%s' % (mac[0:2],mac[2:4],mac[4:6],mac[6:8],mac[8:10],mac[10:])
    return ":".join([mac[e: e+2] for e in range(0, 11, 2)])


def cal_distance(vector_1, vector_2, axis=None):
    assert len(vector_1) == len(vector_2) or len(vector_2) == 1
    distance = (np.sum((np.array(vector_1) - np.array(vector_2)) ** 2, axis=axis)) ** 0.5
    return distance


def OS_dir_list(dir_path: str):
    """[文件夹下所有文件夹路径]

    Args:
        dir_path (str): [输入文件夹路径]

    Returns:
        [list]: [文件夹下文件夹路径（非递归）]
    """
    dir_name_list = os.listdir(dir_path)
    path_list = list()
    for dir_name in dir_name_list:
        path = OS_join(dir_path, dir_name)
        if OS_isdir(path):
            path_list.append(path)
    return path_list


def get_file_size_M(file_path):
    """[get file size]

    Args:
        file_path ([str/Path]): [path to file]

    Returns:
        [float]: [size of file by M]
    """
    return os.path.getsize(str(file_path)) / 1024 / 1024


def unify_data_to_python_type(data):
    """[transfer numpy data to python type]

    Args:
        data ([dict/list]): [data to transfer]

    Returns:
        [type of input data]: [numpy data will be transfered to python type]
    """
    return json.loads(json.dumps(data, cls=MyEncoder))


def timer_vvd(func):
    """
    a timer for func
    you could add a @timer_vvd ahead of the fun need to be timed
    Args:
        func (function): a function to be timed

    Outputs:
        time message: a message which tells you how much time the func spent will be printed
    """
    is_static_method = False
    try :
        func_name = func.__name__
    except Exception as e:
        func_name = func.__func__.__name__
        func = func.__func__
        is_static_method = True

    @wraps(func)
    def wrapper(*args, **kwargs):
        if is_static_method:
            args = args[1:]

        start_time = time.time()
        res = func(*args, **kwargs)
        end_time = time.time()
        print('func: {_funcname_} runing: {_time_}s'.format(_funcname_=func_name, _time_=format(end_time - start_time, '.6f')))
        return res
    return wrapper


def file_rename(srcFile, dstFile):
    srcFile = str(srcFile)
    dstFile = str(dstFile)
    assert OS_exists(srcFile), f"srcFile {srcFile} not found"
    try:
        os.rename(srcFile, dstFile)
    except Exception as e:
        print(e)
        print('rename file fail\r\n')


def get_current_dir():
    """
    get current dir of the running file
    """
    return os.path.dirname(os.path.realpath(__file__))


def file_read_lines(file_path, encoding='utf8'):
    if not OS_exists(file_path):
        print("file {} not found, None will be return".format(file_path))
        return None

    with open(file_path, "r", encoding=encoding) as f:
        lines = f.readlines()
        for index, line in enumerate(lines):
            lines[index] = line.strip('\n')
        return lines


def file_write_lines(line_list, file_path, overwrite=False, verbose=False):
    dir_check(OS_dirname(file_path))
    file_path = save_file_path_check(file_path, overwrite, verbose)
    with open(file_path, 'w', encoding='utf8') as f:
        f.writelines('\n'.join(line_list))


def pickle_save(object, save_path, overwrite=False, verbose=False):
    """
    将object保存为pickle文件到save_path中
    """
    save_path = save_file_path_check(save_path, overwrite, verbose)
    with open(save_path, 'wb') as fp:
        pickle.dump(object, fp)


def pickle_load(load_path):
    """
    从load_path中读取object
    """
    assert isinstance(load_path, str) or is_path_obj(load_path)
    if isinstance(load_path, str):
        load_path = load_path.replace('\\', '/')
    with open(load_path, 'rb') as fp:
        return pickle.load(fp)


def find_sub_string(string, substring, times):
    """
    find the char position of the substring in string for times-th comes up
    """
    current = 0
    for _ in range(1, times+1):
        current = string.find(substring, current+1)
        if current == -1:
            return -1

    return current


def underline_connection(*str_args, connect_char='_'):
    """
    connect strings in the list with underline
    """
    assert isinstance(str_args, tuple)
    string = ""
    for item in str_args:
        if isinstance(item, list):
            item = underline_connection(*item, connect_char=connect_char)
        if item != '':
            string = string + str(item) + connect_char
    string = string[:-1]
    return string


def get_main_file_name(string):
    """
    return file name without extension
    """
    assert isinstance(string, str) or is_path_obj(string)
    if is_path_obj(string):
        string = str(string)
    return os.path.splitext(os.path.basename(string))[0]


def strong_printing(*str_args):
    """
    print string strongly
    """
    assert isinstance(str_args, tuple)
    string = underline_connection(*str_args, connect_char=' ')
    print()
    boudary_size = int(max(40, len(string)*1.4))
    split_string = boudary_size*'#'
    print(split_string)
    space_size = (boudary_size - len(string))//2
    print(space_size*' '+string.upper())
    print(split_string)
    print()


def current_system():
    """
    返回当前操作系统名称字符串
    """
    return platform.system()


def current_split_char():
    """
    返回当前操作系统的路径分隔符
    """
    if current_system() == 'Windows':
        return '\\'
    elif current_system() == 'Linux':
        return '/'
    else:
        return '/'


def save_file_path_check(save_file_path, overwrite=False, verbose=False):
    """
    检查要保存的文件路径
    - 如果文件已经存在 ： 在文件名与扩展名之间加入当前时间作为后缀 避免覆盖之前的文件并给出提示
    - 如文件不存在 ： 检查文件所在的文件夹目录
    返回检查后的文件路径
    """
    if is_path_obj(save_file_path):
        save_file_path = str(save_file_path)

    assert isinstance(save_file_path, str)
    if OS_exists(save_file_path):
        if overwrite:
            checked_save_file_path = save_file_path
            if verbose:
                print("file path {} already exists, the file will be overwrite.".format(save_file_path))
        else:
            main_file_name = get_main_file_name(save_file_path)
            new_base_name = OS_basename(save_file_path).replace(main_file_name, underline_connection(main_file_name, time_stamp()))
            checked_save_file_path = OS_join(OS_dirname(save_file_path), new_base_name)
            if verbose:
                print("file path {} already exists, the file will be saved as {} instead.".format(save_file_path, checked_save_file_path))
    else:
        dir_check(str(Path(save_file_path).parent), verbose)
        assert OS_basename(save_file_path) != ''
        checked_save_file_path = save_file_path
    return checked_save_file_path


def encode_chinese_to_unicode(input_string, remove=False):
    '''
    将中文转换为 unicode #Uxxxx 形式
    '''
    unicode_string = ''
    for char in input_string:
        if ord(char) > 255:
            if remove:
                continue
            char = "%%U%04x" % ord(char)
        unicode_string += char
    unicode_string = unicode_string.replace('%', '#')
    return unicode_string


def create_uuid2():
    """ create a uuid (universally unique ID) """
    return uuid.uuid1().hex


def create_uuid():
    """ create a uuid (universally unique ID) """
    md5_hash = hashlib.md5(uuid.uuid1().bytes)
    return md5_hash.hexdigest()


def get_file_hash_code(file):
    """
    获取文件hash值
    """
    assert os.path.exists(file)
    md5_hash = hashlib.md5()
    with open(file, "rb") as fid:
        md5_hash.update(fid.read())
        digest = md5_hash.hexdigest()
    return digest


class MyEncoder(json.JSONEncoder):
    """
    自定义序列化方法，解决 TypeError - Object of type xxx is not JSON serializable 错误
    使用方法：
    在json.dump时加入到cls中即可，例如：
    json.dumps(data, cls=MyEncoder) 
    """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, Path) or isinstance(obj, Path2):
            return str(obj)
        else:
            return super(MyEncoder, self).default(obj)


class Sys_Logger(object):
    '''
    修改系统输出流
    '''

    def __init__(self, fileN="Default.log"):

        self.terminal = sys.stdout
        if OS_exists(fileN):
            self.log = open(fileN, "a")
        else:
            self.log = open(fileN, "w")

    def write(self, message):

        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()


class Loger_printer():
    """
    日志打印类
    会在控制台与日志同时打印信息    
    """

    def __init__(self, logger):
        self.logger = logger

    def vvd_logging(self, *message):
        for message_str in message:
            print(message_str)
            self.logger.info(message_str)

    def vvd_logging_quiet(self, *message):
        for message_str in message:
            self.logger.info(message_str)


def log_init(log_path, quiet=False):
    """
    initialize logging 
    save the logging object in `config.Parameters.Logging_Object`

    after this operation,
    we could save logs with simple orders such as `logging.debug('test debug')` `logging.info('test info')` 
    logging level : debug < info < warning <error < critical

    Loger_printer.vvd_logging('test')
    """
    dir_name = os.path.dirname(log_path)

    dir_check(dir_name)

    log_file_path = log_path

    if os.path.exists(log_file_path):
        # open log file as  mode of append
        open_type = 'a'
    else:
        # open log file as  mode of write
        open_type = 'w'

    logging.basicConfig(

        # 日志级别,logging.DEBUG,logging.ERROR
        level=logging.INFO,

        # 日志格式: 时间、   日志信息
        format='%(asctime)s: %(message)s',

        # 打印日志的时间
        datefmt='%Y-%m-%d %H:%M:%S',

        # 日志文件存放的目录（目录必须存在）及日志文件名
        filename=log_file_path,

        # 打开日志文件的方式
        filemode=open_type
    )

    logging.StreamHandler()

    if quiet:
        return Loger_printer(logging).vvd_logging_quiet
    else:
        return Loger_printer(logging).vvd_logging


def dir_exists(dir_path):
    """
    check if dir exists
    """
    dir_path = str(dir_path)
    if not os.path.isdir(dir_path):
        raise TypeError("dir not found")


def uniform_split_char(string, split_char=current_split_char()):
    """
    uniform the split char of a string
    """
    assert isinstance(string, str)
    return string.replace('\\', split_char).replace('/', split_char)


def dir_check(dir_path, verbose=False):
    """
    check if `dir_path` is a real directory path
    if dir not found, make one
    """

    dir_path = str(dir_path)
    assert isinstance(dir_path, str)
    dir_path = uniform_split_char(dir_path)
    if not os.path.isdir(dir_path):
        try:
            os.makedirs(dir_path)
            if verbose:
                print('dirs made: {}'.format(dir_path))
        except Exception as err:
            print(f'failed to make dir {dir_path}, error {err}')
        return False
    else:
        return True


def time_reduce(*data):
    """
    [计算输入数据的乘积]
    """
    data = list(data)
    return reduce(lambda x, y: x*y, data)


def get_function_name():
    '''获取正在运行函数(或方法)名称'''
    # print(sys._getframe().f_code.co_name)
    return inspect.stack()[1][3]


def draw_RB_map(y_true, y_pred, map_save_path=None):
    assert isinstance(y_pred, np.ndarray) and isinstance(y_true, np.ndarray)
    assert np.ndim(y_pred) == 1
    assert y_pred.shape == y_true.shape

    sorted_ids = np.argsort(y_pred+np.random.rand(y_pred.size)*1e-8)
    sorted_y_true = y_true[sorted_ids]
    ng_rank = np.where(sorted_y_true == 1)[0]
    ok_rank = np.where(sorted_y_true == 0)[0]

    plt.figure(figsize=(25, 3))
    plt.bar(ok_rank, 1, width=1, color='b')
    plt.bar(ng_rank, 1, width=int(ok_rank.size/ng_rank.size/5+1), color='r')
    plt.ylim([0, 1])
    plt.xlim([0, len(ok_rank)+len(ng_rank)])
    if map_save_path is not None:
        plt.savefig(map_save_path)
    plt.show()

    plt.figure(figsize=(25, 3))
    plt.hist(y_pred, bins=255)
    plt.title('ng_score distribution')
    plt.show()


def histgrom(*data, bin_num=100):
    data_list = list(data)
    for data_item in data_list:
        plt.hist(data_item, bin_num)
    plt.show()


def data_show(data):
    '''
    show data in a chart
    '''
    plt.plot(data)
    plt.show()


def is_path_obj(path):
    if isinstance(path, Path) or isinstance(path, Path2):
        return True
    else:
        return False


def time_stamp():
    """
    返回当前时间戳字符串
    格式: 年-月-日_时-分-秒
    """
    return time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())


def smart_copy(source_file_path, target_path, verbose=False, remove_source_file=False):
    """[复制文件从源到目标，如果目标已经存在则跳过]]

    Args:
        source_file_path ([str]): [源文件路径]
        target_path ([str]): [目标文件夹/目标文件路径]
        verbose (bool, optional): [是否显示信息]. Defaults to False.
    """
    source_file_path = str(source_file_path).replace('\\', '/')
    target_path = str(target_path).replace('\\', '/')
    assert OS_exists(source_file_path)
    if OS_isdir(target_path):
        target_path = OS_join(target_path, OS_basename(source_file_path))
    if OS_exists(target_path):
        if verbose:
            print("{} already exists!".format(target_path))
    else:
        dir_check(Path(target_path).parent)

        if remove_source_file:
            shutil.move(source_file_path, target_path)
        else:
            shutil.copy(source_file_path, target_path)


def json_load(json_path, verbose=False):
    """
    读取json文件并返回内容字典
    """
    json_path = str(json_path)
    if isinstance(json_path, str):
        json_path = json_path.replace('\\', '/')
    try:
        assert OS_exists(json_path)
    except Exception as e:
        if verbose:
            print('file not found !', e)
    try:
        with open(json_path, 'r') as fp:
            return json.load(fp)
    except Exception as e:
        if verbose:
            print('simple json load failed, try utf-8', e)
    try:
        with open(json_path, 'r', encoding='utf-8') as fp:
            return json.load(fp)
    except Exception as e:
        if verbose:
            print('utf-8 json load failed, try gbk', e)
    try:
        with open(json_path, 'r', encoding='gbk') as fp:
            return json.load(fp)
    except Exception as e:
        if verbose:
            print('gbk json load failed!', e)        


def json_save(json_dict, json_path, overwrite=False, verbose=False):
    """
    将内容字典保存为json文件
    """
    json_path = str(json_path)
    json_path = save_file_path_check(json_path, overwrite, verbose)
    with open(json_path, 'w', encoding='utf-8') as fp:
        json.dump(json_dict, fp, ensure_ascii=False, sort_keys=False, indent=4, cls=MyEncoder)


def glob_recursively(path, extension, recursively=True):
    """
    在path 路径中递归查找所有扩展名为extension的文件，返回完整路径名列表
    """
    path = str(path)
    if recursively:
        return glob(OS_join(path, '**', '*.' + extension), recursive=True)
    else:
        return glob(OS_join(path, '*.' + extension), recursive=True)


def is_integer(num):
    """
    是否是整数，返回bool结果
    """
    return isinstance(num, (int, np.int, np.int32, np.uint8, np.int16, np.int64))


def is_float(num):
    """
    是否是浮点数，返回bool结果
    """
    return isinstance(num, (float, np.floating))


def is_number(num):
    """
    是否是数字，返回bool结果
    """
    return is_float(num) or is_integer(num)


def is_bool(data):
    """
    是否是 bool 值，返回bool结果
    """
    return isinstance(data, bool) or isinstance(data, np.bool_)


def whether_divisible_by(to_be_divided, dividing):
    """
    to_be_divided 是否可以被 dividing 整除，返回bool结果
    """
    assert is_integer(to_be_divided) and is_integer(dividing)
    if to_be_divided % dividing == 0:
        return True
    else:
        return False


def vvd_round(num):
    if iterable(num):
        return np.round(np.array(num)).astype('int32').tolist()
    return int(round(num))


def vvd_ceil(num):
    if iterable(num):
        return np.ceil(np.array(num)).astype('int32').tolist()
    return int(np.ceil(num))


def vvd_floor(num):
    if iterable(num):
        return np.floor(np.array(num)).astype('int32').tolist()
    return int(np.floor(num))


def erode(mat, iterations=1, kernel_size=3):
    """ erode 2D binary matrix by one pixel """
    assert isinstance(mat, np.ndarray) and mat.dtype == np.bool
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    mat_eroded = cv.erode(mat.astype(np.uint8), kernel, iterations=iterations)
    return mat_eroded > 0


def dilate(mat, iterations=1, kernel_size=3):
    """ dilate 2D binary matrix by one pixel """
    assert isinstance(mat, np.ndarray) and mat.dtype == np.bool
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    mat_dilated = cv.dilate(mat.astype(np.uint8), kernel, iterations=iterations)
    return mat_dilated > 0


def open_op(mat, iterations=1, kernel_size=3):
    """ dilate 2D binary matrix by one pixel """
    assert isinstance(mat, np.ndarray) and mat.dtype == np.bool
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    mat_dilated = cv.erode(mat.astype(np.uint8), kernel, iterations=iterations)
    mat_dilated = cv.dilate(mat_dilated.astype(np.uint8), kernel, iterations=iterations)
    return mat_dilated > 0


def get_gpu_str_as_you_wish(gpu_num_wanted, verbose=0):
    """[get empty gpu index str as needed]

    Args:
        gpu_num_wanted ([int]): [the num of gpu you want]

    Returns:
        [str]: [gpu str returned]
    """
    try:
        import pynvml
    except Exception as e:
        print('can not import pynvml.', e)
        print('please make sure pynvml is installed correctly.')
        print('a simple pip install nvidia-ml-py3 may help.')
        print('now a 0 will be return')
        return '0'

    NUM_EXPAND = 1024 * 1024

    try:
        # 初始化工具
        pynvml.nvmlInit()
    except Exception as e:
        print('pynvml.nvmlInit failed:', e)
        print('now a 0 will be return')
        return '0'

    # 驱动信息
    if verbose:
        print("GPU driver version: ", pynvml.nvmlSystemGetDriverVersion())

    # 获取Nvidia GPU块数
    gpuDeviceCount = pynvml.nvmlDeviceGetCount()
    returned_gpu_num = max(min(gpu_num_wanted, gpuDeviceCount), 0)

    gpu_index_and_free_memory_list = list()
    for index in range(gpuDeviceCount):
        handle = pynvml.nvmlDeviceGetHandleByIndex(index)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        gpu_memory_total = info.total / NUM_EXPAND
        gpu_memory_used = info.used / NUM_EXPAND
        gpu_index_and_free_memory_list.append([index, gpu_memory_total - gpu_memory_used])
        if verbose:
            if index == 0:
                device_name = pynvml.nvmlDeviceGetName(handle)
                print('GPU device name:', device_name)
            print(f'gpu {index}: total_memory: {gpu_memory_total} memory_left: {gpu_memory_total - gpu_memory_used}')

    gpu_index_and_free_memory_list.sort(key=lambda x: - x[1])

    gpu_index_picked_list = list()

    for i in range(returned_gpu_num):
        gpu_index_picked_list.append(gpu_index_and_free_memory_list[i][0])

    gpu_index_str = ','.join([str(index) for index in gpu_index_picked_list])
    if verbose:
        print(returned_gpu_num, 'gpu index will be return.')
        print(f'return gpu str: {gpu_index_str}')

    # 关闭工具
    pynvml.nvmlShutdown()

    return gpu_index_str, gpu_index_picked_list


def get_dir_file_list(root_path, recursive=False):
    """[get dir and file list under root_path recursively]

    Args:
        root_path ([str]): [root dir to querry]
        recursive ([bool]): [whether walk recursively]

    Returns:
        dir_list [list]: [output dir list]
        file_list [list]: [output file list]
    """

    dir_list = list()
    file_list = list()

    root_path = str(root_path)

    for root, dirs, files in os.walk(root_path):
        file_list += get_list_from_list(files, lambda x: os.path.join(root, x))

        for dir in dirs:
            cur_dir_path = os.path.join(root, dir)
            dir_list.append(cur_dir_path)

        if not recursive:
            break

    return dir_list, file_list


def get_segments(data):
    """
    get segments for data (for moved safe data)
    """
    assert data.ndim == 1
    data = (data > 0).astype('int8')
    mark = data[:-1] - data[1:]
    start_pos = np.nonzero(mark == -1)[0].tolist()
    end_pos = np.nonzero(mark == 1)[0].tolist()
    if data[0] > 0:
        start_pos = [-1] + start_pos
    if data[-1] > 0:
        end_pos = end_pos + [len(mark)]
    assert len(start_pos) == len(end_pos)
    segments_list = [[x + 1, y] for x, y in zip(start_pos, end_pos)]
    return segments_list


def try_exc_handler(try_func, exc_func, developer_mode=False):
    except_result = try_result = None

    if developer_mode:
        try_result = try_func()
    else:
        try:
            try_result = try_func()
        except Exception as e:
            try:
                ori_exception_info = list(e.args)
                if len(ori_exception_info) == 0:
                    ori_exception_info.append('')
                ori_exception_info[0] = ' ErrorMessage: ' + str(ori_exception_info[0])\
                    + '\n CrashFile: ' + str(e.__traceback__.tb_next.tb_frame.f_globals['__file__'])\
                    + '\n Line: ' + str(e.__traceback__.tb_next.tb_lineno)

                e.args = tuple(ori_exception_info)
                except_result = exc_func(e)
            except Exception as ee:
                print("!! exc_func failed.")
                print(f"!! error message: {str(ee)}")
                print("!! we can only return the previous exception info.")
                except_result = str(e)
            return except_result

    return try_result


def class_timer(input_class):
    class Timmer(input_class):
        def __getattribute__(self, name: str):

            func = super().__getattribute__(name)

            if str(type(func)) == "<class 'method'>":
                is_static_method = False
                try :
                    func_name = func.__name__
                except Exception as e:
                    func_name = func.__func__.__name__
                    func = func.__func__
                    is_static_method = True

                @wraps(func)
                def wrapper(*args, **kwargs):
                    if is_static_method:
                        args = args[1:]

                    start_time = time.time()
                    res = func(*args, **kwargs)
                    end_time = time.time()
                    print('func: {_funcname_} runing: {_time_}s'.format(_funcname_=func_name, _time_=format(end_time - start_time, '.6f')))
                    return res
                return wrapper
            return func
    return Timmer


def remove_small_components(mask, area_thres):
    """ remove connected components from mask if their areas < area_thres """
    nccomps = cv.connectedComponentsWithStats(mask.astype(np.uint8))

    labels = nccomps[1]
    status = nccomps[2]

    for index, st in enumerate(status.tolist()):
        if st[0] == st[1] == 0:
            continue
        area = st[4]
        if area >= area_thres:
            labels[labels == index] = - index

    return labels < 0


def encode_path(path, seg_num = 4, key_word=None, sep_char='@', root_path=None, with_suffix=None, stem=False):

    if key_word is not None:
        pos = str(path).find(key_word)
        if pos == '-1':
            print('keyword encode path failed, use default function')
            key_word = None
        else:
            path = str(path)[pos:]
            tmp_path = Path(path)
            encoded_path = sep_char.join(tmp_path.parts)

    if key_word is None:
        tmp_path = Path(path)
        encoded_path = sep_char.join(tmp_path.parts[-seg_num:])

    if root_path is not None:
        encoded_path = str(Path(root_path) / encoded_path)

    if with_suffix is not None:
        encoded_path = str(Path(str(encoded_path)).with_suffix('.' + with_suffix))
    
    if stem:
        encoded_path = Path(encoded_path).stem

    return encoded_path


def extract_file_to(root_dir, suffix, target_dir, default_level=3):
    file_list = glob_recursively(root_dir, suffix)
    desc = f"Extracting {suffix} file from {root_dir} to {target_dir}:"
    for file_path in tqdm(file_list, desc=desc):
        file_name = encode_path(file_path, seg_num=default_level)
        save_path = Path(target_dir) / file_name
        smart_copy(file_path, save_path)


def hardlink(src, tar):
    if osp.isdir(tar):
        target_path = osp.join(tar, osp.basename(src))
    else:
        target_path = tar
    if osp.exists(target_path):
        return False
    else:
        if osp.exists(src):
            os.link(src, target_path)
        else:
            return False
    return True


class ListOrderedDict(OrderedDict):
    def __getitem__(self, key):
        if is_integer(key):
            key = list(self.keys())[key]
        elif isinstance(key, slice):
            slicedkeys = list(self.keys())[key]
            lod_obj = type(self)()
            for slicedkey in slicedkeys:
                lod_obj[slicedkey] = self[slicedkey]
            return lod_obj

        return super().__getitem__(key)

    def append(self, key, value):
        if is_integer(key):
            raise RuntimeError(f" integer key is not allowed in ListOrderedDict {key}.")
        assert key not in self, f"cannot add existed key. {key}"
        self[key] = value
    
    def __setitem__(self, key, value):
        'od.__setitem__(i, y) <==> od[i]=y'
        # Setting a new item creates a new link at the end of the linked list,
        # and the inherited dictionary is updated with the new key/value pair.
        if is_integer(key):
            raise RuntimeError(f" integer key is not allowed in ListOrderedDict {key}.")
        else:
            return super().__setitem__(key, value)

    def __delitem__(self, key):
        'od.__delitem__(y) <==> del od[y]'
        # Deleting an existing item uses self.__map to find the link which gets
        # removed by updating the links in the predecessor and successor nodes.
        if is_integer(key):
            key = list(self.keys())[key]

        return super().__delitem__(key)

    def move_to_end(self, key, last=True):
        '''Move an existing element to the end (or beginning if last is false).

        Raise KeyError if the element does not exist.
        '''
        if is_integer(key):
            key = list(self.keys())[key]

        return super().move_to_end(key, last)

    def __repr__(self):
        'od.__repr__() <==> repr(od)'
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self.items()))

    def pop(self, key=-1):
        '''od.pop(k[,d]) -> v, remove specified key and return the corresponding
        value.  If key is not found, d is returned if given, otherwise KeyError
        is raised.
        '''
        if is_integer(key):
            if len(list(self.keys())) == 0:
                print(f"pop a None from an empty ListOrderedDict.")
                return None
            key = list(self.keys())[key]
        return super().pop(key)

    def setdefault(self, key, default=None):
        '''Insert key with a value of default if key is not in the dictionary.

        Return the value for key if key is in the dictionary, else default.
        '''
        if is_integer(key):
            key = list(self.keys())[key]
        return super().setdefault(key, default)


def is_valid_identifier(input_str):
    ascii = string.ascii_letters+'_'
    digits = string.digits
    if not isinstance(input_str, str):
        return False
    if len(input_str) == 0:
        return False
    if input_str[0] not in ascii:
        return False
    for char in input_str:
        if char not in ascii and char not in digits:
            return False
    return True


def chinese_str_to_pinyin(input_str, join_char='_', remove=True):
    pinyin_str =  pypinyin.pinyin(input_str, style=pypinyin.NORMAL)
    pinyin_str_list = get_list_from_list(pinyin_str, lambda x: x[0])
    pinyin_res_str = join_char.join(pinyin_str_list)
    output_str = encode_chinese_to_unicode(pinyin_res_str, remove=remove)
    return output_str


def remove_chinese_for_file_names(root_dir):
    dir_list, file_list = get_dir_file_list(root_dir, recursive=True)
    file_name_changed = 0
    for file_path in tqdm(file_list, desc=f"changing file names: "):
        file_name = Path(file_path).name
        changed_name = chinese_str_to_pinyin(file_name)
        if file_name != changed_name:
            dst_path = Path(file_path).parent / changed_name
            file_rename(file_path, dst_path)
            file_name_changed += 1
    print(f"change {file_name_changed} file names.")
    
    dir_name_changed = 0
    for dir_path in tqdm(dir_list[::-1], desc=f"changing directory names: "):
        dir_name = Path(dir_path).name
        changed_name = chinese_str_to_pinyin(dir_name)
        if dir_name != changed_name:
            dst_path = Path(dir_path).parent / changed_name
            file_rename(dir_path, dst_path)
            dir_name_changed += 1
    print(f"change {dir_name_changed} dir names.")
    pass


if __name__ == '__main__':
    print(chinese_str_to_pinyin('asdfd_（阿斯蒂芬）'))
    
    is_valid_identifier('')
    test_name = 'abc/sadf/gsdf.sadf.test'
    strong_printing(test_name)
    print(underline_connection())
    get_gpu_str_as_you_wish(3, verbose=1)

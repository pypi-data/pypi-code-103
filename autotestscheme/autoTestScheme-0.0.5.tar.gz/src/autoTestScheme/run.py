import copy
import datetime
import json
import os
import sys
import queue
import shutil
import traceback
import uuid
import subprocess
from functools import cmp_to_key
import urllib3
urllib3.disable_warnings()
import pytest
import gevent
import time
from multiprocessing import Process
from locust.stats import stats_printer, stats_history
from locust.env import Environment
import locust, logging
from locust.log import greenlet_exception_logger
from locust.user.inspectuser import print_task_ratio
from .common import constant, config, common, start_data, robot
from .common.logger import logger

json_name = 'autoTestScheme'


def run_case(data: list, _uuid: str, env: str):
    if type(data) == dict:
        # 为适配无分组用例
        data = [data]
    _data = {}
    _data['__env'] = env
    num = 1
    for i in data:
        __file = i.get('__file')
        __func = i.get('__func')
        if __file not in list(_data.keys()):
            _data[__file] = {}
        if __func not in list(_data[__file].keys()):
            _data[__file][__func] = []
        i['__order'] = num
        _data[__file][__func].append(i)
        num += 1
    folder = os.path.join(constant.RUN_TMP_DIR, _uuid)
    if not os.path.exists(folder):
        os.makedirs(folder)
    _path = os.path.join(folder, 'case.json')
    logger.info('执行数据：{}, 数据地址:{}'.format(_data, _path))
    with open(_path, 'w+')as f:
        f.write(json.dumps(_data, sort_keys=True, indent=4, separators=(',', ':')))

    _path = os.path.join(constant.TMP_REPORTS_DIR, _uuid)
    command = ['-s', '--capture=no', '-v', '--alluredir', _path, '--clean-alluredir',
               '--cache-clear', '-W','ignore:Module already imported:pytest.PytestWarning', '--{}'.format(json_name), _uuid]
    logger.info('执行命令:{}'.format(command))
    pytest.main(command)


def run_locust(data: list, _uuid: str, env:str):
    ...



@common.singleton
class Run(object):

    def __init__(self):
        self.all_data = []
        self.all_data_by_channel_id = {}
        self.uuid_list = []
        self.data_folder = None
        self.api_data = []

    def register_tags(self, tags: dict):
        """
        注册标签列表
        :param tags:
        :return:
        """
        for key, value in tags.items():
            self.register_tag(key, value)

    def register_tag(self, key, value):
        """
        注册标签
        """
        start_data.TAG_LIST[key] = value

    def debug(self, tags=None, case='all', env='dev', process_num=1):
        """
        调试（注意，需要再用例的tags列表内添加debug标签）
        :param tags: 标签列表，为空时运行所有标签
        :param case: 执行指定的用例，all指所有用例
        :param env: 对应环境
        :param process_num:并行数
        :return:
        """
        if tags is None:
            tags = start_data.TAG_LIST.keys()
        self.run(tags, case, True, env, process_num)

    def set_logger_identifier(self, folder, _str):
        """
        修改日志前缀
        :param _str:
        :return:
        """
        start_data.Logger_START_STR = _str
        start_data.LOGGER_FOLDER = folder
        from .common import logger
        logger.restart()

    def load_case(self, folder_name):
        """
        加载用例数据
        :param folder_name: 启动脚本同级目录名
        :return:
        """
        self.data_folder = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), folder_name)

    def load_api(self, folder_name):
        """
        加载API数据
        :param folder_name: 启动脚本同级目录名
        :return:
        """
        api_folder = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), folder_name)

    def load_allure_tmp(self, folder_name):
        """
        定义allure缓存目录
        :param folder_name: 启动脚本同级目录名
        :return:
        """
        constant.TMP_REPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), folder_name)

    def append_locust_task(self, *args, **kwargs):
        gevent.spawn(*args, **kwargs)

    def run_locust(self, case: list, env: str, tag:set, host:str, ui_host:str='0.0.0.0', ui_port:int=8089):
        start_data.TEST_TAG = []
        start_data.TEST_CASE = 'all'
        start_data.IS_DEBUG = False
        start_data.IS_LOCUST = True
        start_data.TEST_ENV = env
        start_data.PROCESS_NUM = 1
        env = Environment(
            locustfile='',
            user_classes=case,
            tags=tag,
            events=locust.events,
            host=host
        )
        print_task_ratio(case)
        runner = env.create_local_runner()
        # main_greenlet = runner.greenlet
        web_ui = env.create_web_ui(ui_host, ui_port)
        env.events.init.fire(environment=env, runner=runner, web_ui=web_ui)
        main_greenlet = web_ui.greenlet
        stats_printer_greenlet = gevent.spawn(stats_printer(runner.stats))
        # setup_logging(loglevel, logfile)
        logger = logging.getLogger(__name__)
        greenlet_exception_handler = greenlet_exception_logger(logger)
        stats_printer_greenlet.link_exception(greenlet_exception_handler)
        gevent.spawn(stats_history, runner)
        main_greenlet.join()

    def run(self, tags, case, is_debug, env, process_num=6):
        self.init_dir()
        start_data.TEST_TAG = tags
        start_data.TEST_CASE = case
        start_data.IS_DEBUG = is_debug
        start_data.TEST_ENV = env
        start_data.PROCESS_NUM = process_num
        logger.info("相关参数:{},{},{},{},{}".format(start_data.TEST_TAG, start_data.TEST_CASE,
                                                 start_data.IS_DEBUG, start_data.TEST_ENV, start_data.PROCESS_NUM))
        logger.info('开始收集测试用例。。。。。')
        group, surplus_data = self.get_group_data()
        group_length = len(group)
        surplus_length = len(surplus_data)
        logger.info('分组用例：{}'.format(group))
        logger.info('未分组用例：{}'.format(surplus_data))

        # 执行分组用例
        if len(group) == 0:
            logger.info('分组用例为空')
            del group
        elif len(group) == 1:
            self.run_case(group[0])
        else:
            self.start_process(self.list_transformation_queue(group))

        # 执行未分组用例
        if len(surplus_data) == 0:
            logger.info('未分组用例为空')
        elif (len(surplus_data) == 1 and len([j for i in surplus_data for j in i]) == 1) or start_data.PROCESS_NUM == 1:
            for i in surplus_data:
                self.run_case(i)
        else:
            for surplus in surplus_data:
                self.start_process(self.list_transformation_queue(surplus))
        if group_length == 0 and surplus_length == 0:
            logger.info("结束测试。。。。")
            return
        self.collect_reports()
        self.update_environment(constant.TMP_REPORT_DIR)

    def run_case(self, data):
        _uuid = str(uuid.uuid4())
        self.uuid_list.append(_uuid)
        run_case(data, _uuid, start_data.TEST_ENV)

    def start_process(self, group_queue):
        total = group_queue.qsize()
        pro_list = []
        while len(pro_list) != 0 or group_queue.qsize() != 0:
            for pro in pro_list:
                if pro.is_alive() is False:
                    name = pro.name
                    pro_list.remove(pro)
            if len(pro_list) < start_data.PROCESS_NUM and group_queue.qsize() > 0:
                try:
                    data = group_queue.get_nowait()
                    _uuid = str(uuid.uuid4())
                    self.uuid_list.append(_uuid)
                    logger.info("执行进度:{}/{}".format(group_queue.qsize(), total))
                    p = Process(target=run_case, args=(data, _uuid, start_data.TEST_ENV))
                    p.start()
                    p.name = _uuid
                    pro_list.append(p)
                except Exception:
                    logger.error(traceback.format_exc())
            time.sleep(2)

    def list_transformation_queue(self, _list) -> queue.Queue:
        _result = queue.Queue()
        for i in range(len(_list)):
            _result.put(_list[len(_list) - 1 - i])
        del _list
        return _result

    def get_group_data(self):
        group_data = []
        self.init_all_data()

        # 区分下渠道
        _all_data = {}
        for i in self.all_data:
            if i.get('tag') not in list(_all_data.keys()):
                _all_data[i.get('tag')] = []
            _all_data[i.get('tag')].append(i)

        for channel_data in list(_all_data.values()):
            channel_group_data = self.get_group_by_channel(copy.deepcopy(channel_data))
            group_data += channel_group_data

        surplus_data = self.get_surplus_data(copy.deepcopy(_all_data), copy.deepcopy(group_data))
        return group_data, surplus_data

    def get_group_by_channel(self, channel_data: list) -> list:
        """
        获取渠道的分组
        :param channel_data: 渠道数据
        :return:
        """
        group = []
        # dependent_list
        dependent_list = []
        for data in channel_data:
            if self.check_data(data):
                continue
            if data.get('dependent') is not None:
                dependent_list.append(data['dependent'])
        for data in channel_data:
            if self.check_data(data):
                continue
            if data.get('dependent') is not None and data.get('id') not in dependent_list:
                _data = self.get_dependent_data(data, channel_data)
                _data.reverse()
                group.append(_data)
        return group

    def check_data(self, data, is_file=True):
        # 调试时过滤
        if start_data.IS_DEBUG is True and 'debug' not in data.get('tags'):
            return True
        if data.get('__file') != start_data.TEST_CASE and start_data.TEST_CASE != 'all' and is_file is True:
            return True
        return False

    def get_surplus_data(self, all_data: dict, channel_group_data: list):
        surplus = {}
        for channel_data in list(all_data.values()):
            for data in channel_data:
                __file = data.get('__file')
                __func = data.get('__func')
                __dependent_class = data.get('__dependent_class')
                if self.check_data(data):
                    continue
                if data not in [j for i in channel_group_data for j in i]:
                    if __file not in list(surplus.keys()):
                        surplus[__file] = {}
                    if __func not in list(surplus[__file].keys()):
                        surplus[__file][__func] = []
                        surplus[__file]['__dependent_class'] = __dependent_class
                    surplus[__file][__func].append(data)
        surplus_data = list(surplus.items())
        sorted(surplus_data, key=cmp_to_key(self.compare))
        surplus_result = []
        for i in surplus_data:
            if '__dependent_class' in list(i[1].keys()): del i[1]['__dependent_class']
            new_i = list(i[1].items())
            new_i.sort()
            surplus_result += [j[1] for j in new_i]
        return surplus_result

    def collect_reports(self):
        for root, dirs, files in os.walk(constant.TMP_REPORTS_DIR):
            if os.path.basename(root) in self.uuid_list:
                for name in files:
                    _path = os.path.join(root, name)
                    if_copy = True
                    if name.endswith('result.json'):
                        _tmp = config.Json(_path)
                        # 过滤无数据用例
                        filter = "@pytest.mark.skip(reason='got empty parameter set ['data']"
                        labels = _tmp.get_key('labels')
                        for label in labels:
                            if label.get('name') == 'tag':
                                if label.get('value').startswith(filter):
                                    if_copy = False
                                    break
                        if if_copy is True:
                            # 删除防止参数显示太长导致用例标题显示过大
                            _tmp.put_key('parameters', [])
                            # 删除防止数据被当成重试用例
                            _tmp.remove_key('historyId')
                    if if_copy is True:
                        shutil.copyfile(_path, os.path.join(constant.TMP_REPORT_DIR, name))
        time.sleep(10)

    def compare(self, data1, data2):
        if data1[1].get('__dependent_class') == data2[0]:
            return 1
        return 0

    def get_dependent_data(self, data, all_data):
        """
        获取某个用例数据的依赖数据
        :param data:
        :param all_data:
        :return:
        """
        _data = [data]
        dependent = data.get('dependent')
        channel = data.get('tag')
        if channel is None:
            return _data
        if channel in list(self.all_data_by_channel_id.keys()) and \
            dependent in list(self.all_data_by_channel_id[channel].keys()):
            _dep = self.all_data_by_channel_id[channel].get(dependent)
            if _dep.get('dependent') is not None:
                _data += self.get_dependent_data(_dep, all_data)
            else:
                _data.append(_dep)
        return _data

    def init_all_data(self):
        """
        获取所有用例数据
        :return:
        """
        logger.info(self.data_folder)
        for root, dirs, files in os.walk(self.data_folder):
            for name in files:
                _path = os.path.join(root, name)
                if name.startswith('test_') is True and name.endswith('.json') is True:
                    _data = config.Json(_path).get_object()
                    if type(_data) != list or len(_data) == 0:
                        continue
                    if _data[0].get('__file') is None:
                        continue
                    __file = _data[0].get('__file')
                    __func = _data[0].get('__func')
                    __dependent_class = _data[0].get('__dependent_class')
                    if __func is None:
                        __func = 'default'

                    for i in _data[1:]:
                        i['__file'] = __file
                        i['__func'] = __func
                        i['__dependent_class'] = __dependent_class
                        tags = i.get('tags')
                        if tags is None:
                            continue

                        for tag in list(set(start_data.TEST_TAG).intersection(tags)):
                            if i.get('id') is None:
                                i['id'] = str(uuid.uuid4())
                            i['tag'] = tag
                            i['untag'] = 'psbc' if tag == 'antb' else 'antb'
                            if tag not in list(self.all_data_by_channel_id.keys()):
                                self.all_data_by_channel_id[tag] = {}
                            self.all_data_by_channel_id[tag][i['id']] = copy.deepcopy(i)
                            self.all_data.append(copy.deepcopy(i))
        self.replace_base_data()

    def replace_base_data(self):
        """
        替换继承数据
        :return:
        """
        _num = 0
        for i in range(len(self.all_data)):
            data = self.all_data[i]
            _base = data.get('__base')
            if _base is None:
                continue

            # 使base可继承别的渠道数据，继承顺序：优先本渠道-->其次其他渠道
            _base_data = {}
            for v in list(self.all_data_by_channel_id.values()):
                for k, j in v.items():
                    if k not in list(_base_data.keys()):
                        _base_data[k] = j
            channel = data.get('tag')
            _id = data.get('id')
            if channel in list(self.all_data_by_channel_id.keys()) and _base in list(self.all_data_by_channel_id[channel].keys()):
                data = self.merge_dict(copy.deepcopy(self.all_data_by_channel_id[channel][_base]), copy.deepcopy(data))
                del data['__base']
                self.all_data[i] = data
                self.all_data_by_channel_id[data['tag']][data.get('id')] = data
            elif _base in list(_base_data.keys()):
                data = self.merge_dict(copy.deepcopy(_base_data[_base]), copy.deepcopy(data))
                del data['__base']
                self.all_data[i] = data
                self.all_data_by_channel_id[data['tag']][data.get('id')] = data
            elif _base is not None:
                logger.info("数据对应base不存在:{}".format(_base))
                self.all_data[i] = {}
                _num += 1
                self.all_data_by_channel_id[data['tag']][data.get('id')] = data

        for i in range(_num):
            self.all_data.remove({})

    def merge_dict(self, _json1: dict, _json2: dict):
        for k in list(_json2.keys()):
            v = _json2[k]
            if type(v) != dict:
                _json1[k] = v
            elif type(v) == dict:
                _json1[k] = self.merge_dict(_json1[k], _json2[k])
        return _json1

    def check_and_create_by_dir(self, dir):
        if not os.path.exists(dir):
            logger.log("DEBUG", '创建目录:{}'.format(dir))
            logger.debug('创建目录:{}'.format(dir))
            os.makedirs(dir)

    def init_dir(self):
        if os.path.exists(constant.RUN_TMP_DIR):
            shutil.rmtree(constant.RUN_TMP_DIR)
        self.check_and_create_by_dir(constant.REPORT_DIR)
        self.check_and_create_by_dir(constant.RUN_TMP_DIR)
        if os.path.exists(constant.TMP_REPORT_DIR):
            shutil.rmtree(constant.TMP_REPORT_DIR)
        self.check_and_create_by_dir(constant.TMP_REPORT_DIR)
        self.check_and_create_by_dir(constant.TMP_REPORTS_DIR)

    def get_env(self):
        _list = []
        _list.append(['环境:', start_data.TEST_ENV])
        tags_name = ';'.join([start_data.TAG_LIST[i] for i in start_data.TEST_TAG])
        _list.append(['标签:', tags_name])
        _list.append(['执行用例:', start_data.TEST_CASE])
        _list.append(['并行数:', start_data.PROCESS_NUM])
        return _list

    def update_environment(self, result_tmp):
        environment = self.get_env()
        xml = config.AllureXml()
        xml.append_child(environment)
        xml.save_path(os.path.join(result_tmp, 'environment.xml'))

    def update_parameters(self, behaviors):
        if type(behaviors) == dict:
            if 'parameters' in list(behaviors.keys()):
                behaviors['parameters'] = []
            elif 'children' in list(behaviors.keys()):
                for i in range(len(behaviors['children'])):
                    self.update_parameters(behaviors['children'][i])

    def update_behaviors(self, report_tmp):
        try:
            behaviors_path = os.path.join(report_tmp, 'data', 'behaviors.json')
            behaviors_obj = config.Json(behaviors_path)
            self.update_parameters(behaviors_obj.get_object())
            behaviors_obj.save()
        except Exception as e:
            logger.error(traceback.format_exc())

    def get_result(self, allure_path):
        result_folder = os.path.join(constant.BASE_DIR, 'tmp_result')
        self.check_and_create_by_dir(result_folder)
        command = '{} generate {} -c -o {}'.format(allure_path, constant.TMP_REPORT_DIR, result_folder)
        os.system(command)
        result_path = os.path.join(result_folder, 'widgets', 'summary.json')
        _config = config.Json(result_path)
        statistic = _config.get('statistic')
        _time = _config.get('time')
        return statistic, _time

    def get_report(self, result_folder):
        """
        生成allure报告
        :param result_folder:报告地址文件名
        :return:
        """
        result_folder = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), result_folder)
        command = '{} generate {} -c -o {}'.format(constant.ALLURE_PATH, constant.TMP_REPORT_DIR, result_folder)
        logger.info(command)
        self.update_environment(constant.TMP_REPORT_DIR)
        logger.info(subprocess.call(command, shell=True))

    def send_report_by_dingtalk(self):
        ...

    def send_report_by_feishu(self, allure_path, access_token, secret, link, id=None):
        statistic, _time = self.get_result(allure_path)
        logger.error(statistic)
        logger.error(_time)
        created_at = self.unix_by_datetime(_time.get('start'))
        if id is not None:
            title = '接口测试报告(id:{})'.format(id)
        else:
            title = '接口测试报告'
        response = robot.Robot().execute_robot('feishu_report', access_token, secret, title, created_at,
                                               self.get_env(), {}, statistic, link)
        logger.info(response)

    def send_feishu(self, access_token, secret, title, text):
        response = robot.Robot().send_feishu(access_token, secret, title, text)
        logger.info(response)

    def unix_by_datetime(self, unix_time):
        return datetime.datetime.fromtimestamp(int(float(str(unix_time)[:10]))).strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    run = Run()
    run.run()
    run.get_report('allure')

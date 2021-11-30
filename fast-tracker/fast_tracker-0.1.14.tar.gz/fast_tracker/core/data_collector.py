# -*- coding: utf-8 -*-
"""
数据收集器并发送数据
"""

from __future__ import print_function

import logging
import os
import time
import datetime
import hashlib
import hmac


import fast_tracker.packages.six as six

import fast_tracker.packages.requests as requests


from fast_tracker.core.config import (global_settings, global_settings_dump, finalize_application_settings)
from fast_tracker.common.encoding_utils import  json_decode, json_encode
from fast_tracker.core.exception import FASTLogServerSTSException
from fast_tracker.packages.log import LogItem, LogClient, PutLogsRequest, LogException

_logger = logging.getLogger(__name__)


_audit_log_fp = None  # 计日志文件句柄
_audit_log_id = 0  # 审计日志文件的id,用来给日志文件命名


def _validate_fast_log_server_sts(response):
    """
    校验原始日志上报服务器的临时秘钥
    :param dict response:
    :return:
    """

    if not isinstance(response, dict):
        message = '获取FAST日志服务临时权限时返回值格式不正确,请联系FAST团队'
        logging.warning(message)
        raise FASTLogServerSTSException(message)
    data = response.get('data')
    if not isinstance(data, dict):
        message = '获取FAST日志服务临时权限时返回值格式不正确,请联系FAST团队'
        logging.warning(message)
        raise FASTLogServerSTSException(message)
    if not data.get('endpoint') or not data.get('project') or not data.get('logstore'):
        message = '获取FAST日志服务临时权限时返回值里缺少日志服务地址或仓库信息,请联系FAST团队'
        logging.warning(message)
        raise FASTLogServerSTSException(message)
    credentials = data.get('credentials')
    if not isinstance(credentials, dict) or not credentials.get('SecurityToken') or not credentials.get('AccessKeyId') \
            or not credentials.get('AccessKeySecret'):
        message = '获取FAST日志服务临时权限时权限秘钥格式不正确,请联系FAST团队'
        logging.warning(message)
        raise FASTLogServerSTSException(message)


def _apply_fast_log_server_sts(settings):
    """

    :param :
    :return:
    """
    api = settings.transport.token_server_endpoint
    product_code = settings.product_code
    app_code = settings.app_code
    timestamp = int(time.time())
    app_key = settings.app_key
    sig_str = 'app_code=%s&product_code=%s&timestamp=%d' % (app_code, product_code, timestamp)
    signature = hmac.new(app_key.encode(), sig_str.encode(), hashlib.sha1).hexdigest()
    sig_str += '&signature=%s' % signature
    api = '?'.join([api, sig_str])
    
    logging.debug('获取上报数据的秘钥接口:%s', api)
    try:
        response = requests.get(api)
        response = response.json()
    except Exception:
        message = '获取FAST日志服务临时权限失败,请联系FAST团队'
        logging.info(message)
        raise TypeError(message)
    _validate_fast_log_server_sts(response)
    return response['data']


def apply_host_credentials(settings):
    """
    申请秘钥
    :param settings:
    :return:
    """

    try:
        utc_format = '%Y-%m-%dT%H:%M:%SZ'
        expiration = datetime.datetime.strptime(settings.log_server.expiration, utc_format)
        now = datetime.datetime.utcnow()
        is_apply = not (expiration - now).total_seconds() > 60
    except:
        is_apply = True
    if is_apply:
        response = _apply_fast_log_server_sts(settings)
        settings.log_server.endpoint = response['endpoint']
        settings.log_server.project = response['project']
        settings.log_server.logstore = response['logstore']
        settings.log_server.security_token = response['credentials']['SecurityToken']
        settings.log_server.access_key_id = response['credentials']['AccessKeyId']
        settings.log_server.access_key_secret = response['credentials']['AccessKeySecret']
        settings.log_server.expiration = response['credentials']['Expiration']


def send_request(session, payload=[]):
    """
    :param session:
    :param list payload: [[(),()],[(),()]]
    :return:
    """
    settings = global_settings()
    apply_host_credentials(settings)
    if not session:
        session = requests.session()
    log_client = LogClient(request_session=session,
                           endpoint=settings.log_server.endpoint,
                           accessKeyId=settings.log_server.access_key_id,
                           accessKey=settings.log_server.access_key_secret,
                           securityToken=settings.log_server.security_token)
    log_items = [LogItem(contents=log) for log in payload]

    try:
        req = PutLogsRequest(settings.log_server.project, settings.log_server.logstore, topic=settings.app_name,
                             logitems=log_items)
        r = log_client.put_logs(req)
        content = r.body
    except LogException as ex:
        logging.exception('上报数据失败,错误信息:%r', str(ex))
        raise ex
    
    return content


class ApplicationSession(object):

    def __init__(self, configuration):
        """
        """
        self.configuration = configuration
        self._requests_session = None

    @property
    def requests_session(self):
        if self._requests_session is None:
            self._requests_session = requests.session()
        return self._requests_session

    def close_connection(self):
        if self._requests_session:
            self._requests_session.close()
        self._requests_session = None

    @property
    def max_payload_size_in_bytes(self):
        return self.configuration.max_payload_size_in_bytes

    @classmethod
    def send_request(cls, session, payload=[]):
        return send_request(session, payload)

    def shutdown_session(self):
        """关闭会话
        """
        return []

    def send_errors(self, errors):
        pass

    def send_transaction_traces(self, transaction_traces):
        pass

    def send_sql_traces(self, sql_traces):
        pass

    def send_transaction_events(self, sampling_info, sample_set):
        pass

    def send_error_events(self, sampling_info, error_data):
        pass

    def send_custom_events(self, sampling_info, custom_event_data):

        payload = (sampling_info, custom_event_data)

        return self.send_request(self.requests_session, payload)

    def send_span_events(self, sampling_info, span_event_data):
        """
        
        :param sampling_info: 
        :param span_event_data: [{}}
        :return: 
        """
        def items(event):
            data = event.items()
            for key, value in data:
                if not isinstance(value, str):
                    value = json_encode(value)
                yield (key, value)

        payload = [list(items(event)) for event in span_event_data if isinstance(event, dict)]

        return self.send_request(self.requests_session, payload)

    def finalize(self):
        pass

    @classmethod
    def create_session(cls, app_name, environment, settings):

        start = time.time()
        _logger.debug('连接数据收集器以注册代理,相关配置信息如下: app_name=%r,  environment=%r '
                      'and settings=%r.', app_name, environment, settings)
        application_config = finalize_application_settings()

        session = cls(application_config)
        duration = time.time() - start
        _logger.info('成功注册天眼Python代理: app_name=%r, pid=%r,  in %.2f seconds.', app_name, os.getpid(), duration)
        if getattr(application_config, 'high_security', False):
            _logger.info('代理与数据收集器直接的数据通信已经开启高安全模式,不会收集敏感信息')

        logger_func_mapping = {
                'ERROR': _logger.error,
                'WARN': _logger.warning,
                'INFO': _logger.info,
                'VERBOSE': _logger.debug,
            }

        if 'messages' in application_config:
            for item in application_config['messages']:
                message = item['message']
                if six.PY2 and hasattr(message, 'encode'):
                    message = message.encode('utf-8')
                level = item['level']
                logger_func = logger_func_mapping.get(level, None)
                if logger_func:
                    logger_func('%s', message)

        return session


class DeveloperModeSession(ApplicationSession):

    @classmethod
    def send_request(cls, session, payload=()):
        return ''

    def shutdown_session(self):
        """关闭会话
        """
        return []

    def send_errors(self, errors):
        return None

    def send_transaction_traces(self, transaction_traces):
        return None

    def send_sql_traces(self, sql_traces):
        return None

    def send_transaction_events(self, sampling_info, sample_set):
        return None

    def send_error_events(self, sampling_info, error_data):
        return None

    def send_custom_events(self, sampling_info, custom_event_data):
        return None

    def send_span_events(self, sampling_info, span_event_data):
        return None


def create_session(app_name, environment, settings):
    _global_settings = global_settings()

    if _global_settings.developer_mode:
        session = DeveloperModeSession.create_session(app_name, environment, settings)
    else:
        session = ApplicationSession.create_session(app_name, environment, settings)

    if session is None:
        return None

    application_settings = global_settings_dump(session.configuration)

    for key, value in list(six.iteritems(application_settings)):
        if not isinstance(key, six.string_types):
            del application_settings[key]

        if (not isinstance(value, six.string_types) and
                not isinstance(value, float) and
                not isinstance(value, six.integer_types)):
            application_settings[key] = repr(value)
    return session

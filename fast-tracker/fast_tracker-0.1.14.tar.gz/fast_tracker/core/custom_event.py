# -*- coding: utf-8 -*-
import logging
import re
import time

from fast_tracker.core.attribute import (check_name_is_string, check_name_length,
                                         process_user_attribute, NameIsNotStringException, NameTooLongException,
                                         MAX_NUM_USER_ATTRIBUTES)

_logger = logging.getLogger(__name__)

EVENT_TYPE_VALID_CHARS_REGEX = re.compile(r'^[a-zA-Z0-9:_ ]+$')


class NameInvalidCharactersException(Exception):
    pass


def check_event_type_valid_chars(name):
    regex = EVENT_TYPE_VALID_CHARS_REGEX
    if not regex.match(name):
        raise NameInvalidCharactersException()


def process_event_type(name):
    #  校验自定义事件类型名称是否合法
    FAILED_RESULT = None

    try:
        check_name_is_string(name)
        check_name_length(name)
        check_event_type_valid_chars(name)

    except NameIsNotStringException:
        _logger.debug('自定义事件名称必须是个字符串. 正在删除事件: %r', name)
        return FAILED_RESULT

    except NameTooLongException:
        _logger.debug('自定义事件名称超出最大长度,正在删除事件: %r', name)
        return FAILED_RESULT

    except NameInvalidCharactersException:
        _logger.debug('自定义事件名称含有不合法的字符,正在删除事件: %r', name)
        return FAILED_RESULT

    else:
        return name


def create_custom_event(event_type, params):
    """
    创建一个有效的自定义事件
    :param event_type: 自定义事件类型
    :param params: 自定义事件参数
    :return:
    """

    name = process_event_type(event_type)

    if name is None:
        return None

    attributes = {}

    try:
        for k, v in params.items():
            key, value = process_user_attribute(k, v)
            if key:
                if len(attributes) >= MAX_NUM_USER_ATTRIBUTES:
                    _logger.debug('事件 %r已经添加的参数数量达到继续,不能继续添加. 正在删除参数: %r=%r',
                                  name, key, value)
                else:
                    attributes[key] = value
    except Exception:
        _logger.debug('由于未知原因导致参数验证失败,检查回溯以获取详细信息 .正在删除参数: %r.', name,
                      exc_info=True)
        return None

    intrinsics = {
        'type': name,
        'timestamp': int(1000.0 * time.time()),
    }

    event = [intrinsics, attributes]
    return event

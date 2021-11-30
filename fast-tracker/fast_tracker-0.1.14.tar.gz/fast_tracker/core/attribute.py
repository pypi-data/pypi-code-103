# -*- coding: utf-8 -*-
import logging

from collections import namedtuple

from fast_tracker.packages import six

from fast_tracker.core.attribute_filter import (DST_ALL, DST_ERROR_COLLECTOR,
                                                DST_TRANSACTION_TRACER, DST_TRANSACTION_EVENTS, DST_SPAN_EVENTS,
                                                DST_TRANSACTION_SEGMENTS)

_logger = logging.getLogger(__name__)

_Attribute = namedtuple('_Attribute', ['name', 'value', 'destinations'])  # 三个字段对应的意思是:名称,值,位域目的地

_DESTINATIONS = (DST_ERROR_COLLECTOR |
                 DST_TRANSACTION_TRACER |
                 DST_TRANSACTION_SEGMENTS)
_DESTINATIONS_WITH_EVENTS = (_DESTINATIONS |
                             DST_TRANSACTION_EVENTS |
                             DST_SPAN_EVENTS)

#  事物事件默认的属性名称
_TRANSACTION_EVENT_DEFAULT_ATTRIBUTES = {'request.method', 'request.uri', 'response.status', 'http_method', 
                                         'http.statusCode', 'message.queueName', 'message.routingKey', 'http.url', 
                                         'status_code', 'db.instance', 'db.statement', 'error.class', 
                                         'error.message', 'peer.hostname', 'peer.address', 'request.headers.host'}

MAX_NUM_USER_ATTRIBUTES = 64  # 最大拥有属性的个数
MAX_ATTRIBUTE_LENGTH = 255  # 属性长度
MAX_64_BIT_INT = 2 ** 63 - 1


class NameTooLongException(Exception):
    #  名字太长
    pass


class NameIsNotStringException(Exception):
    #  名字不是字符串
    pass


class IntTooLargeException(Exception):
    #  整数太大
    pass


class CastingFailureException(Exception):
    pass


class Attribute(_Attribute):

    def __repr__(self):
        return "Attribute(name=%r, value=%r, destinations=%r)" % (
            self.name, self.value, bin(self.destinations))


def create_attributes(attr_dict, destinations, attribute_filter):
    #  创建属性,创建属性的时候会验证属性值的规则
    attributes = []
    for k, v in attr_dict.items():
        dest = attribute_filter.apply(k, destinations)
        attributes.append(Attribute(k, v, dest))
    return attributes


def create_agent_attributes(attr_dict, attribute_filter):
    attributes = []

    for k, v in attr_dict.items():
        if v is None:
            continue

        if k in _TRANSACTION_EVENT_DEFAULT_ATTRIBUTES:
            dest = attribute_filter.apply(k, _DESTINATIONS_WITH_EVENTS)
        else:
            dest = attribute_filter.apply(k, _DESTINATIONS)

        attributes.append(Attribute(k, v, dest))

    return attributes


def resolve_user_attributes(attr_dict, attribute_filter, target_destination):
    u_attrs = {}

    for attr_name, attr_value in attr_dict.items():
        if attr_value is None:
            continue

        dest = attribute_filter.apply(attr_name, DST_ALL)

        if dest & target_destination:
            u_attrs[attr_name] = attr_value

    return u_attrs


def resolve_agent_attributes(attr_dict, attribute_filter, target_destination):
    a_attrs = {}

    for attr_name, attr_value in attr_dict.items():
        if attr_value is None:
            continue

        if attr_name in _TRANSACTION_EVENT_DEFAULT_ATTRIBUTES:
            dest = attribute_filter.apply(attr_name, _DESTINATIONS_WITH_EVENTS)
        else:
            dest = attribute_filter.apply(attr_name, _DESTINATIONS)

        if dest & target_destination:
            a_attrs[attr_name] = attr_value

    return a_attrs


def create_user_attributes(attr_dict, attribute_filter):
    destinations = DST_ALL
    return create_attributes(attr_dict, destinations, attribute_filter)


def truncate(text, maxsize=MAX_ATTRIBUTE_LENGTH, encoding='utf-8', ending=None):
    # 对于超过长度的进行截断处理
    if isinstance(text, six.text_type):
        truncated = _truncate_unicode(text, maxsize, encoding)
    else:
        truncated = _truncate_bytes(text, maxsize)
        ending = ending and ending.encode(encoding)

    if ending and truncated != text:
        truncated = truncated[:-len(ending)] + ending

    return truncated


def _truncate_unicode(u, maxsize, encoding='utf-8'):
    encoded = u.encode(encoding)[:maxsize]
    return encoded.decode(encoding, 'ignore')


def _truncate_bytes(s, maxsize):
    return s[:maxsize]


def check_name_length(name, max_length=MAX_ATTRIBUTE_LENGTH, encoding='utf-8'):
    trunc_name = truncate(name, max_length, encoding)
    if name != trunc_name:
        raise NameTooLongException()


def check_name_is_string(name):
    # 检查名称是不是字符串
    if not isinstance(name, (six.text_type, six.binary_type)):
        raise NameIsNotStringException()


def check_max_int(value, max_int=MAX_64_BIT_INT):
    # 检查最大值
    if isinstance(value, six.integer_types) and value > max_int:
        raise IntTooLargeException()


def process_user_attribute(name, value, max_length=MAX_ATTRIBUTE_LENGTH, ending=None):
    # 校验配置里的属性名和值
    FAILED_RESULT = (None, None)

    try:
        check_name_is_string(name)
        check_name_length(name)
        check_max_int(value)

        value = sanitize(value)

    except NameIsNotStringException:
        _logger.debug('属性名必须是字符串,正在删除属性: %r=%r', name, value)
        return FAILED_RESULT

    except NameTooLongException:
        _logger.debug('属性名超过最大长度,正在删除属性: %r=%r', name, value)
        return FAILED_RESULT

    except IntTooLargeException:
        _logger.debug('属性值超过最大整数值,正在删除属性: %r=%r', name, value)
        return FAILED_RESULT

    except CastingFailureException:
        _logger.debug('属性值不能被转换成字符串,正在删除属性: %r=%r', name, value)
        return FAILED_RESULT

    else:
        valid_types_text = (six.text_type, six.binary_type)

        if isinstance(value, valid_types_text):
            trunc_value = truncate(value, maxsize=max_length, ending=ending)
            if value != trunc_value:
                _logger.debug('属性值有最大长度(%r字节). 正在截取值: %r=%r.', max_length, name, trunc_value)

            value = trunc_value
        return name, value


def sanitize(value):
    #  归一化数据，如果是支持的数据类型，直接返回原值，否则转换成字符串

    valid_value_types = (six.text_type, six.binary_type, bool, float,
                         six.integer_types)

    if not isinstance(value, valid_value_types):
        original = value

        try:
            value = str(value)
        except Exception:
            raise CastingFailureException()
        else:
            _logger.debug('属性值的类型是: %r. 不能将 %r 转换成字符串: %s', type(original), original, value)
    return value

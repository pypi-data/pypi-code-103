import asyncio
import datetime
import decimal
import traceback
import uuid
import warnings
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from functools import partial, reduce
from typing import Dict, List, Any, Callable, Union

import simplejson as json
from aio_pika import connect_robust, IncomingMessage, Exchange, Message, DeliveryMode, connect
from envparse import env
from vtb_http_interaction.keycloak_gateway import KeycloakConfig
from vtb_http_interaction.process_authorization_header import MemoryCache
from vtb_http_interaction.services import AuthorizationHttpService, HttpServiceWithRequestId
from vtb_py_logging.log_extra import log_extra
from vtb_py_logging.request_id import RequestId
from vtb_py_logging.utils import get_graph_logger

from state_service_utils.enums_client import enums
from .exceptions import StateServiceException
from .logging import create_logger

DEBUG = env.bool("DEBUG", default=False)
STATE_SERVICE_URL = env.str("STATE_SERVICE_URL", default=None)
STATE_SERVICE_TOKEN = env.str('STATE_SERVICE_TOKEN', default=None)
STATE_SERVICE_MOCK = env.bool('STATE_SERVICE_MOCK', default=False)

KEYCLOAK_SERVER_URL = env.str("KEY_CLOAK_SERVER_URL", default=None) or env.str("KEYCLOAK_SERVER_URL", default=None)
KEYCLOAK_REALM_NAME = env.str("KEY_CLOAK_REALM_NAME", default=None) or env.str("KEYCLOAK_REALM_NAME", default=None)
KEYCLOAK_CLIENT_ID = env.str("KEY_CLOAK_CLIENT_ID", default=None) or env.str("KEYCLOAK_CLIENT_ID", default=None)
KEYCLOAK_CLIENT_SECRET_KEY = env.str("KEY_CLOAK_CLIENT_SECRET_KEY", default=None) or env.str(
    "KEYCLOAK_CLIENT_SECRET_KEY", default=None)

KEYCLOAK_CONFIG = None
if KEYCLOAK_SERVER_URL and \
        KEYCLOAK_REALM_NAME and KEYCLOAK_CLIENT_ID and KEYCLOAK_CLIENT_SECRET_KEY:
    KEYCLOAK_CONFIG = KeycloakConfig(
        server_url=KEYCLOAK_SERVER_URL,
        client_id=KEYCLOAK_CLIENT_ID,
        realm_name=KEYCLOAK_REALM_NAME,
        client_secret_key=KEYCLOAK_CLIENT_SECRET_KEY
    )

LOG_FULL = 'full'
LOG_SHORT = 'short'

if not DEBUG and not (STATE_SERVICE_MOCK or STATE_SERVICE_TOKEN or KEYCLOAK_CONFIG):
    raise EnvironmentError(
        '`STATE_SERVICE_TOKEN` or `KEYCLOAK_CONFIG` is required when you`re not using `STATE_SERVICE_MOCK` or debug.')

if STATE_SERVICE_TOKEN:
    # TODO: Удалить класс в версии 2.0.0
    warnings.warn(
        'Поддержка переменной окружение STATE_SERVICE_TOKEN будет удалена в версии 1.7.0. \
Настройте интеграцию с keycloak, указав KEYCLOAK_SERVER_URL, \
KEYCLOAK_REALM_NAME, KEYCLOAK_CLIENT_ID и KEYCLOAK_CLIENT_SECRET_KEY.',
        DeprecationWarning, stacklevel=2)


@dataclass
class OrderAction:
    order_id: str
    action_id: str
    graph_id: str
    graph_version: str = ''


async def add_action_event(*, action: OrderAction, type, subtype, status='', data=None,
                           log_level=LOG_FULL):
    if not log_level:
        return

    request_data = {
        'type': type,
        'subtype': subtype,
        'status': status,
    }
    if log_level == LOG_FULL:
        request_data['data'] = data

    request_data.update(action.__dict__)
    await _make_request(
        url=f'{STATE_SERVICE_URL}/actions/',
        data=request_data
    )


async def add_event(*, action: OrderAction, item_id: str,
                    type, subtype, status='', data=None):
    """ Создание события в сервисе состояний """
    data = {
        'item_id': item_id,
        'type': type,
        'subtype': subtype,
        'status': status,
        'data': data
    }
    data.update(action.__dict__)
    await _make_request(
        url=f'{STATE_SERVICE_URL}/events/',
        data=data
    )


async def add_events(*, action: OrderAction, events: List[Dict]) -> Any:
    """ Создание списка событий в сервисе состояний одним запросом """
    data = {
        'events': events
    }
    data.update(action.__dict__)
    return await _make_request(
        url=f'{STATE_SERVICE_URL}/events/bulk-add-event/',
        data=data
    )


def state_action_decorator(is_add_call_kwargs: Union[bool, Callable] = True):
    def func_decorator(func):
        async def wrapper(*, order_action: OrderAction, node, action_type=enums.ActionDeploy.RUN_NODE.value,
                          task_logger, log_level=LOG_FULL, **kwargs):
            node_name = node if isinstance(node, str) else node.path
            await add_action_event(
                action=order_action,
                type=enums.ActionType.DEPLOY.value,
                subtype=action_type,
                status='%s:%s' % (node_name, enums.ActionStatus.STARTED.value),
                data=kwargs,
                log_level=log_level
            )
            try:
                if action_type not in enums.ActionDeploy._value2member_map_.keys():
                    raise StateServiceException(f'Invalid action type: {action_type}')
                if is_add_call_kwargs:
                    kwargs.update({
                        'order_action': order_action,
                        'action_type': action_type,
                        'task_logger': task_logger
                    })
                result = await func(
                    node=node,
                    **kwargs,
                )
                status = '%s:%s' % (node_name, enums.ActionStatus.COMPLETED.value)
            except Exception as e:
                tb = traceback.format_exc()
                result = {
                    'error': str(e),
                    'traceback': tb}
                status = '%s:%s' % (node_name, enums.ActionStatus.ERROR.value)
                task_logger.error(
                    f"Error in action ({status}): {tb}")
                log_level = LOG_FULL
            await add_action_event(
                action=order_action,
                type=enums.ActionType.DEPLOY.value,
                subtype=action_type,
                status=status,
                data=result,
                log_level=log_level
            )
            return result

        return wrapper

    if callable(is_add_call_kwargs):
        # it means that the decorator was called without its arguments, therefore we
        # are passing argument further to the func_decorator and assigning default argument value
        wrapped_func = is_add_call_kwargs
        is_add_call_kwargs = True
        return func_decorator(wrapped_func)
    else:
        # the decorator was called with arguments, hence we are returning the wrapper just as usual
        return func_decorator


class EventsReceiver:
    def __init__(self, fn, mq_addr, mq_input_queue, logger_name: str = ''):
        self.mq_addr = mq_addr
        self.input_queue = mq_input_queue
        self.fn = state_action_decorator()(fn)
        self.logger = create_logger(logger_name)

        self.connection = None
        self.channel = None
        self.queue = None

    async def on_message(self, message: IncomingMessage, exchange: Exchange):
        async with message.process():
            data = json.loads(message.body)

            if not isinstance(data, dict):
                raise StateServiceException('Invalid message (need struct): %s', data)

            order_action = OrderAction(
                order_id=data.pop('_order_id'),
                action_id=data.pop('_action_id'),
                graph_id=data.pop('_graph_id'))
            node = data['_name']
            action_type = data.get('_type')

            task_logger = get_graph_logger(logger=self.logger, order_action=order_action, node=node,
                                           action_type=action_type, orchestrator_id=data.get('_id'))

            request_id = message.headers.get("request_id")
            if not request_id:
                request_id = RequestId.make(prefix="ssu")

            with log_extra(request_id=request_id):
                response = await self.fn(
                    order_action=order_action,
                    node=node,
                    action_type=action_type,
                    task_logger=task_logger,
                    **data,
                )

            if not isinstance(response, str):
                response = json.dumps(response, default=default_encoder)

            await exchange.publish(
                Message(body=response.encode(), content_type="application/json",
                        correlation_id=message.correlation_id, delivery_mode=DeliveryMode.PERSISTENT),
                routing_key=message.reply_to,
            )

    async def _receive(self, loop, addr, queue_name, queue_kwargs, prefetch_count=None):
        self.connection = await connect_robust(addr, loop=loop)
        self.channel = await self.connection.channel()
        if prefetch_count:
            await self.channel.set_qos(prefetch_count=prefetch_count)
        self.queue = await self.channel.declare_queue(queue_name, **(queue_kwargs or {}), durable=True)
        await self.queue.consume(partial(self.on_message, exchange=self.channel.default_exchange))

    def run(self, queue_kwargs: dict = None, prefetch_count: int = None, loop=None):
        """ Запуск процесса прослушивания """
        loop = loop or asyncio.get_event_loop()

        task = loop.create_task(self._receive(
            loop, addr=self.mq_addr, queue_name=self.input_queue,
            queue_kwargs=queue_kwargs,
            prefetch_count=prefetch_count
        ))
        loop.run_until_complete(task)
        self.logger.info('Awaiting events')
        try:
            loop.run_forever()
        except (SystemExit, KeyboardInterrupt):
            self.logger.info('Sever stopped')

    async def close(self) -> None:
        """
        Закрытие подключения
        """
        if self.channel:
            await self.channel.close()

        if self.connection:
            await self.connection.close()


def items_from_events(events: List[dict], pre_ordered=False) -> list:
    """
        Получает список событий:
            - отсортированных в обратном порядке по времени создания и флагом 'pre_ordered' = True
            - или не сортированных, но имеющих поле со временем создания - 'create_dt'
        Возвращает список item:
            - с полем 'data', содержащим все уникальные ключи 'subtype'. С последними значениями 'subtype'
    """
    if not events:
        return []

    exclude = {'id', 'subtype', 'status', 'data', 'create_dt'}
    items_dict = {}

    if not pre_ordered:
        events = sorted(events, key=lambda x: x['create_dt'], reverse=True)

    for event in events:
        item_id = str(event['item_id'])
        items_dict.setdefault(item_id, {
            **{k: v for k, v in event.items() if k not in exclude},
            **{'data': {}, 'update_dt': event.get('create_dt')},
        })
        if event['subtype'] not in items_dict[item_id]['data']:
            items_dict[item_id]['data'][event['subtype']] = event.get('status') or event.get('data')

    return list(items_dict.values())


def default_encoder(obj):
    """ Default JSON encoder """
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()

    if isinstance(obj, (uuid.UUID, decimal.Decimal)):
        return str(obj)

    return obj


class UpdateTypeAction(Enum):
    """ Тип обновления конфигурации """
    UPDATE = "update"
    REPLACE = "replace"


def get_dict_value_by_path(obj: dict, path: Union[list, tuple]):
    """ Получение вложенного значения словаря по пути """
    return reduce(lambda t, i: t[i], path, obj)


def calculate_new_config_data(prev_data: Union[list, dict], updated_data: Union[list, dict], path: str,
                              action_type: UpdateTypeAction) -> Union[list, dict]:
    """ Расчет конфигурации с учетом новых данных """

    if action_type == UpdateTypeAction.UPDATE:
        new_data = deepcopy(prev_data)
        to_update: Union[list, dict] = get_dict_value_by_path(new_data, path.split(".")) if path else new_data
        if isinstance(updated_data, list):
            to_update.extend(updated_data)
        else:
            to_update.update(updated_data)

    elif action_type == UpdateTypeAction.REPLACE:
        if path == '':
            new_data = updated_data
        else:
            new_data = deepcopy(prev_data)
            target = path.split('.')
            to_update: Union[list, dict] = get_dict_value_by_path(new_data, target[:-1])
            to_update[target[-1]] = updated_data

    else:
        raise NotImplementedError(f'Unrecognized update type: {action_type}')

    return new_data


async def _make_create_with_drf_token(url, data: dict) -> Any:
    service = HttpServiceWithRequestId()
    request = {
        'method': "POST",
        'url': url,
        'cfg': {
            'timeout': 60,
            'json': data,
            'headers': {'Authorization': f'Token {STATE_SERVICE_TOKEN}'}
        }
    }
    status, response = await service.send_request(**request)
    if status == 400:
        raise StateServiceException(response)
    elif status != 201:
        raise StateServiceException(f'State service request error ({status}): {response}')

    return status, response


async def _make_create_with_keycloak_token(url, data: dict) -> Any:
    service = AuthorizationHttpService(KEYCLOAK_CONFIG, token_cache=MemoryCache())

    request = {
        'method': "POST",
        'url': url,
        'cfg': {
            'timeout': 60,
            'json': data
        }
    }
    status, response = await service.send_request(**request)

    if status == 400:
        raise StateServiceException(response)
    elif status != 201:
        raise StateServiceException(f'State service request error ({status}): {response}')

    return response


async def _make_request(url, data: dict) -> Any:
    if STATE_SERVICE_MOCK:
        return None, None

    if STATE_SERVICE_TOKEN:
        return await _make_create_with_drf_token(url, data)
    elif KEYCLOAK_CONFIG:
        return await _make_create_with_keycloak_token(url, data)

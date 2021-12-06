"""
Example of simple consumer that waits for a single message, acknowledges it
and exits.
"""
import logging
from pprint import pformat
from threading import Thread
from kombu import Connection, Consumer, Exchange, Queue, eventloop, Producer
from kombu.pools import producers
from amqp.exceptions import ConnectionForced

from ..file import read_yaml

logger = logging.getLogger(__name__)


# priority_to_routing_key = {
#     'high': 'hipri',
#     'mid': 'midpri',
#     'low': 'lopri',
# }


def pretty(obj):
    return pformat(obj, indent=4)


class Broker:
    queue_attrs = ['queue_arguments', 'binding_arguments', 'consumer_arguments', 'durable', 'exclusive', 'auto_delete',
                   'no_ack', 'alias', 'bindings', 'no_declare', 'expires', 'message_ttl', 'max_length',
                   'max_length_bytes', 'max_priority']

    exchange_attrs = ['arguments', 'durable', 'passive', 'auto_delete', 'delivery_mode', 'no_declare']

    def __init__(self, broker_ip='localhost', port=5672, username=None, password=None, queue=None, routing_key=None,
                 exchange=None, exchange_type=None, **kwargs):
        self.exchanges = {}
        self.queues = {}
        self.host = broker_ip
        self.port = port
        self.username = username
        self.password = password
        self.vhost = kwargs['vhost'] if 'vhost' in kwargs else '%2F'
        self.kwargs = kwargs
        if queue and routing_key and exchange_type and exchange:
            _exchange_attr = self._find_attr(self.exchange_attrs, self.kwargs)
            _queue_attr = self._find_attr(self.queue_attrs, self.kwargs)
            self.queue, self.exchange = self.add_conn(queue, routing_key, exchange_type, exchange, _queue_attr,
                                                      _exchange_attr)

        self._conn = None

    def load(self, config_dict=None, config_path=None, enforce=True):
        config = {}
        if config_path:
            try:
                config.update(read_yaml(config_path, 'MQCONFIG'))
            except Exception as e:
                logger.error(e, exc_info=True)
                return
        elif config_dict:
            config.update(config_dict)
        else:
            return

        exchanges = config.pop('exchange') if 'exchange' in config else {}
        queues = config.pop('queue') if 'queue' in config else {}

        if enforce:
            self.__dict__.update(config)
        else:
            self.__dict__.update((k, v) for k, v in config.items() if (k not in self.__dict__) or v)

        for exchange in exchanges:
            self.add_exchange(**exchange)
        for queue in queues:
            self.add_queue(**queue)

    def _check(self):
        if not self.host:
            raise ValueError("broker: invalid ip.")

        if not self.username:
            raise ValueError("broker: invalid user.")

        if not self.password:
            raise ValueError("broker: invalid passwd.")

    def _find_attr(self, keys: list, target: dict):
        res = {}
        for key in target:
            if key in keys:
                res[key] = target[key]
        return res

    @property
    def amqp(self):
        if self.host and self.username and self.password:
            return 'amqp://{}:{}@{}:{}/{}'.format(self.username, self.password, self.host, self.port, self.vhost)
        else:
            raise

    def connection(self):
        if not self._conn:
            self._check()
            self._conn = Connection(self.amqp, **self.kwargs)
        return self._conn

    def add_exchange(self, **kwarg):
        #: By default messages sent to exchanges are persistent (delivery_mode=2),
        #: and queues and exchanges are durable.
        _name = kwarg['name']
        _exchange = Exchange(**kwarg)
        self.exchanges[_name] = _exchange

    def add_queue(self, **kwarg):
        _name = kwarg['name']
        if kwarg['exchange'] in self.exchanges:
            kwarg['exchange'] = self.exchanges[kwarg['exchange']]
            _queue = Queue(**kwarg)
            self.queues[_name] = _queue
        else:
            logger.error('不存在 {} 这个exchange'.format(kwarg['exchange']))

    def add_conn(self, queue, routing_key, exchange_type, exchange, queue_attrs={}, exchange_attrs={}):
        _exchange = self.add_exchange(name=exchange, type=exchange_type, **exchange_attrs)
        _queue = self.add_queue(name=queue, exchange=exchange, routing_key=routing_key, **queue_attrs)
        self.exchanges[exchange] = _exchange
        self.queues[queue] = _queue
        return _queue, _exchange


class RabbitMQ:
    def __init__(self, broker, cb=None):
        self.broker = broker
        self.cb = cb if cb else self.handle_message
        self.is_running = False
        self.thread = None

    def run(self, queues=None, thread=True, **kwargs):
        res = []

        if not queues:
            res = [self.broker.queues[x] for x in self.broker.queues]
        else:
            if isinstance(queues, str):
                if queues in self.broker.queues:
                    res = [self.broker.queues[queues]]
                queues = [queues]
            for queue in set(queues):
                if queue not in self.broker.queues:
                    logger.error('no queue named {}'.format(queue))
                else:
                    res.append(self.broker.queues[queue])

        if res:
            if thread:
                self.thread = Thread(target=self._run_consumer, args=(res,), kwargs=kwargs)
                self.thread.start()
            else:
                self._run_consumer(res, **kwargs)
        else:
            logger.warning('no queue avaible, please check again!')
            return None

    @staticmethod
    def handle_message(body, message):
        #: This is the callback applied when a message is received.
        print(f'Received message: {body!r}')
        print(f'  properties:\n{pretty(message.properties)}')
        print(f'  delivery_info:\n{pretty(message.delivery_info)}')
        # finally should ack this message
        message.ack()

    def _run_consumer(self, queues, **kwargs):
        #: Create a connection and a channel.
        #: If hostname, userid, password and virtual_host is not specified
        #: the values below are the default, but listed here so it can
        #: be easily changed.
        timeout = kwargs.get('timeout') or 1
        ignore_timeouts = kwargs.get('ignore_timeouts') or True
        with self.broker.connection() as connection:
            with Consumer(connection, queues, callbacks=[self.cb], **kwargs):
                self.is_running = True
                logger.debug("mq is running at {}".format(self.broker.amqp))
                while self.is_running:
                    try:
                        # #: Each iteration waits for a single event.  Note that this
                        #         #: event may not be a message, or a message that is to be
                        #         #: delivered to the consumers channel, but any event received
                        #         #: on the connection.
                        for _ in eventloop(connection, timeout=timeout, ignore_timeouts=ignore_timeouts):
                            pass
                    except ConnectionForced:
                        self.is_running = False
                        logger.info('MQ Received a Force Close Commend: {}'.format(e))
                        break
                    except ConnectionResetError:
                        pass
                    except Exception as e:
                        self.is_running = False
                        logger.error('cb has some problem {}'.format(e), exc_info=True)
                        break

    def send_as_task(self, data, block=False, **kwargs):
        with producers[self.broker.connection()].acquire(block=block) as producer:
            producer.publish(data, **kwargs)

    # if __name__ == '__main__':
    #     broker = Broker()
    #     broker.load(config_path='some_file.yaml')
    #     mq = RabbitMQ(broker)
    #     mq.run(thread=False)
    #
    """
    demo some_file.yaml:
    MQCONFIG:
      host: 106.54.140.36
      port: 5672
      username: guest
      password: guest
      exchange:
        - name: message
          type: topic
          durable: false
        - name: asset.scanTaskTopic
          type: topic
          durable: true
      queue:
        - name: asset.scanTaskManage
          exchange: asset.scanTaskTopic
          routing_key: scanTaskManage
          durable: true
        - name: TEST01
          exchange: message
          routing_key: example.text
          durable: false
    
    """

from .queue0 import *
from .log import log_exception, log_info, log_task_schedule
from .utils import sleep, get_current_second


class RabbitConsumer2(RabbitConsumer0):

    def __init__(self, topic, label='rabbit', socket_timeout=300, heartbeat=30, config_info=None, no_ack=False,
                 retry_times=0, prefetch_count=1, schedule_module=None, schedule_task=None, schedule_period=3600 * 24,
                 schedule_interval=300):
        super(RabbitConsumer2, self).__init__(topic, label, socket_timeout, heartbeat, config_info)
        self.no_ack = no_ack
        self.retry_times = retry_times
        self.prefetch_count = prefetch_count
        self.schedule_task = schedule_task
        self.schedule_module = schedule_module
        self.schedule_period = schedule_period
        self.schedule_interval = schedule_interval
        if schedule_period < schedule_interval:
            self.schedule_interval = schedule_period / 2
        self.last_schedule_time = 0
        self.exception_handler = None

    def need_log_schedule(self):
        return self.schedule_task and self.schedule_module and self.schedule_period and self.schedule_interval

    def callback(self, ch, method, properties, body):
        self._caller(body)
        if not self.no_ack:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def execute_once(self, caller, no_ack=False):
        self._caller = caller
        self.no_ack = no_ack
        flag = self._execute_once()
        self.close_connection()
        return flag

    def do_log_schedule(self):
        if not self.need_log_schedule():
            return
        if get_current_second() - self.last_schedule_time > self.schedule_interval:
            log_task_schedule(self.schedule_task, self.schedule_period, self.schedule_module)
            self.last_schedule_time = get_current_second()

    def _execute_once(self):
        if not self._connection:
            self.check_connection()
            self._channel.queue_declare(queue=self._topic, durable=True)
            self._channel.basic_qos(prefetch_count=self.prefetch_count)
        mframe, hframe, body = self._channel.basic_get(queue=self._topic, no_ack=self.no_ack)
        if body is not None:
            retry_times = self.retry_times if self.retry_times > 0 else 10000000
            while retry_times >= 0:
                try:
                    self._caller(body.decode())
                    break
                except Exception as ex:
                    log_exception(ex)
                    if self.exception_handler:
                        self.exception_handler(ex)
                    sleep(2)
                    retry_times -= 1
            if not self.no_ack:
                self._channel.basic_ack(delivery_tag=mframe.delivery_tag)
        else:
            log_info("not get new queue message for {0}".format(self._topic))
            sleep(1)
        return body is not None

    def _consume_one(self):
        try:
            self._execute_once()
            self.do_log_schedule()
        except Exception as ex:
            log_info("rabbit except {0}".format(ex))
            self.close_connection()
            sleep(2)

    def consume_loop(self, caller, exception_handler=None):
        self._caller = caller
        self.exception_handler = exception_handler
        while True:
            self._consume_one()

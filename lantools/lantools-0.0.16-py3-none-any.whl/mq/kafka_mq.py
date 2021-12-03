from kafka import KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaTimeoutError
from .mq import Writer, Reader

class KafkaReader(Reader):
    def run(self, callback):
        consumer = KafkaConsumer(
            bootstrap_servers       = self.get_option('bootstrap_servers'),
            group_id                = self.get_option('group_id'),
            enable_auto_commit      = self.get_option('enable_auto_commit', True),
            auto_offset_reset       = self.get_option('auto_offset_reset', 'earliest'),
            max_poll_records        = self.get_option('max_poll_records', 500),
            max_poll_interval_ms    = self.get_option('max_poll_interval_ms', 300000)
        )

        '''auto_offset_reset
        earliest:表示分区下有已提交的offset时，从提交的offset开始消费；无提交的offset时，从头开始消费；
        latest:表示分区下有已提交的offset时，从提交的offset开始消费；无提交的offset时，消费新产生的该分区下的数据
        '''
        consumer.subscribe( self.get_option('topics') )

        for message in consumer:
            callback(message.value, handler=message, consumer=consumer)

class KafkaWriter(Writer):
    def __init__(self, *, bootstrap_servers, topic):
        self.topic = topic
        self.producer = KafkaProducer(bootstrap_servers = bootstrap_servers)

    def write(self, message, *, callback=None):
        def send_success(*args, **kwargs):
            if callback!=None:
                callback(is_success=True)

        def send_error(*args, **kwargs):
            if callback!=None:
                callback(is_success=False)

        try:
            self.producer.send(
                self.topic, 
                message
            ).add_callback(send_success).add_errback(send_error)
        except KafkaTimeoutError as k:
            print("发送超时", k)
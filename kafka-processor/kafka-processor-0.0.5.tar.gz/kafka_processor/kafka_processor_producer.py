from kafka.producer import KafkaProducer
from time import sleep
from kafka_processor import logger
from kafka_processor.metrics.producer_metrics import ProducerMetrics
from time import time


class KafkaProcessorProducer:
    """managing producer tasks for kafka processor"""
    def __init__(self, producer, producer_metrics):
        self._producer = producer
        self.producer_metrics = producer_metrics

    @classmethod
    def start(cls, **kafka_configs):
        """start a kafka producer instance"""
        logger.debug(f"starting producer with kafka configuration {kafka_configs}")
        producer = KafkaProducer(**kafka_configs)
        producer_metrics = ProducerMetrics(producer.metrics)

        return cls(producer, producer_metrics)

    def send(self, topic, key, value, is_blocking=True):
        """
        send a message to a given topic
        :param topic: destination topic
        :param key: message key, MUST by bytes or bytesarray
        :param value: message value, MUST by bytes or bytesarray
        :param is_blocking: wait until the messages is sent
        :return:  if run on non-blocking mode return the future for the send
        """

        logger.debug(
            f"sending (key: {key},value: {value}) to topic '{topic}' on "
            f"{'blocking' if is_blocking else 'non-blocking'} mode")

        self.producer_metrics.add_metric("last_message_sent", time())
        self.producer_metrics.add_metric("total_sent_message", 1)

        send_status = self._producer.send(topic, key, value)
        logger.debug(f"message key '{key}' was sent to topic '{topic}'")

        if is_blocking:
            while not send_status.is_done:
                sleep(0.1)
            logger.debug(f"message key '{key}' sent successfully")
        else:
            return send_status

    def stop(self):
        self.producer_metrics.stop()

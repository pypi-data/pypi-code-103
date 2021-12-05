from kafka_processor.kafka_processor_consumer import KafkaProcessorConsumer
from kafka_processor.kafka_processor_producer import KafkaProcessorProducer
from kafka_processor.processing_flow import ProcessingFlow
from time import sleep
import threading
from kafka_processor import logger
from kafka_processor.exceptions import FailToProcessMessage


class KafkaProcessor:
    def __init__(self, consumer, producer, polling_interval):
        self.producer = producer
        self.consumer = consumer
        self._polling_interval = polling_interval
        self._flows = {}
        self._thread = None
        self._is_started = False

    @classmethod
    def start(cls, kafka_group_id, polling_interval=5, **kafka_configs):
        """
        start kafka processor instance
        :param kafka_group_id: consumer group id
        :param polling_interval: how often query kafka for records, number in seconds
        :param kafka_configs: kafka configuration follow
                        https://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html#kafka.KafkaConsumer

        :return: KafkaProcessor instance
        """

        logger.info("starting kafka processor")

        logger.info("creating kafka consumer")
        logger.debug(f"initializing consumer with group id '{kafka_group_id}' and kafka config '{kafka_configs}'")
        consumer = KafkaProcessorConsumer.start(group_id=kafka_group_id, **kafka_configs)

        logger.info("creating kafka producer")
        logger.debug(f"initializing producer with kafka config '{kafka_configs}'")
        producer = KafkaProcessorProducer.start(**kafka_configs)

        logger.info("creating processor instance")
        instance = cls(consumer, producer, polling_interval)

        instance._thread = threading.Thread(target=instance._work, name="KafkaProcessor")

        logger.info("starting processor worker")
        instance._is_started = True
        instance._thread.start()

        return instance

    def add_flow(self, input_topic, output_topic, callbacks, messages_filter=None):
        """
        add a flow to the current kafka processor
        :param input_topic:  source topic name
        :param output_topic: result topic name, will store the result of the process
        :param callbacks: list of function to run on the incoming list
        :param messages_filter: filtering function to run on the collected records,
                                filtered record will not be processed
        :return: None
        """

        logger.info(f"adding flow from topic '{input_topic}' to topic '{output_topic}'")

        callbacks_info = [getattr(callback, "__name__", callback) for callback in callbacks]
        filter_info = getattr(messages_filter, "__name__", messages_filter)

        msg_output_topic = output_topic if output_topic else "terminated flow"

        logger.debug(
            f"input_topic: {input_topic}, output_topic:{msg_output_topic}, "
            f"callbacks: {callbacks_info}, messages_filter : '{filter_info}'")

        self._flows[input_topic] = ProcessingFlow(input_topic, output_topic, callbacks, messages_filter)
        self.consumer.follow_topic(input_topic)

        logger.info(f"flow '{input_topic}' added successfully")

    def remove_flow(self, topic):
        """
        remove a flow from kafka processor
        :param topic: source topic name
        :return: None
        """

        logger.info(f"stop flow {topic}")

        self.consumer.unfollow_topic(topic)
        del self._flows[topic]

        logger.info(f"flow '{topic}' removed successfully")

    def _work(self):
        """
        getting the messages and process them
        :return:
        """

        logger.debug("start polling messages from kafka")

        while self._is_started:
            try:
                # get a bunch of messages
                for topic, messages in self.consumer.read().items():
                    # filter messages with the filtering function,
                    # if not supplied then all the records will be processed
                    failed_idx, processed_messages = self._flows[topic].filter(messages)

                    # check if filtering finished with success
                    if failed_idx == -1:
                        logger.debug(
                            f"{len(messages)} messages received for topic {topic}, "
                            f"process {len(processed_messages)} messages after filtering"
                        )
                        commit_info = (messages[-1].offset, messages[-1].topic, messages[-1].partition)
                    else:
                        logger.warning(
                            f"due to exception in the filter function only {failed_idx + 1} items was scanned")
                        commit_info = (messages[failed_idx].offset, messages[failed_idx].topic,
                                       messages[failed_idx].partition)

                    # processing messages
                    for msg in processed_messages:
                        result_key, result_value = self._flows[topic].evaluate_callbacks(msg)

                        if self._flows[topic].output_topic:
                            self.producer.send(self._flows[topic].output_topic, result_key, result_value)

                        self.consumer.commit(msg.offset, msg.topic, msg.partition)

                    # final commit according to the filter state, use to skip filtered and broken messages
                    self.consumer.commit(*commit_info)

            except FailToProcessMessage as ex:
                logger.exception(f"fail to process messages for flow '{topic}'")
                self.consumer.commit(ex.record.offset, ex.record.topic, ex.record.partition)

            logger.debug(f"waiting for {self._polling_interval} seconds before polling again")
            sleep(self._polling_interval)
        logger.info("processor worker was terminated")

    def stop(self):
        """
        stop kafka processor
        :return: None
        """

        logger.info("stopping processor")
        self._is_started = False
        self.consumer.stop()
        self.producer.stop()


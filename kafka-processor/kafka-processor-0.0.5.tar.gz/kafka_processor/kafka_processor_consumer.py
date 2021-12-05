from kafka.consumer.group import KafkaConsumer
from kafka.structs import OffsetAndMetadata, TopicPartition
from itertools import chain
from kafka_processor import logger
from kafka_processor.metrics.consumer_metrics import ConsumerMetrics
from time import time


class KafkaProcessorConsumer:
    """handling kafka processor read and commit tasks"""
    def __init__(self, consumer, consumer_metrics):
        self._consumer = consumer
        self._topics = set()
        self.consumer_metrics = consumer_metrics

    @classmethod
    def start(cls, group_id, **kafka_configs):
        """
        starting a consumer instance
        :param group_id: kafka group id to use as a consumer
        :param kafka_configs: kafka configuration follow
                        https://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html#kafka.KafkaConsumer
        :return: KafkaConsumer instance
        """

        logger.info(f"starting consumer with group id {group_id} and kafka configuration {kafka_configs}")

        kafka_consumer = KafkaConsumer(
            group_id=group_id, enable_auto_commit=kafka_configs.get("enable_auto_commit", False), **kafka_configs)
        consumer_metrics = ConsumerMetrics(kafka_consumer.metrics)

        return cls(kafka_consumer, consumer_metrics)

    def follow_topic(self, topic):
        """
        start following a new topic
        :param topic: topic name
        :return: None
        """

        logger.info(f"start following topic '{topic}'")

        if topic not in self._consumer.topics():
            logger.warning(f"topic '{topic}' not found on cluster {self._consumer.config.get('bootstrap_servers')}")

        self._topics.add(topic)
        logger.debug(f"followed topics list: {self._topics}")
        self._consumer.subscribe(self._topics)
        logger.info(f"topic '{topic}' added successfully to following list")

    def unfollow_topic(self, topic):
        """
        stop following topic
        :param topic: topic name
        :return: None
        """

        logger.info(f"stop following topic {topic}")
        self._topics.discard(topic)
        logger.debug(f"followed topics list: {self._topics}")
        self._consumer.subscribe(self._topics)

    def read(self, timeout=10):
        """
        read messages from all followed topics and flattening result to dict with key of topic name ana value
        of messages list
        :param timeout: time in seconds to wait for poll results
        :return: dict with key of topic name ana value of messages list
        """

        logger.debug(f"reading messages from kafka, timeout set to {timeout} seconds")
        self.consumer_metrics.add_metric("last_poll_time", time())
        results = self._consumer.poll(timeout)

        ans = {}

        # flattening result to map with topic name and value of messages list
        before_get_messages = self.consumer_metrics.get_metric("total_message_polled").get()["value"]
        for topic_partition, messages in results.items():
            self.consumer_metrics.add_metric("total_message_polled", len(messages))
            if topic_partition.topic not in ans:
                ans[topic_partition.topic] = [messages]
            else:
                ans[topic_partition.topic].append(messages)

        after_get_messages = self.consumer_metrics.get_metric("total_message_polled").get()["value"]
        self.consumer_metrics.add_metric("last_poll_message_count", after_get_messages - before_get_messages)

        # since in the previous step the value set to list of list, not it chained to a single big list
        for topic, messages in ans.items():
            ans[topic] = sorted(list(chain(*messages)), key=lambda item: item.timestamp)

        msgs_count = [(topic, len(messages)) for topic, messages in ans.items()]
        logger.debug(f"messages found for topic, {msgs_count}")

        return ans

    def commit(self, offset, topic, partition):
        """
        commit an offset on a give topic and partition, and make sure that the position is set correctly
        :param offset: offset in the given topic partition
        :param topic: topic name
        :param partition: partition id
        :return: None
        """

        meta = OffsetAndMetadata(offset, set([topic]))
        topic_partition = TopicPartition(topic, partition)

        committed_offset = self._consumer.committed(topic_partition)
        committed_offset = committed_offset if committed_offset is not None else 0

        if committed_offset < offset:
            logger.debug(f"commit message at partition {topic_partition} with offset {offset}")
            self._consumer.commit({topic_partition: meta})

            if self._consumer.committed(topic_partition) + 1 != self._consumer.position(topic_partition):
                self._consumer.seek(topic_partition, offset+1)

    def stop(self):
        self.consumer_metrics.stop()

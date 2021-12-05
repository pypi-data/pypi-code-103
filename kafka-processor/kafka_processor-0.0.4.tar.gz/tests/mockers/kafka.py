from unittest.mock import MagicMock
from collections import namedtuple
from time import time
from tests.mockers.mocked_future import MockedFuture
from collections import defaultdict

TopicPartition = namedtuple("TopicPartition", ["topic", "partition"])
KafkaRecord = namedtuple("KafkaRecord", ["key", "value", "timestamp", "offset", "topic", "partition"])


class MockedKafka(MagicMock):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.subscribed = []
        self._commit_by_topic_partition = {}
        self._position_by_topic_partition = {}
        self._messages_by_topic_partition = {}
        self.sent_messages = defaultdict(list)
        self.last_sent_topic = None
        self.last_sent_message = None
        self.send_called = 0

    def set_messages_to_topic(self, topic, partition, messages_list):

        messages_list = [KafkaRecord(
            item, item, time(), idx, topic, partition) for idx, item in enumerate(messages_list)]

        self._messages_by_topic_partition[TopicPartition(topic, partition)] = messages_list
        self._commit_by_topic_partition[TopicPartition(topic, partition)] = 0
        self._position_by_topic_partition[TopicPartition(topic, partition)] = 0

    def poll(self, timeout=0):
        result = {}

        for topic_partition in self._messages_by_topic_partition:
            if len(self._messages_by_topic_partition[topic_partition]) > 0:
                result[topic_partition] = (
                    self._messages_by_topic_partition[topic_partition][
                        self._position_by_topic_partition[topic_partition]:])

                self._position_by_topic_partition[topic_partition] = len(
                    self._messages_by_topic_partition[topic_partition])

        return result

    def commit(self, commit_info):
        for topic_partition, metadata in commit_info.items():
            self._commit_by_topic_partition[topic_partition] = metadata.offset

    def committed(self, topic_partition):
        return self._commit_by_topic_partition[topic_partition]

    def position(self, topic_partition):
        return self._position_by_topic_partition[topic_partition]

    def seek(self, topic_partition, offset):
        self._position_by_topic_partition[topic_partition] = offset

    def topics(self):
        return ["test_topic"]

    def subscribe(self, topic):
        self.subscribed = topic

    def get_topic_partition(self, topic, partition):
        return TopicPartition(topic, partition)

    def send(self, topic, key, value):

        self.sent_messages[topic].append((key, value))
        self.last_sent_topic = topic
        self.last_sent_message = (key, value)
        self.send_called += 1

        return MockedFuture()

from uuid import uuid4
from ..utilities.helpers import current_datetime
from ..utilities.transformer import transform_to_dict
import json
import datetime


class Message():
    def __init__(self, topic: str, published_time: str, content_format: str, content: str or dict or list,
                 consumed_time: str = None, uuid: str = None) -> None:
        self.__uuid = uuid4().hex if uuid is None else uuid
        self.__is_consumed = False
        self.__topic = topic
        self.__published_time = published_time
        self.__content_format = content_format
        self.__content = transform_to_dict(content, content_format)
        self.__consumed_time = consumed_time

    def __str__(self):
        return str(self.__dict__)

    @property
    def uuid(self):
        return self.__uuid

    @property
    def topic(self):
        return self.__topic

    @property
    def is_consumed(self):
        return self.__is_consumed

    @is_consumed.setter
    def is_consumed(self, is_consumed):
        self.__is_consumed = is_consumed

    @property
    def content(self):
        return self.__content

    @content.setter
    def content(self, content):
        self.__content = content

    @property
    def consumed_time(self):
        return self.__consumed_time

    @consumed_time.setter
    def consumed_time(self, consumed_time):
        self.__consumed_time = consumed_time

    def get_publish_message(self):
        return {
            'uuid':  self.__uuid,
            'topic': self.__topic,
            'content_format': self.__content_format,
            'content': self.__content
        }

    def get_log_message(self):

        return {
            'uuid':  self.__uuid,
            'is_consumed': self.__is_consumed,
            'topic': self.__topic,
            'published_time': str(self.__published_time),
            'content_format': self.__content_format,
            'content': json.dumps(self.__content),
            'consumed_time': self.consumed_time if self.consumed_time == None else str(self.consumed_time)
        }

from dataclasses import dataclass
from typing import List, Any, Set, Dict


@dataclass
class CanMessage:
    timestamp: float
    msg_id: int
    data: bytearray
    is_extended_id: bool


@dataclass
class ParsedCanMessage:
    nodeid: int
    signals: List[str]
    data: List[Any]
    formatted_data: List[str]


class CanMessageCollection:

    def __init__(self, existing_messages=None):
        self.messages = [] if existing_messages is None else existing_messages

    def add_or_update(self, message: CanMessage):
        for i, data in enumerate(self.messages):
            if data.msg_id == message.msg_id:
                self.messages[i] = message
                break
        else:
            self.messages.append(message)

    def clear(self, msg_ids=None):
        if msg_ids is None:
            # clear all
            self.messages = []
        else:
            self.messages = [message for message in self.messages if message.msg_id not in msg_ids]

    def filter(self, predicate):
        return CanMessageCollection([message for message in self.messages if predicate(message.msg_id)])

    @property
    def sorted_by_id(self) -> List[CanMessage]:
        return sorted(self.messages, key=lambda x: x.msg_id)

    @property
    def sorted_by_time(self) -> List[CanMessage]:
        return sorted(self.messages, key=lambda x: x.timestamp)

    def get_timing_info(self) -> int:
        if len(self.messages) == 0:
            return 0, 0, 0
        msgs = self.sorted_by_time
        first = msgs[0].timestamp
        last = msgs[-1].timestamp
        return first, last, int((last - first) * 1e6)

    @property
    def ids(self) -> List[int]:
        return set(i.msg_id for i in self.messages)

    def __len__(self):
        return len(self.messages)


class ProcessedCanDataBlock:

    def __init__(self, timestamp, reception_window_us):
        self.timestamp = timestamp
        self.reception_window_us = reception_window_us
        self.items = []

    def add(self, item: ParsedCanMessage):
        self.items.append(item)

    def get_nodeids(self) -> Set[int]:
        return {d.nodeid for d in self.items}  # removes duplicates by returning a set

    def get_messages_for_nodeid(self, nodeid: int) -> List[ParsedCanMessage]:
        return [d for d in self.items]

    def has_signal(self, nodeid: int, signal_name: str):
        try:
            self.get_message(nodeid, signal_name)
            return True
        except StopIteration:
            return False

    def get_message(self, nodeid: int, signal_name: str):
        return next(d for d in self.items if d.nodeid == nodeid and signal_name in d.signals)

    def get_messages(self) -> List[ParsedCanMessage]:
        """Returns a list of messages contained in one CAN epoch.
        """
        return self.items

    def __str__(self):
        return f'{self.timestamp} {self.reception_window_us} {self.items}'

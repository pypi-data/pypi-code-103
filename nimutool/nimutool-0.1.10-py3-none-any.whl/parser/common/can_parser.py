from nimutool.canbus.can_message import ProcessedCanDataBlock, CanMessageCollection, ParsedCanMessage, CanMessage
from typing import List


def get_all_subclasses(cls):
    all_subclasses = []
    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))
    return all_subclasses


class CanParserBase:

    def __init__(self):
        self.handlers = {hldr.canid: hldr() for hldr in self.MSG_HANDLERS}
        self.synced_frames = [can_id for can_id, handler in self.handlers.items() if handler.frequency == 1]
        self.latched_frames = [can_id for can_id, handler in self.handlers.items() if handler.frequency != 1]

    def on_datacollection_ready(self, data_collection: CanMessageCollection) -> ProcessedCanDataBlock:
        synced_collection = data_collection.filter(lambda x: self.canid2dataid(x) in self.get_synchronized_frames())
        first, _, window_us = synced_collection.get_timing_info()
        processed_block = ProcessedCanDataBlock(first, window_us)
        for message in data_collection.sorted_by_id:
            processed_item = self.process_message(message, data_collection)
            if processed_item:
                processed_block.add(processed_item)
        return processed_block

    def process_message(self, message: CanMessage, data_collection: CanMessageCollection) -> ParsedCanMessage:
        data_id, node_id = self.split_canid_to_msgid_and_nodeid(message.msg_id)
        handler = self.handlers[data_id]
        parsed_message = handler.parse(message.data)
        if parsed_message:
            parsed_message.nodeid = node_id
        return parsed_message

    def canid2dataid(self, can_id):
        return can_id

    def split_canid_to_msgid_and_nodeid(self, can_id):
        return can_id, None

    def get_highest_priority_frame(self, set_of_canids):
        highest_prio_canid = -1
        highest_prio = 999
        for canid in set_of_canids:
            dataid = self.canid2dataid(canid)
            prio = self.handlers[dataid].priority
            if prio < highest_prio:
                highest_prio = prio
                highest_prio_canid = canid
        return highest_prio_canid

    def get_synchronized_frames(self) -> List[int]:
        return self.synced_frames

    def get_latched_frames(self) -> List[int]:
        return self.latched_frames

    def is_synchronized_frame(self, can_id: int):
        data_id = self.canid2dataid(can_id)
        return self.handlers[data_id].frequency == 1

    def is_supported(self, message: CanMessage):
        data_id = self.canid2dataid(message.msg_id)
        return data_id in self.handlers and self.handlers[data_id].extended == message.is_extended_id

    def get_msg_name(self, can_id):
        data_id = self.canid2dataid(can_id)
        return self.handlers[data_id].__class__.__name__

    def contains_sync(self, can_ids: List[int]):
        return False

    def is_sync(self, can_id: int):
        return False

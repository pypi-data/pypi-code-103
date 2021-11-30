from nimutool.canbus.can_message import CanMessage, CanMessageCollection, ProcessedCanDataBlock


class BusTimingMonitor:

    def __init__(self):
        self.first_received_timestamp = 0
        self.start_of_monitoring_period = 0
        self.count = 0
        self.events_per_sec = 0
        self.events_per_sec_accumulator = 0

    def add_event(self, timestamp: float):
        if self.first_received_timestamp == 0:
            self.first_received_timestamp = timestamp
            self.start_of_monitoring_period = int(timestamp)
        self.count += 1
        if int(timestamp) == self.start_of_monitoring_period:
            self.events_per_sec_accumulator += 1
        else:
            self.events_per_sec = self.events_per_sec_accumulator
            self.events_per_sec_accumulator = 1
            self.start_of_monitoring_period = int(timestamp)


class BusSynchronizer:

    def __init__(self, wait_period_sec, processor, latch_unsynchronized=False):
        self.data = CanMessageCollection()
        self.wait_period_sec = wait_period_sec
        self.synchronized_ids = set()
        self.state_handler = self._state_waiting_initial_ids
        self.processor = processor
        self.msg_monitor = BusTimingMonitor()
        self.latch = latch_unsynchronized
        self.previous_collection = None
        print('Studying bus traffic')

    def __housekeep_buffers(self):
        if self.latch:
            # conditionally clear buffer to preserve frames which are not present on every can epoch
            frames_to_drop = [msg_id for msg_id in self.data.ids if self.processor.is_synchronized_frame(msg_id)]
            self.data.clear(frames_to_drop)
        else:
            # otherwise clear everything
            self.data.clear()

    def __update_buffers_and_check_for_completeness(self, message):
        full_collection = None
        # check for missing messages by inspecting sync messages
        if self.processor.is_sync(message.msg_id) and self.previous_collection and self.processor.contains_sync(self.data.ids):
            newest = self.data.sorted_by_time[-1].timestamp
            print(f't={message.timestamp} imputing message ids: {self.previous_collection.ids - self.data.ids}')
            for m in self.previous_collection.messages:
                m.timestamp = newest
            for m in self.data.messages:
                self.previous_collection.add_or_update(m)
            self.__housekeep_buffers()
            self.data.add_or_update(message)
            return self.previous_collection
        self.data.add_or_update(message)
        if self.data.ids >= self.synchronized_ids:
            full_collection = CanMessageCollection(self.data.messages)
            self.previous_collection = full_collection
            self.__housekeep_buffers()
        return full_collection

    def _state_waiting_initial_ids(self, message: CanMessage):
        self.msg_monitor.add_event(message.timestamp)
        if self.processor.is_supported(message):
            self.data.add_or_update(message)
        first, last, _ = self.data.get_timing_info()
        if last - self.msg_monitor.first_received_timestamp > self.wait_period_sec:
            self.synchronized_ids = self.data.ids
            self.data.clear(self.processor.get_synchronized_frames())
            self.state_handler = self._state_waiting_sync

    def _state_waiting_sync(self, message: CanMessage):
        if message.msg_id == self.processor.get_highest_priority_frame(self.synchronized_ids):
            self.state_handler = self._state_waiting_data
            self.data.clear()
            self.state_handler(message)
            hexids = [f'0x{can_id:03x} ({self.processor.get_msg_name(can_id)})' for can_id in sorted(self.synchronized_ids)]
            print(f'Found CAN messages: {", ".join(hexids)}')

    def _state_waiting_data(self, message: CanMessage) -> ProcessedCanDataBlock:
        full_collection = self.__update_buffers_and_check_for_completeness(message)
        if full_collection:
            # print(full_collection.ids, self.processor.get_synchronized_frames())
            processed_block = self.processor.on_datacollection_ready(full_collection)
            return processed_block

    def synchronize(self, message: CanMessage) -> ProcessedCanDataBlock:
        if self.processor.is_supported(message):
            return self.state_handler(message)

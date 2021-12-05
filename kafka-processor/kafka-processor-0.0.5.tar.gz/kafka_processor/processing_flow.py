from kafka_processor.exceptions import FailToProcessMessage
from kafka_processor import logger
from kafka_processor.enhanced_list import EnhancedList


class ProcessingFlow:
    def __init__(self, input_topic, output_topic, callbacks, messages_filter=None):
        self.input_topic = input_topic
        self.output_topic = output_topic
        self.filter_function = messages_filter
        self.callbacks = callbacks

    def filter(self, collection):
        """
        filter a given collection using flow's filtering function,
        return the index of the function fail if failed, and filtered collection
        :param collection: list of items to filter
        :return: failed index, filtered collection
        """

        failed_idx = -1

        try:
            collection = EnhancedList(collection)
            collection = self.filter_function(collection) if self.filter_function is not None else collection
        except Exception:
            logger.exception(f"fail to filter collection using '{self.filter_function.__name__}'")
            failed_idx = collection.last_accessed_index
            collection = self.filter_function(collection[:failed_idx])
        finally:
            return failed_idx, collection

    def evaluate_callbacks(self, record):
        """
        run all the flow callbacks on a given record
        :param record: message from kafka
        :return: the result of the last function
        """

        try:
            curr_key, curr_value = record.key, record.value

            for callback in self.callbacks:
                curr_key, curr_value = callback(curr_key, curr_value)

            return curr_key, curr_value
        except Exception as ex:
            raise FailToProcessMessage(record, ex)

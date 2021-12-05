class FailToProcessMessage(Exception):
    """
    exception for processing message error
    """
    def __init__(self, record, ex):
        super().__init__(f"fail to process message for topic {record.topic}")
        self.record = record
        self.ex = ex


class UnExpectedMetricAccessed(Exception):
    pass


class UnExpectedMetricType(Exception):
    pass

from kafka_processor.metrics.kafka_processor_metrics import KafkaProcessorMetrics
from kafka_processor.metrics.metrics_types import MetricsType


class ConsumerMetrics(KafkaProcessorMetrics):
    def __init__(self, client_metrics_function):
        super(ConsumerMetrics, self).__init__(client_metrics_function)
        self.create_metric("total_message_polled", MetricsType.COUNTER)
        self.create_metric("last_poll_time", MetricsType.GAUGES)
        self.create_metric("last_poll_message_count", MetricsType.GAUGES)

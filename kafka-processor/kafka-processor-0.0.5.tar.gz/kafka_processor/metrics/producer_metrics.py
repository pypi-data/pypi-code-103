from kafka_processor.metrics.kafka_processor_metrics import KafkaProcessorMetrics
from kafka_processor.metrics.metrics_types import MetricsType


class ProducerMetrics(KafkaProcessorMetrics):
    def __init__(self, client_metrics_function):
        super(ProducerMetrics, self).__init__(client_metrics_function)
        self.create_metric("total_sent_message", MetricsType.COUNTER)
        self.create_metric("last_message_sent", MetricsType.GAUGES)

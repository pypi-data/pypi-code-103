from appmetrics import metrics
from appmetrics.exceptions import DuplicateMetricError
from kafka_processor import logger
from kafka_processor.metrics.metrics_types import MetricsType
from kafka_processor.exceptions import UnExpectedMetricAccessed, UnExpectedMetricType


class KafkaProcessorMetrics:
    def __init__(self, client_metrics_function):
        self._client_metrics = client_metrics_function
        self._metrics = {}

    def raw_client_metrics(self):
        return self._client_metrics()

    def create_metric(self, metric_name, metric_type, overwrite_metric=True):
        logger.info(f"creating a new metric with name '{metric_name}' and type '{metric_type}'")
        creator = {MetricsType.COUNTER: metrics.new_counter,
                   MetricsType.GAUGES: metrics.new_gauge,
                   MetricsType.METER: metrics.new_meter}
        try:
            is_metric_is_already_exists = metric_name in metrics.metrics()

            if is_metric_is_already_exists and overwrite_metric:
                logger.info("overriding existing metric with a new one")
                metrics.delete_metric(metric_name)
                del self._metrics[metric_name]

            if metric_type in creator:
                self._metrics[metric_name] = creator[metric_type](metric_name)
            else:
                raise UnExpectedMetricType(
                    f"invalid metric type was created '{metric_type}', supported types: {creator.keys()}")
        except DuplicateMetricError:
            logger.info(f"metric {metric_name} is already exist, skip metric creation")

    def add_metric(self, metric_name, value):
        if metric_name in self._metrics:
            self._metrics[metric_name].notify(value)
        else:
            raise UnExpectedMetricAccessed(
                f"invalid metric was accessed '{metric_name}', found metrics: {self._metrics.keys()}"
            )

    def get_metric(self, item):

        if item == "raw":
            return self.raw_client_metrics()

        if item in self._metrics:
            return self._metrics.get(item)

        raise UnExpectedMetricType(
            f"invalid metric was accessed '{item}', found metrics: {self._metrics.keys()}"
        )

    def has_metric(self, item):
        return item in self._metrics

    def stop(self):
        for metric_name in self._metrics:
            logger.info(f"delete metrics {metric_name} from {type(self)}")
            metrics.delete_metric(metric_name)

        logger.debug(f"metrics left after removal '{metrics.metrics()}'")

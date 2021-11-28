from json import dumps

from windchill_metric_config.description import Description
from windchill_metric_config.windchill.method_server import MethodServer
from windchill_metric_config.windchill.garbage_collector import \
    GarbageCollector
from windchill_metric_config.windchill.memory import Memory
from windchill_metric_config.windchill.method_context import MethodContext
from windchill_metric_config.windchill.queue_worker import QueueWorker


class WindchillMetrics:

    def __init__(self):

        self.apache_status = Description(
            metric_id='windchill_apache_status',
            desc='windchill apache status (0=not running, >1=http code)'
        )
        self.windchill_status = Description(
            metric_id='windchill_windchill_status',
            desc='windchill app status (0=not running, >1=http code)'
        )
        self.api_resp_time = Description(
            metric_id='windchill_api_response_time_seconds',
            desc='windchill api (/Windchill/api/v1/publishmonitor'
                 '/getworkerinfo.jsp) response time'
        )
        self.active_users = Description(
            metric_id='windchill_active_users_total',
            desc='windchill total active users count',
        )
        self.version_info = Description(
            metric_id='windchill_version_info',
            desc='windchill version and release info',
            labels=['release_id', 'sequence', 'release', 'display',
                    'data_code'],
            prometheus_method='info'
        )

        self.method_server = MethodServer()
        self.queue_worker = QueueWorker()
        self.garbage_collector = GarbageCollector()
        self.memory = Memory()
        self.method_context = MethodContext()

    def __str__(self):
        return dumps(self.as_dict())

    def as_dict(self):
        all_metrics = {}
        for item in self.__dict__.keys():
            all_metrics[item] = self.__getattribute__(item).as_dict()
        return all_metrics

    def as_yaml_dict(self):
        metrics = {}
        for item in self.__dict__.keys():
            child = self.__getattribute__(item)
            if type(child) == Description:
                metrics[child.id] = child.enabled
            else:
                metrics[item] = child.as_yaml_dict()
        return metrics

    def generate_yaml(self, yaml_object, comment_indent):
        for item in self.__dict__.keys():
            child = self.__getattribute__(item)
            if type(child) == Description:
                yaml_object.yaml_add_eol_comment(child.description, child.id,
                                                 comment_indent)
            else:
                child.generate_yaml(yaml_object[item], comment_indent)

    def metrics_as_list(self, metric_list: list):
        for item in self.__dict__.keys():
            child = self.__getattribute__(item)
            if type(child) == Description:
                metric_list.append(child)
            else:
                child.metrics_as_list(metric_list)

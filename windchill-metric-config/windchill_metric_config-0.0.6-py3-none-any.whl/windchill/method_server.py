from json import dumps

from windchill_metric_config.description import Description


class MethodServer:
    def __init__(self):
        self.start_time = Description(
            metric_id='windchill_server_status_runtime_start_time',
            desc='windchill apache status (0=not running, >1=http code)'
        )
        self.uptime = Description(
            metric_id='windchill_server_status_runtime_uptime',
            desc='windchill apache status (0=not running, >1=http code)'
        )

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
                child: Description
                metrics[child.id] = child.enabled
        return metrics

    def generate_yaml(self, yaml_object, comment_indent):
        for item in self.__dict__.keys():
            child = self.__getattribute__(item)
            if type(child) == Description:
                child: Description
                yaml_object.yaml_add_eol_comment(child.description, child.id,
                                                 comment_indent)

    def metrics_as_list(self, metric_list: list):
        for item in self.__dict__.keys():
            child = self.__getattribute__(item)
            if type(child) == Description:
                metric_list.append(child)
            else:
                child.metrics_as_list(metric_list)

from json import dumps

from prometheus_client import Gauge, Info


class Description:
    def __init__(self, metric_id: str, desc: str = 'test',
                 labels: list = None, enabled: bool = False,
                 prometheus_method: str = 'gauge'):
        """
        :param metric_id: metrics identification,
                          example process_real_memory_total_bytes
        :param desc: description for metric id
        :param labels: list of all required labels, default set values are
                        ['host', 'resource_type', 'environment', 'company']
        """
        self.id = metric_id
        self.labels = ['host', 'resource_type', 'environment', 'company']
        if labels is not None:
            for label in labels:
                if label not in self.labels:
                    self.labels.append(label)
        self.description = desc
        self.enabled = enabled
        if 'gauge' == prometheus_method:
            self.prometheus_obj = Gauge(metric_id, desc, self.labels)
        elif 'info' == prometheus_method:
            self.prometheus_obj = Info(metric_id, desc)

    def __str__(self):
        return dumps(self.as_dict())

    def as_dict(self):
        obj = {}
        for key in self.__dict__.keys():
            value = self.__getattribute__(key)
            if type(value) is str or type(value) is list or \
                    type(value) is bool:
                obj[key] = value
        return obj

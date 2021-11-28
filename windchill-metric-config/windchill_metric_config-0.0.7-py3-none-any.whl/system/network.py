from json import dumps

from windchill_metric_config.description import Description


class Network:
    def __init__(self):
        self.bytes_sent = Description(
            metric_id='process_network_bytes_sent',
            desc='bytes sent over all network addresses',
        )
        self.bytes_recv = Description(
            metric_id='process_network_packets_recv',
            desc='bytes received over all network addresses',
        )
        self.err_in = Description(
            metric_id='process_network_err_in',
            desc='total number of errors while receiving',
        )
        self.err_out = Description(
            metric_id='process_network_err_out',
            desc='total number of errors while sending',
        )
        self.drop_in = Description(
            metric_id='process_network_drop_in',
            desc='total number of incoming packets which were dropped',
        )
        self.drop_out = Description(
            metric_id='process_network_drop_out',
            desc='total number of outgoing packets which were dropped '
                 '(always 0 on macOS and BSD)',
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

    def set_config(self, config: dict):
        for key in config:
            for item in self.__dict__.keys():
                child = self.__getattribute__(item)
                if type(child) == Description:
                    if child.id == key:
                        child.enabled = config[key]

                else:
                    if item == key:
                        child.set_config(config[key])

    def metrics_as_list(self, metric_list: list):
        for item in self.__dict__.keys():
            child = self.__getattribute__(item)
            if type(child) == Description:
                metric_list.append(child)
            else:
                child.metrics_as_list(metric_list)

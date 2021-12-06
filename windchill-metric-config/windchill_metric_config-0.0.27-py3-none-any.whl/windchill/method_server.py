from json import dumps

from windchill_metric_config.description import Description


class MethodServer:
    def __init__(self):
        self.start_time = Description(
            metric_id='windchill_server_status_runtime_start_time',
            desc='windchill apache status (0=not running, >1=http code)',
            labels=['server_type', 'sub_server_types']
        )
        self.uptime = Description(
            metric_id='windchill_server_status_runtime_uptime',
            desc='windchill apache status (0=not running, >1=http code)',
            labels=['server_type', 'sub_server_types']
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

    def as_treeview(self):
        metrics = []
        for item in self.__dict__.keys():
            child = self.__getattribute__(item)
            tree_item = {}
            if type(child) == Description:
                tree_item['text'] = child.id
                tree_item['state'] = {'checked': child.enabled}
                tree_item['data'] = {'description': child.description}
            else:
                tree_item['text'] = item
                tree_item['children'] = child.as_treeview()
            metrics.append(tree_item)
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

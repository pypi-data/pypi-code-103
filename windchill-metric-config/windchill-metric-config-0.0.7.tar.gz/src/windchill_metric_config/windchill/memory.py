from windchill_metric_config.description import Description


class Memory:
    def __init__(self):
        self.heap_threshold = Description(
            metric_id='windchill_server_status_memory_heap_usage_threshold_percent',
            desc='Heap memory usage threshold in percent'
        )
        self.heap_percent = Description(
            metric_id='windchill_server_status_memory_heap_usage_percent',
            desc='Heap memory usage in percent'
        )
        self.perm_gen_threshold = Description(
            metric_id='windchill_server_status_memory_perm_gen_usage_threshold_percent',
            desc='Perm gen memory usage threshold in percent'
        )
        self.pem_gem_percent = Description(
            metric_id='windchill_server_status_memory_perm_gen_usage_percent',
            desc='Perm gen memory usage in percent'
        )

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

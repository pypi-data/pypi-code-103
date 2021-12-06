from windchill_metric_config.description import Description


class Memory:
    def __init__(self):
        self.heap_threshold = Description(
            metric_id='windchill_memory_heap_usage_threshold_percent',
            desc='Heap memory usage threshold in percent',
            labels=['server_type', 'sub_server_types']
        )
        self.heap_percent = Description(
            metric_id='windchill_memory_heap_usage_percent',
            desc='Heap memory usage in percent',
            labels=['server_type', 'sub_server_types']
        )
        self.perm_gen_threshold = Description(
            metric_id='windchill_memory_perm_gen_usage_threshold_percent',
            desc='Perm gen memory usage threshold in percent',
            labels=['server_type', 'sub_server_types']
        )
        self.perm_gem_percent = Description(
            metric_id='windchill_memory_perm_gen_usage_percent',
            desc='Perm gen memory usage in percent',
            labels=['server_type', 'sub_server_types']
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

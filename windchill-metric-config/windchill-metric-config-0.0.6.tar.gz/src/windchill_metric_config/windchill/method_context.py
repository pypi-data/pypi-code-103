from windchill_metric_config.description import Description


class MethodContext:
    def __init__(self):
        self.context_average = Description(
            metric_id='windchill_server_status_mc_active_contexts_average',
            desc='active context average'
        )
        self.context_end = Description(
            metric_id='windchill_server_status_mc_active_contexts_end',
            desc=''
        )
        self.context_max = Description(
            metric_id='windchill_server_status_mc_active_contexts_max',
            desc=''
        )
        self.context_start = Description(
            metric_id='windchill_server_status_mc_active_contexts_start',
            desc=''
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
                if child.description != 'test' and len(child.description)\
                        > 0:
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

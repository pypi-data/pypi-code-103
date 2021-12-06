from windchill_metric_config.description import Description


class Sessions:
    def __init__(self):
        self.average = Description(
            metric_id='windchill_active_sessions_average',
            desc='activeSessionsAverage',
            labels=['server_type', 'sub_server_types']
        )
        self.end = Description(
            metric_id='windchill_active_sessions_end',
            desc='activeSessionsEnd',
            labels=['server_type', 'sub_server_types']
        )
        self.max = Description(
            metric_id='windchill_active_sessions_max',
            desc='activeSessionsMax',
            labels=['server_type', 'sub_server_types']
        )
        self.start = Description(
            metric_id='windchill_active_sessions_start',
            desc='activeSessionsStart',
            labels=['server_type', 'sub_server_types']
        )
        self.activated = Description(
            metric_id='windchill_sessions_activated',
            desc='sessionsActivated',
            labels=['server_type', 'sub_server_types']
        )
        self.created = Description(
            metric_id='windchill_sessions_created',
            desc='sessionsCreated',
            labels=['server_type', 'sub_server_types']
        )
        self.destroyed = Description(
            metric_id='windchill_sessions_destroyed',
            desc='sessionsDestroyed',
            labels=['server_type', 'sub_server_types']
        )
        self.passivated = Description(
            metric_id='windchill_sessions_passivated',
            desc='sessionsPassivated',
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

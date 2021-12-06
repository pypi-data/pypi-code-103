from windchill_metric_config.description import Description


class MethodContext:
    def __init__(self):
        self.average = Description(
            metric_id='windchill_mc_active_context_average',
            desc='activeContextsAverage',
            labels=['server_type', 'sub_server_types']
        )
        self.end = Description(
            metric_id='windchill_mc_active_context_end',
            desc='activeContextsEnd',
            labels=['server_type', 'sub_server_types']
        )
        self.max = Description(
            metric_id='windchill_mc_active_context_max',
            desc='activeContextsMax',
            labels=['server_type', 'sub_server_types']
        )
        self.start = Description(
            metric_id='windchill_mc_active_context_start',
            desc='activeContextsStart',
            labels=['server_type', 'sub_server_types']
        )
        self.blocked = Description(
            metric_id='windchill_mc_blocked_count_per_context',
            desc='averageBlockedCountPerContext',
            labels=['server_type', 'sub_server_types']
        )
        self.cobra = Description(
            metric_id='windchill_mc_cobra_calls_per_context_average',
            desc='averageCORBACallsPerContext',
            labels=['server_type', 'sub_server_types']
        )
        self.jdbc = Description(
            metric_id='windchill_mc_jdbc_calls_per_context_average',
            desc='averageJDBCCallsPerContext',
            labels=['server_type', 'sub_server_types']
        )
        self.jndi = Description(
            metric_id='windchill_mc_jndi_calls_per_context_average',
            desc='averageJNDICallsPerContext',
            labels=['server_type', 'sub_server_types']
        )
        self.remote_cache = Description(
            metric_id='windchill_mc_remote_cache_calls_per_context_average',
            desc='averageRemoteCacheCallsPerContext',
            labels=['server_type', 'sub_server_types']
        )
        self.waited_count = Description(
            metric_id='windchill_mc_waited_count_per_context',
            desc='averageWaitedCountPerContext',
            labels=['server_type', 'sub_server_types']
        )
        self.completed_context = Description(
            metric_id='windchill_mc_completed_context',
            desc='completedContexts',
            labels=['server_type', 'sub_server_types']
        )
        self.cpu_seconds = Description(
            metric_id='windchill_mc_cpu_seconds_average',
            desc='contextCpuSecondsAverage',
            labels=['server_type', 'sub_server_types']
        )
        self.jdbc_wait = Description(
            metric_id='windchill_mc_jdbc_conn_wait_seconds_average',
            desc='contextJDBCConnWaitSecondsAverage',
            labels=['server_type', 'sub_server_types']
        )
        self.seconds = Description(
            metric_id='windchill_mc_seconds_average',
            desc='contextSecondsAverage',
            labels=['server_type', 'sub_server_types']
        )
        self.seconds_max = Description(
            metric_id='windchill_mc_seconds_max',
            desc='contextSecondsMax',
            labels=['server_type', 'sub_server_types']
        )
        self.user = Description(
            metric_id='windchill_mc_user_seconds_average',
            desc='contextUserSecondsAverage',
            labels=['server_type', 'sub_server_types']
        )
        self.per_seconds = Description(
            metric_id='windchill_mc_context_per_seconds',
            desc='contextsPerSecond',
            labels=['server_type', 'sub_server_types']
        )
        self.error = Description(
            metric_id='windchill_mc_error_count',
            desc='errorCount',
            labels=['server_type', 'sub_server_types']
        )
        self.blocked_time = Description(
            metric_id='windchill_mc_blocked_time_per_context_percentage',
            desc='percentageOfContextTimeBlocked',
            labels=['server_type', 'sub_server_types']
        )
        self.cobra_time = Description(
            metric_id='windchill_mc_cobra_time_of_context_percentage',
            desc='percentageOfContextTimeInCORBACalls',
            labels=['server_type', 'sub_server_types']
        )
        self.jdbc_time = Description(
            metric_id='windchill_mc_jdbc_time_of_context_percentage',
            desc='percentageOfContextTimeInJDBCCalls',
            labels=['server_type', 'sub_server_types']
        )
        self.jdbc_conn_wait = Description(
            metric_id='windchill_mc_jdbc_time_conn_wait_percentage',
            desc='',
            labels=['server_type', 'sub_server_types']
        )
        self.jndi_time = Description(
            metric_id='windchill_mc_jndi_time_of_context_percentage',
            desc='percentageOfContextTimeInJDBCConnWait',
            labels=['server_type', 'sub_server_types']
        )
        self.remote_cache_calls = Description(
            metric_id='windchill_mc_remote_cache_time_of_context_percentage',
            desc='percentageOfContextTimeInJNDICalls',
            labels=['server_type', 'sub_server_types']
        )
        self.time_waited = Description(
            metric_id='windchill_mc_time_waited_time_of_context_percentage',
            desc='percentageOfContextTimeWaited',
            labels=['server_type', 'sub_server_types']
        )
        self.redirect = Description(
            metric_id='windchill_mc_redirect_count',
            desc='redirectCount',
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

from windchill_metric_config.description import Description


class ServletRequests:
    def __init__(self):
        self.average = Description(
            metric_id='windchill_servlet_active_requests_average',
            desc='activeRequestsAverage',
            labels=['server_type', 'sub_server_types']
        )
        self.end = Description(
            metric_id='windchill_servlet_active_requests_end',
            desc='activeRequestsEnd',
            labels=['server_type', 'sub_server_types']
        )
        self.max = Description(
            metric_id='windchill_servlet_active_requests_max',
            desc='activeRequestsMax',
            labels=['server_type', 'sub_server_types']
        )
        self.start = Description(
            metric_id='windchill_servlet_active_requests_start',
            desc='activeRequestsStart',
            labels=['server_type', 'sub_server_types']
        )
        self.blocked = Description(
            metric_id='windchill_servlet_blocked_count_per_request',
            desc='averageBlockedCountPerRequest',
            labels=['server_type', 'sub_server_types']
        )
        self.ie_requests = Description(
            metric_id='windchill_servlet_ie_calls_per_request',
            desc='averageIECallsPerRequest',
            labels=['server_type', 'sub_server_types']
        )
        self.jndi_requests = Description(
            metric_id='windchill_servlet_jndi_calls_per_request',
            desc='averageJNDICallsPerRequest',
            labels=['server_type', 'sub_server_types']
        )
        self.rmi_requests = Description(
            metric_id='windchill_servlet_rmi_calls_per_request',
            desc='averageRMICallsPerRequest',
            labels=['server_type', 'sub_server_types']
        )
        self.soap_requests = Description(
            metric_id='windchill_servlet_soap_call_per_request',
            desc='averageSOAPCallsPerRequest',
            labels=['server_type', 'sub_server_types']
        )
        self.waited_count = Description(
            metric_id='windchill_servlet_waited_count_per_request',
            desc='averageWaitedCountPerRequest',
            labels=['server_type', 'sub_server_types']
        )
        self.completed_requests = Description(
            metric_id='windchill_servlet_completed_requests',
            desc='completedRequests',
            labels=['server_type', 'sub_server_types']
        )
        self.error_count = Description(
            metric_id='windchill_servlet_error_count',
            desc='errorCount',
            labels=['server_type', 'sub_server_types']
        )
        self.blocked_percent = Description(
            metric_id='windchill_servlet_blocked_time_percentage',
            desc='percentageOfRequestTimeBlocked',
            labels=['server_type', 'sub_server_types']
        )
        self.ie_percent = Description(
            metric_id='windchill_servlet_ie_calls_time_percentage',
            desc='percentageOfRequestTimeInIECalls',
            labels=['server_type', 'sub_server_types']
        )
        self.jndi_percent = Description(
            metric_id='windchill_servlet_jndi_calls_time_percentage',
            desc='percentageOfRequestTimeInJNDICalls',
            labels=['server_type', 'sub_server_types']
        )
        self.rmi_percent = Description(
            metric_id='windchill_servlet_rmi_calls_time_percentage',
            desc='percentageOfRequestTimeInRMICalls',
            labels=['server_type', 'sub_server_types']
        )
        self.soap_percent = Description(
            metric_id='windchill_servlet_soap_calls_time_percentage',
            desc='percentageOfRequestTimeInSOAPCalls',
            labels=['server_type', 'sub_server_types']
        )
        self.time_waited = Description(
            metric_id='windchill_servlet_time_waited_percentage',
            desc='percentageOfRequestTimeWaited',
            labels=['server_type', 'sub_server_types']
        )
        self.cpu_seconds = Description(
            metric_id='windchill_servlet_cpu_seconds_average',
            desc='requestCpuSecondsAverage',
            labels=['server_type', 'sub_server_types']
        )
        self.seconds_average = Description(
            metric_id='windchill_servlet_requests_seconds_average',
            desc='requestSecondsAverage',
            labels=['server_type', 'sub_server_types']
        )
        self.requests_max = Description(
            metric_id='windchill_servlet_requests_seconds_max',
            desc='requestSecondsMax',
            labels=['server_type', 'sub_server_types']
        )
        self.user_seconds_average = Description(
            metric_id='windchill_servlet_requests_user_seconds_average',
            desc='requestUserSecondsAverage',
            labels=['server_type', 'sub_server_types']
        )
        self.requests_per_seconds = Description(
            metric_id='windchill_servlet_requests_per_second',
            desc='requestsPerSecond',
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

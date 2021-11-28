from windchill_metric_config.description import Description


class QueueWorker:
    def __init__(self):
        self.worker_status = Description(
            metric_id='windchill_worker_status',
            desc='windchill worker status (0=not running, 1=ok, '
                 '2=fails to start)',
            labels=['worker']
        )
        self.queue_failed = Description(
            metric_id='windchill_queue_jobs_failed',
            desc='windchill failed jobs queue count',
            labels=['queue']
        )
        self.queue_total = Description(
            metric_id='windchill_queue_jobs_total',
            desc='windchill total jobs queue count',
            labels=['queue']
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

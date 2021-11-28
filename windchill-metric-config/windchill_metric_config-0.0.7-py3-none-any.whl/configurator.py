from json import dumps, loads

from ruamel.yaml import YAML, scalarstring, CommentedMap

from windchill_metric_config.description import Description
from windchill_metric_config.system.system import SystemMetrics
from windchill_metric_config.windchill.windchill import WindchillMetrics


class Metrics:
    comment_indent = 80

    def __init__(self):
        self.system = SystemMetrics()
        self.windchill = WindchillMetrics()

    def __str__(self):
        return dumps(self.as_dict())

    def as_dict(self):
        return {
            'system': self.system.as_dict(),
            'windchill': self.windchill.as_dict()
        }

    def as_yaml_dict(self):
        return {
            'system': self.system.as_yaml_dict(),
            'windchill': self.windchill.as_yaml_dict()
        }

    def add_yaml_comments(self, config: dict):
        for key in self.__dict__.keys():
            if key in config:
                item = self.__getattribute__(key)
                if type(item) != Description:
                    item.generate_yaml(config[key], self.comment_indent)

    def save_as_yaml(self, config_yaml: str):
        yaml = YAML()
        data = loads(dumps(self.as_yaml_dict()), object_pairs_hook=CommentedMap)
        scalarstring.walk_tree(data)
        self.windchill.generate_yaml(data['windchill'], self.comment_indent)
        self.system.generate_yaml(data['system'], self.comment_indent)
        with open(config_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(data, f)

    def set_config(self, config: dict):
        for key in self.__dict__.keys():
            if key in config:
                item = self.__getattribute__(key)
                if type(item) != Description:
                    item.set_config(config[key])

    def load_config_from_file(self, config_yaml: str):
        yaml = YAML()
        with open(config_yaml, 'r', encoding='utf-8') as f:
            data = yaml.load(f)
        for key in self.__dict__.keys():
            if key in data:
                if key == 'system':
                    self.__getattribute__(key).set_config(data[key])

    def metrics_as_list(self) -> [Description]:
        metric_list = []
        for item in self.__dict__.keys():
            child = self.__getattribute__(item)
            if type(child) == Description:
                metric_list.append(child.id)
            else:
                child.metrics_as_list(metric_list)

        return metric_list

    def metrics_id_list(self) -> [str]:
        metric_list = []
        for metric in self.metrics_as_list():
            metric_list.append(metric.id)
        return metric_list

    def get_metric_config(self, metrics_id: str) -> Description:
        for metric in self.metrics_as_list():
            if metrics_id == metric.id:
                return metric

    def validate_metric(self, post_metric: dict) -> [str]:
        """
        * This is a bulleted list.
        * It has two items, the second item uses two lines.
        This is a normal text paragraph. The next paragraph is a code sample::

           {
              "metric_id": "process_real_memory_total_bytes",
              "labels": [
                {
                  "key": "environment",
                  "value": "anton500"
                }
              ],
              "value": 20.35
            }

        This is a normal text paragraph again.
        :param post_metric: dictionary with metric_id and labels
        :type post_metric dict
        :return: list with all failed labels
        """
        posted_labels = []
        for posted_label in post_metric['labels']:
            if len(posted_label['value']) > 0:
                posted_labels.append(posted_label['key'])

        metric: Description = self.get_metric_config(post_metric.get(
            'metric_id'))
        error_bucket = []
        for label in metric.labels:
            if label not in posted_labels:
                error_bucket.append(label)
        return error_bucket

import atexit
import logging
import os

import __main__
import yaml

GIT_CONTROL = os.system("git rev-parse") == 0


def save_git_sha(job_dir):
    cmd = f"echo $(git rev-parse --short HEAD) > {job_dir}/git_sha.txt"
    os.system(cmd)


def get_pipeline_dir():
    pipeline_dir = os.path.relpath(os.path.dirname(__main__.__file__))
    if not os.path.exists(pipeline_dir):
        os.makedirs(pipeline_dir, exist_ok=True)
        logging.info(f"Created pipeline directory {pipeline_dir}")

    return pipeline_dir


class ConfigCollector:
    _instance = None

    def __init__(self):
        raise Exception(
            "This class is a singleton. Use JobCollector.instance instead of __init__"
        )

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._init(cls._instance)
        return cls._instance

    # pylint:disable=attribute-defined-outside-init
    def _init(self):
        self.configs = []
        self.pipeline_dir = get_pipeline_dir()
        atexit.register(self.run)

    def add_config(self, config):
        self.configs.append(config)

    def run(self, pipeline_dir=None):
        if pipeline_dir:
            self.pipeline_dir = pipeline_dir

        yaml.dump(
            self.configs,
            open(os.path.join(self.pipeline_dir, "pipeline_config.yaml"), "w"),
        )


CONFIG_COLLECTOR = ConfigCollector.instance()

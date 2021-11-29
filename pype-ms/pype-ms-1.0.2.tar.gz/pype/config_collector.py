import json
import os
import atexit

import yaml

from pype import utils


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
        assert False, ' you are using the wrong config collector'
        self.configs = []
        self.pipeline_dir = utils.get_pipeline_dir()
        # atexit.register(self.run)

    def add_config(self, config):
        self.configs.append(config)

    def run(self, pipeline_dir=None):

        outputs = open(os.path.join(self.pipeline_dir, "outputs"), "w")
        outputs_dict = {}

        for config in self.configs:
            job_id = config["job_id"]

            if "outputs" in config:
                for key, val in config["outputs"].items():
                    output_key = job_id.replace("/", "_") + "_" + key
                    outputs.write(f'{output_key} = "{val}"\n')
                    outputs_dict[output_key] = val


        if pipeline_dir:
            self.pipeline_dir = pipeline_dir

        yaml.dump(
            self.configs, open(os.path.join(self.pipeline_dir, "pipeline_config.yaml"), "w")
        )
        json.dump(outputs_dict, open(os.path.join(self.pipeline_dir, "outputs.json"), "w"))

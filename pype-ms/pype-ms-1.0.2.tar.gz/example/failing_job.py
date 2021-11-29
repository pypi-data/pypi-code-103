
from pype.baseconfig import BaseConfig


class ExampleFailingJobConfig(BaseConfig):
    script_path = "example/failing_job.py"

def main(config):
    _ = config
    1/0

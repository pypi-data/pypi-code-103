from pype.baseconfig import BaseConfig


class Config(BaseConfig):
    script_path = "example/job.py"
    inputs = {"msg"}
    params = {"append": "good day"}
    outputs = {"msg": "msg.txt"}


def main(config):
    msg = open(config["inputs"]["msg"]).read()
    msg += config["params"]["append"]
    open(config["outputs"]["msg"], "w").write(msg)

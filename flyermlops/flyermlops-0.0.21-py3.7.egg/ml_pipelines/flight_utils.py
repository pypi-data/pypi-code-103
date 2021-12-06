import re
from cookiecutter.main import cookiecutter
import inspect
from typing import List
from typing import Dict
from .. import exceptions
from sagemaker.network import NetworkConfig
import os
from shutil import copyfile
import yaml
import sagemaker
import boto3
import glob
import flyermlops
from pathlib import Path
from collections import deque

dir_path = os.path.abspath(flyermlops.__file__).split("/")[:-1]


def create_cookie_cutter(extra_context):

    file_path = f"{'/'.join(dir_path)}/cookie_template.zip"
    cookiecutter(
        file_path,
        no_input=True,
        overwrite_if_exists=True,
        extra_context={**extra_context},
    )


def create_sklearn_cutter(extra_context):

    file_path = f"{'/'.join(dir_path)}/sklearn_template.zip"
    cookiecutter(
        file_path,
        no_input=True,
        overwrite_if_exists=True,
        extra_context={**extra_context},
    )


def clean_text(text: List[str] = None, single_word=False):
    text = text or []

    if isinstance(text, str):
        text = [text]

    clean_list = []
    for word in text:
        if word is not None:
            clean_list.append(re.sub("[^-a-zA-Z0-9 \\n\\.]", "-", word))

    return clean_list


def extract_artifact(line):
    if "self." in line:
        artifact = line.split("self.")[1].split(" ")[0]
        line = line.replace("self.", "")

    else:
        artifact = None

    return artifact, line


def find_pattern_list_split(lines, pattern):
    lines = lines.split("\n")
    indices = [i for i, s in enumerate(lines) if pattern in s]
    new_lines = lines[indices[0] + 1 :]

    spaces = 0
    for i in new_lines[1].split(" "):
        if not i:
            spaces += 1
    # print(new_lines[1])
    # print(spaces)
    return new_lines, spaces


def write_leg_to_file(
    directory, origin_name, func, stage,
):

    clean_name = clean_text(origin_name)[0]

    # Get func lines
    lines = inspect.getsource(func)

    if "tensorflow" in lines:
        ac_type = "tensorflow"
    else:
        ac_type = "sklearn"

    # find where pattern begins
    pattern = f"def {origin_name}(self):"
    lines, spaces = find_pattern_list_split(lines, pattern)

    # Filename
    filename = f"{clean_name}.py"

    # Check path and create if not exists
    path = f"{directory}/pipeline"
    stage_path = f"{path}/{stage}"
    if not os.path.exists(path):
        os.makedirs(stage_path)

    # Create py file
    filehandle = open(f"{stage_path}/{filename}", "w")
    filehandle.write('if __name__ == "__main__": \n')

    if clean_name == "takeoff":
        write_takeoff(dir_path, filehandle)

    elif clean_name == "land":
        write_landing(dir_path, filehandle)

    else:
        for line in lines:

            # Extract instance variables and save to artifact store
            artifact, line = extract_artifact(line)

            # Write line
            filehandle.write(line[spaces - 4 :] + "\n")

        filehandle.close()

    return ac_type


def write_takeoff(dir_path, filehandle):
    file_path = f"{'/'.join(dir_path)}/ml_pipelines/takeoff_text.txt"
    _file = open(file_path, "r")
    lines = _file.read().split("\n")
    for line in lines:
        filehandle.write(f"{line}" + "\n")
    filehandle.close()


def write_landing(dir_path, filehandle):
    file_path = f"{'/'.join(dir_path)}/ml_pipelines/land_text.txt"
    _file = open(file_path, "r")
    lines = _file.read().split("\n")
    for line in lines:
        filehandle.write(f"{line}" + "\n")
    filehandle.close()


def write_to_yaml(data: dict, directory: str, file_name: str):
    path = f"{directory}/pipeline/"

    with open(f"{path}/{file_name}.yaml", "w") as outfile:
        yaml.dump(data, outfile)


def get_step_dependencies(relationships) -> Dict:
    """
    Parses a dict of parent child relationships to determine order of relationships.

    Args:
        Relationships: Dictionary containing keys with parent values and vals with children values.
    Returns:
        Dict containing dependencies for dags
    """
    dependencies = dict()
    for dag in relationships.keys():
        dependencies[dag] = []
        for key, values in relationships.items():
            for val in values:
                if dag == val:
                    dependencies[dag].append(re.sub("[^-a-zA-Z0-9 \\n\\.]", "-", key))
    return dependencies


def available_engines():
    return [
        "ml.p2.xlarge",
        "ml.m5.4xlarge",
        "ml.m4.16xlarge",
        "ml.p4d.24xlarge",
        "ml.c5n.xlarge",
        "ml.p3.16xlarge",
        "ml.m5.large",
        "ml.p2.16xlarge",
        "ml.c4.2xlarge",
        "ml.c5.2xlarge",
        "ml.c4.4xlarge",
        "ml.c5.4xlarge",
        "ml.c5n.18xlarge",
        "ml.g4dn.xlarge",
        "ml.g4dn.12xlarge",
        "ml.c4.8xlarge",
        "ml.g4dn.2xlarge",
        "ml.c5.9xlarge",
        "ml.g4dn.4xlarge",
        "ml.c5.xlarge",
        "ml.g4dn.16xlarge",
        "ml.c4.xlarge",
        "ml.g4dn.8xlarge",
        "ml.c5n.2xlarge",
        "ml.c5n.4xlarge",
        "ml.c5.18xlarge",
        "ml.p3dn.24xlarge",
        "ml.p3.2xlarge",
        "ml.m5.xlarge",
        "ml.m4.10xlarge",
        "ml.c5n.9xlarge",
        "ml.m5.12xlarge",
        "ml.m4.xlarge",
        "ml.m5.24xlarge",
        "ml.m4.2xlarge",
        "ml.p2.8xlarge",
        "ml.m5.2xlarge",
        "ml.p3.8xlarge",
        "ml.m4.4xlarge",
    ]


def verify_args(
    engine: str, number_engines: int, ac_type: str, dependencies: List[str]
):
    avail_engines = available_engines()
    if engine not in avail_engines:
        raise exceptions.InvalidComputeResource(
            f"""Invalid compute resource provided. Please select engine type from the provided list.
                    For more information, please see https://aws.amazon.com/sagemaker/pricing/.
                    {avail_engines })
                """
        )

    if ac_type not in ["sklearn", "tensorflow"]:
        raise exceptions.InvalidEstimator(
            """ Invalid ac type provided. Available Sagemaker Estimators are sklearn and tensorflow.
        """
        )

    try:
        assert isinstance(number_engines, int)
    except Exception as e:
        raise exceptions.NotofTypeInt("""Variable number_engines must be of type int""")

    try:
        assert isinstance(dependencies, list)
    except Exception as e:
        raise exceptions.NotofTypeList("""Variable dependencies must be of type list""")


def get_vpc_config(config):
    if "vpc_config" in config.keys():
        vpc_config = NetworkConfig(
            security_group_ids=config["vpc_config"]["security_group_ids"],
            subnets=config["vpc_config"]["subnets"],
        )
    else:
        vpc_config = None

    return vpc_config


def get_session(default_bucket, region_name):
    """Gets the sagemaker session

    Args:
        default_bucket: the bucket to use for storing the artifacts

    Returns:
        sagemaker.session.Session instance
        Region

    """

    boto_session = boto3.Session(region_name)
    sagemaker_client = boto_session.client("sagemaker")
    runtime_client = boto_session.client("sagemaker-runtime")

    sagemaker_session = sagemaker.session.Session(
        default_bucket=default_bucket,
        boto_session=boto_session,
        sagemaker_client=sagemaker_client,
        sagemaker_runtime_client=runtime_client,
    )

    return sagemaker_session


def get_config() -> dict:
    for path in Path(os.getcwd()).rglob("*.yaml"):
        config_path = path.absolute()
    assert os.path.isfile(config_path)
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config, config_path


def topological_sort(relationships) -> List:
    """
        Parses a dict of parent child relationships to determine order of relationships.

        Args:
            Relationships: Dictionary containing keys with parent values and vals with children values.
        Returns:
            List with order of relationships
        """

    GRAY, BLACK = 0, 1
    order, enter, state = deque(), set(relationships), {}

    def dfs(node):
        state[node] = GRAY
        for k in relationships.get(node, ()):
            sk = state.get(k, None)
            if sk == GRAY:
                raise ValueError("cycle")
            if sk == BLACK:
                continue
            enter.discard(k)
            dfs(k)
        order.appendleft(node)
        state[node] = BLACK

    while enter:
        dfs(enter.pop())
    return order

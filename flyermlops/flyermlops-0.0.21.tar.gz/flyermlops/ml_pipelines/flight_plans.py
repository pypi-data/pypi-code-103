from typing import List
from collections import OrderedDict
import shutil
import subprocess
import os
import glob
import yaml

from flyermlops.ml_pipelines import flight_utils as utils
from flyermlops.ml_pipelines.cli_utils import stdout_msg
from flyermlops import exceptions


def add_leg(
    engine: str = None,
    number_engines: int = 1,
    destinations: List[str] = None,
    stage: str = "models",
    retry=0,
):
    """Decorater used to extract and provision resources for each
       method defined within a flight plan.

    Args:
        engine: Sagemaker comptue resource
        destination: Leg that depends on current leg.

    """

    def inner_func(func):
        def wrapper(self, *args, **kwargs):

            origin_name = func.__name__
            leg_name = utils.clean_text(origin_name)[0]

            # Write to file
            ac_type = utils.write_leg_to_file(
                self._config["project_name"], origin_name, func, stage,
            )

            utils.verify_args(engine, number_engines, ac_type)

            # Get leg specs
            leg_specs = {
                "destinations": utils.clean_text(destinations),
                "engine": engine,
                "number_engines": number_engines,
                "ac_type": ac_type,
                "retry": retry,
            }

            # Update flight plan
            self._flight_plan.update({leg_name: leg_specs})

            # Update OD pairs
            self._write_od_pairs(leg_name, leg_specs["destinations"])

        return wrapper

    return inner_func


class BaseFlightPlan:
    def __init__(
        self, config: dict = None, requirments: str = None,
    ):

        # NOTE
        # variables and methods must have a "_" prefix.
        # BaseFlightPlan is used to parse methods from the subclassed flight plan only.

        # Create initial flight plan
        self._requirements = requirments
        self._flight_plan = dict()
        self._od_pairs = {}

        # Get config
        stdout_msg("Beginning initial flight plan diagnostics", fg="red", bold=True)
        self._config = self._get_aircraft_config(config)

        # Create repo template to write to
        stdout_msg("Creating flight schematics")
        self._create_flight_plan_schematics()

        # Write flight plan
        self._write_flight_plan()

        # Write flight runner
        self._flight_liftoff()

    def _create_flight_plan_schematics(self):
        if os.path.exists(self._config["project_name"]) and os.path.isdir(
            self._config["project_name"]
        ):
            shutil.rmtree(self._config["project_name"])
        utils.create_cookie_cutter(self._config)

    def _write_flight_plan(self):
        stdout_msg(
            f"Writing flight plan!", fg="red", bold=True,
        )

        # Parse and write flight legs to directory
        for method in self.__dir__():
            if method.startswith("_") is False:
                self.__getattribute__(method)()

        # Write vpc config if exists
        self._get_vpc_if_exists()

        # Write requirements to directory
        if self._requirements is not None:
            shutil.copyfile(
                self._requirements,
                f"{self._config['project_name']}/pipeline/requirements.txt",
            )

        # Write fight plan to config
        self._config["flight_plan"] = self._flight_plan

        # Write config to yaml
        utils.write_to_yaml(
            self._config, self._config["project_name"], file_name="flight-config",
        )

    def _write_od_pairs(self, origin: str, destinations: List[str]):
        if origin not in self._od_pairs.keys():
            self._od_pairs[origin] = []

        for destination in destinations:
            if destination is not None:
                self._od_pairs[origin].append(destination)

    def _flight_liftoff(self):
        # Run flight_runner
        flight_runner_path = f"{self._config['project_name']}/flight_runner.py"
        subprocess.call(["python", f"{flight_runner_path}"])

    def _get_vpc_if_exists(self):
        for key in self._config.keys():
            if "vpc" in key:
                vpc_dict = {}
                for sub_key in self._config[key]:
                    if "security" in sub_key:
                        sg_ids = []
                        for id_ in self._config[key][sub_key]:
                            sg_ids.append(id_)
                        vpc_dict["security_group_ids"] = sg_ids
                    if "subnet" in sub_key:
                        subnets = []
                        for net in self._config[key][sub_key]:
                            subnets.append(net)
                        vpc_dict["subnets"] = subnets
                self._config["vpc_config"] = vpc_dict
            else:
                pass

    def _get_aircraft_config(self, config=None):
        """Pulls config that has flight pipelines parameters
        """
        if config is None:

            try:
                path = glob.glob(f"./*.yaml")
                path = "".join(path)
                with open(path, "r") as f:
                    config = yaml.safe_load(f)

                return config

            except FileNotFoundError as not_found:
                raise exceptions.NoConfig(
                    """A yaml configuration file is expected in the current directory 
                    if not povided during base class instantiation"""
                )
        else:
            if not isinstance(config, dict):
                raise exceptions.NotofTypeDictionary(
                    """A config dictionary is expected"""
                )

            return config


def generate_empty_plan(extra_context):
    utils.create_sklearn_cutter(extra_context)

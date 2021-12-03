import os
import logging
import json

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.WARNING)


class ConfigBase(object):

    ## Some default variables every config should have
    # only bump up version numbers when merging/commiting into/to master
    MAJOR_VERSION = 0

    # Change this if you make breaking changes that will break compatibility to olde versions
    MINOR_VERSION = 0

    # Changes this of you have new features and/or database scheme changes
    REVISION_VERSION = 0  # Change this for bugfixes
    env_file_vars_override_system_env_vars = False

    def getVersionString(self):
        return (
            self.MAJOR_VERSION + "." + self.MINOR_VERSION + "." + self.REVISION_VERSION
        )

    def __init__(
        self,
        envvars_prefix="CONFIGS_",
        dotenv_files_base_path="./env/",
        env_file_vars_override_system_env_vars=False,
    ):

        self.env_file_vars_override_system_env_vars = (
            env_file_vars_override_system_env_vars
        )
        self._envvars_prefix = envvars_prefix
        self._load_env_files(dotenv_files_base_path)
        for key, value in self._get_config_from_env_vars(envvars_prefix).items():
            # remove prefix from key and add as config attribute
            setattr(self, key[len(envvars_prefix) :], value)
        self._parse_env_variables()

    @classmethod
    def _get_environment_name(cls):
        env = os.environ.get("ENV")
        if env is None:
            return "DEFAULT"
        return env

    @classmethod
    def _get_config_from_env_vars(cls, envvars_prefix) -> dict:
        return {k: v for k, v in os.environ.items() if k.startswith(envvars_prefix)}

    def _load_env_files(self, basepath="./env/"):
        from dotenv import load_dotenv

        still_override = self.env_file_vars_override_system_env_vars
        if self._get_environment_name() != "DEFAULT":
            env_file = os.path.join(basepath, self._get_environment_name() + ".env")
            if os.path.isfile(env_file):
                load_dotenv(
                    env_file, override=self.env_file_vars_override_system_env_vars
                )
                still_override = False
        load_dotenv(
            os.path.join(basepath, "DEFAULT.env"), override=still_override, verbose=True
        )

    def is_number(self, s, is_float=False):
        try:
            if is_float:
                float(s)
                return True
            int(s)
            return True
        except ValueError:
            return False

    def _parse_env_variables(self):
        # dotenv only supports strings, lets cast at least bools stuff to the correct type
        for key, val in self._get_config_from_env_vars(self._envvars_prefix).items():
            attr_key = key[len(self._envvars_prefix) :]
            attr_val = getattr(self, attr_key)
            # Todo: this is ugly, but atm only relaiable way to clean docker-compose values. find better solution
            attr_val = attr_val.strip()
            attr_val = attr_val.strip("'")
            attr_val = attr_val.strip('"')
            attr_val = attr_val.strip("'")
            attr_val = attr_val.strip('"')
            attr_val = attr_val.strip()
            if attr_val in ["True", "true"]:
                # Parse boolean true values
                setattr(self, attr_key, True)
            elif attr_val in ["False", "false"]:
                # Parse boolean false values
                setattr(self, attr_key, False)
            elif self.is_number(attr_val):
                # Parse int values
                setattr(self, attr_key, int(attr_val))
            elif self.is_number(attr_val, is_float=True):
                # parse float values
                setattr(self, attr_key, float(attr_val))
            elif attr_val.strip().startswith(("{", "[")):
                # parse json and cast into dict
                try:
                    attr_val_dq = attr_val.replace(
                        "'", '"'
                    )  # todo: this maybe could result in garbage in some cases. keep eye on and find a better solution
                    attr_dict = json.loads(attr_val_dq)
                    setattr(self, attr_key, attr_dict)
                except ValueError as e:
                    log.warning(
                        "Warning: Invalid JSON? '{ENV_VAL}' in variable '{ENV_KEY}' it Seems like you tried to provide a json/dict value via the environment variable '{ENV_KEY}' but parsing failed. The value will be handled as string.".format(
                            ENV_KEY=attr_key, ENV_VAL=attr_val
                        )
                    )
                    log.error(str(e))
                    pass

    def get(self, key):
        return getattr(self, key)

    def to_dict(self) -> dict:
        dict_ = {}
        attr_names = [
            a
            for a in dir(self)
            if not a.startswith("_") and not callable(getattr(self, a))
        ]
        for attr_n in attr_names:
            dict_[attr_n] = getattr(self, attr_n)
        return dict_


def getConfig(
    dotenv_files_dir_path=None,
    config_classes_pathes=None,
    env_file_vars_override_system_env_vars=False,
):
    import sys
    import os
    import inspect
    import importlib.util

    project_base = os.path.dirname(sys.argv[0])
    if dotenv_files_dir_path is None:
        dotenv_files_dir_path = os.path.join(project_base, "env/")
    if config_classes_pathes is None:
        config_classes_pathes = [os.path.join(project_base, "config.py")]
    config_class_name = ConfigBase._get_environment_name()
    for confclass_path in config_classes_pathes:
        if os.path.isdir(confclass_path):
            raise NotImplementedError(
                "Directories with config class files are not supported yet. please use only one file named config.py"
            )
        elif os.path.isfile(confclass_path):

            spec = importlib.util.spec_from_file_location(
                config_class_name, confclass_path
            )
            config_class_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_class_module)
            for name, obj in inspect.getmembers(config_class_module):
                if inspect.isclass(obj) and name == config_class_name:
                    # return config appropiate to ENV var
                    return obj(
                        dotenv_files_base_path=dotenv_files_dir_path,
                        env_file_vars_override_system_env_vars=env_file_vars_override_system_env_vars,
                    )
            # no appropriate config class found. return DEFAULT
            for name, obj in inspect.getmembers(config_class_module):
                if inspect.isclass(obj) and name == "DEFAULT":
                    return obj(
                        dotenv_files_base_path=dotenv_files_dir_path,
                        env_file_vars_override_system_env_vars=env_file_vars_override_system_env_vars,
                    )
    # no config.py at all?
    raise FileExistsError(
        f"Could not load config: No `config.py`-file at following pathes: {config_classes_pathes}"
    )

import os
import sys

os.environ["CONFIGS_ENV_VALUE"] = "4"


# Load the library local and not the system installed one
if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    # one up because we are in subfolder "smoketest"
    DEV_LIB_DIR = os.path.join(SCRIPT_DIR, "..")
    sys.path.insert(0, os.path.normpath(DEV_LIB_DIR))
# Lets go

from Configs import getConfig


# Default config
config = getConfig(env_file_vars_override_system_env_vars=True)
assert config.MY_JSON == {"KEY1": "True"}
print(config.MY_JSON)
assert config.MY_JSON2 == {"KEY2": "VAL2"}
assert config.ENV_VALUE == 4
assert config.MY_ENVFILE_VAR == 1
assert config.MY_CONFIG_VALUE == 1

os.environ["ENV"] = "DEV"
config = getConfig(env_file_vars_override_system_env_vars=True)
assert config.ENV_VALUE == 4
assert config.MY_ENVFILE_VAR == 2
assert config.MY_CONFIG_VALUE == 2

os.environ["ENV"] = "PROD"
config = getConfig(env_file_vars_override_system_env_vars=True)
assert config.ENV_VALUE == 4
assert config.MY_ENVFILE_VAR == 3
assert config.MY_CONFIG_VALUE == 3

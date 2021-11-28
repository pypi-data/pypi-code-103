from dataclasses import dataclass
from typing import Dict, List

import toml

from piter.config.utils import shrink_dependencies
from piter.config.default import DEFAULT_CONFIG_ENV, DEFAULT_CONFIG_PITER
import piter.cli.output as output


@dataclass
class EnvConfig:
    system_site_packages: bool = DEFAULT_CONFIG_ENV["system_site_packages"]
    clear: bool = DEFAULT_CONFIG_ENV["clear"]
    symlinks: bool = DEFAULT_CONFIG_ENV["symlinks"]
    upgrade: bool = DEFAULT_CONFIG_ENV["upgrade"]
    with_pip: bool = DEFAULT_CONFIG_ENV["with_pip"]
    prompt: str = DEFAULT_CONFIG_ENV["prompt"]
    upgrade_deps: bool = DEFAULT_CONFIG_ENV["upgrade_deps"]
    dependencies: List[str] = DEFAULT_CONFIG_ENV["dependencies"]
    scripts: Dict[str, List[str]] = DEFAULT_CONFIG_ENV["scripts"]
    # install_self: bool = DEFAULT_CONFIG_ENV["install_self"]


@dataclass
class EnvWarning:
    env: str = None
    script: str = None
    line: str = None


class Config:
    def __init__(self, config_dict: dict) -> None:
        self._config_from_file = config_dict

        self.env_root: str = self.setting_from_config_or_default("env_root")

        self.env: Dict[str, EnvConfig] = None

        if "env" in self._config_from_file.keys():
            self.env: Dict[str, EnvConfig] = {}
            if isinstance(self._config_from_file["env"], dict):
                for env_name, env_config in self._config_from_file["env"].items():
                    if "prompt" not in env_config.keys():
                        env_config["prompt"] = env_name

                    self.env[env_name] = EnvConfig(**env_config)
                    if (
                        self.env[env_name].dependencies
                        and len(self.env[env_name].dependencies) > 0
                    ):
                        self.env[env_name].dependencies = shrink_dependencies(
                            self.env[env_name].dependencies
                        )

                    if isinstance(self.env[env_name].scripts, dict):
                        for script_name, script in self.env[env_name].scripts.items():
                            if isinstance(script, str):
                                self.env[env_name].scripts[script_name] = [script]

    def to_toml(self) -> str:
        output = {
            "tools": {
                "piter": {
                    "env_root": self.env_root,
                    "dependencies": self.dependencies,
                    "env": {
                        env_name: env_config.__dict__
                        for env_name, env_config in self.env.items()
                    },
                }
            }
        }
        return toml.dumps(output)

    def get_warnings(self) -> List[EnvWarning]:
        result = []

        for env_name, env in self.env.items():
            for script_name, script_lines in env.scripts.items():
                for script_line in script_lines:
                    # TODO: add link to documentation
                    if "pip install" in script_line or "pip3 install" in script_line:
                        result.append(
                            EnvWarning(
                                env=env_name,
                                script=script_name,
                                line=f"Script has line with {output.script('pip install')} in it. It may cause issues: https://docs.link/scripts_caveats. Consider using {output.script('piter install')} instead",
                            )
                        )

                    # TODO: add link to documentation
                    if ".sh" in script_line:
                        result.append(
                            EnvWarning(
                                env=env_name,
                                script=script_name,
                                line=f"Script has line with {output.script('*.sh')} file in it. It may cause issues: https://docs.link/scripts_caveats",
                            )
                        )

        return result

    def setting_from_config_or_default(self, setting_name: str):
        try:
            return self._config_from_file[setting_name]
        except:
            return DEFAULT_CONFIG_PITER[setting_name]

    @property
    def dependencies(self) -> list:
        try:
            return shrink_dependencies(self._config_from_file["dependencies"])
        except:
            return None

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import config as ext_config_mod
    from .core import Session


class ConfigManager:
    """
    Temporary class
    When all content is moved to the data provider style,
    this class and module will be deleted
    """

    def get_api_config(
        self,
        api_name: str,
        session: "Session",
    ) -> "ext_config_mod.ConfigurationSet":
        config = session.config
        api_config = config.get(f"apis.{api_name}")
        return api_config


config_mgr: ConfigManager = ConfigManager()

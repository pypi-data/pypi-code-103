from typing import List


class WebserviceConfiguration:
    def __init__(
        self,
        environment_name: str,
        service_name: str,
        source_directory: str,
        entry_script: str,
        model_names: List[str] = [],
    ):
        self.environment_name = environment_name
        self.service_name = service_name
        self.source_directory = source_directory
        self.entry_script = entry_script
        self.model_names = model_names

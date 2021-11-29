import os
import json

from artefacts import config


class Context(object):
    def __init__(self, config=config):
        self.config = config

    def get(self, *args, **kwargs):
        return self.config.context_data.get(*args, **kwargs)

    def update(self, **kwargs):
        self.config.context_data.update(**kwargs)

    def load(self, artifact, target, allow_missing=False):
        artifact_path = os.path.join(target, artifact + ".json")

        if allow_missing and not os.path.exists(artifact_path):
            return
        else:
            with open(artifact_path, "r") as fh:
                self.config.context_data[f"raw_{artifact}"] = json.load(fh)

    def parse(self, artifact, parser, allow_missing=False):
        if allow_missing and f"raw_{artifact}" not in self.config.context_data:
            return
        else:
            self.config.context_data[f"parsed_{artifact}"] = parser(
                **self.config.context_data[f"raw_{artifact}"]
            )

    @property
    def manifest(self):
        try:
            return self.config.context_data["parsed_manifest"]
        except KeyError as err:
            raise KeyError("No parsed manifest available").with_traceback(
                err.__traceback__
            )

    @property
    def catalog(self):
        try:
            return self.config.context_data["parsed_catalog"]
        except KeyError as err:
            raise KeyError("No parsed catalog available").with_traceback(
                err.__traceback__
            )

    @property
    def run_results(self):
        try:
            return self.config.context_data["parsed_run_results"]
        except KeyError as err:
            raise KeyError("No parsed run_results available").with_traceback(
                err.__traceback__
            )

    @property
    def sources(self):
        try:
            return self.config.context_data["parsed_sources"]
        except KeyError as err:
            raise KeyError("No parsed sources available").with_traceback(
                err.__traceback__
            )

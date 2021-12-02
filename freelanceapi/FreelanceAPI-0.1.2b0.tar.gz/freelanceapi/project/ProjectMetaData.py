from abc import ABC, abstractproperty


class ProjectMetaData(ABC):

    @abstractproperty
    def get_keys(self):
        pass

    @abstractproperty
    def get_expected_key(self):
        pass


class PbNode(ProjectMetaData):
    keys: list[str] = ["KW", "NA", "MT", "FN"]
    expected_key = "[PB:NODE]"

    @property
    def get_keys(self) -> list[list]:
        return self.keys

    @property
    def get_expected_key(self) -> str:
        return self.expected_key

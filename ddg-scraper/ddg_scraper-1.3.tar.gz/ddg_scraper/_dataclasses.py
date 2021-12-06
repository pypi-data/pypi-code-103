from dataclasses import dataclass, asdict


@dataclass
class Result:
    title: str
    description: str
    url: str
    icon_url: str

    def as_dict(self):
        """Converts the dataclass to a `dict` object and returns it."""
        return asdict(self)
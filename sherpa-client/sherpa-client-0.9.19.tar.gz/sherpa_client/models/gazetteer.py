from typing import Any, Dict, Type, TypeVar

import attr

from ..models.gazetteer_parameters import GazetteerParameters

T = TypeVar("T", bound="Gazetteer")


@attr.s(auto_attribs=True)
class Gazetteer:
    """ """

    name: str
    label: str
    engine: str
    running: bool
    timestamp: int
    duration: int
    uptodate: bool
    models: int
    parameters: GazetteerParameters

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        label = self.label
        engine = self.engine
        running = self.running
        timestamp = self.timestamp
        duration = self.duration
        uptodate = self.uptodate
        models = self.models
        parameters = self.parameters.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "label": label,
                "engine": engine,
                "running": running,
                "timestamp": timestamp,
                "duration": duration,
                "uptodate": uptodate,
                "models": models,
                "parameters": parameters,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        label = d.pop("label")

        engine = d.pop("engine")

        running = d.pop("running")

        timestamp = d.pop("timestamp")

        duration = d.pop("duration")

        uptodate = d.pop("uptodate")

        models = d.pop("models")

        parameters = GazetteerParameters.from_dict(d.pop("parameters"))

        gazetteer = cls(
            name=name,
            label=label,
            engine=engine,
            running=running,
            timestamp=timestamp,
            duration=duration,
            uptodate=uptodate,
            models=models,
            parameters=parameters,
        )

        return gazetteer

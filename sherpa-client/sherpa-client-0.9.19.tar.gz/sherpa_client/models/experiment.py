from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.experiment_parameters import ExperimentParameters
from ..models.report import Report
from ..types import UNSET, Unset

T = TypeVar("T", bound="Experiment")


@attr.s(auto_attribs=True)
class Experiment:
    """ """

    name: str
    label: str
    engine: str
    running: bool
    quality: int
    timestamp: int
    duration: int
    uptodate: bool
    models: int
    parameters: ExperimentParameters
    favorite: Union[Unset, bool] = UNSET
    report: Union[Unset, Report] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        label = self.label
        engine = self.engine
        running = self.running
        quality = self.quality
        timestamp = self.timestamp
        duration = self.duration
        uptodate = self.uptodate
        models = self.models
        parameters = self.parameters.to_dict()

        favorite = self.favorite
        report: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.report, Unset):
            report = self.report.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "label": label,
                "engine": engine,
                "running": running,
                "quality": quality,
                "timestamp": timestamp,
                "duration": duration,
                "uptodate": uptodate,
                "models": models,
                "parameters": parameters,
            }
        )
        if favorite is not UNSET:
            field_dict["favorite"] = favorite
        if report is not UNSET:
            field_dict["report"] = report

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        label = d.pop("label")

        engine = d.pop("engine")

        running = d.pop("running")

        quality = d.pop("quality")

        timestamp = d.pop("timestamp")

        duration = d.pop("duration")

        uptodate = d.pop("uptodate")

        models = d.pop("models")

        parameters = ExperimentParameters.from_dict(d.pop("parameters"))

        favorite = d.pop("favorite", UNSET)

        _report = d.pop("report", UNSET)
        report: Union[Unset, Report]
        if isinstance(_report, Unset):
            report = UNSET
        else:
            report = Report.from_dict(_report)

        experiment = cls(
            name=name,
            label=label,
            engine=engine,
            running=running,
            quality=quality,
            timestamp=timestamp,
            duration=duration,
            uptodate=uptodate,
            models=models,
            parameters=parameters,
            favorite=favorite,
            report=report,
        )

        return experiment

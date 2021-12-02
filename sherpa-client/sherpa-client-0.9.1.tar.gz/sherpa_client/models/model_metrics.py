from typing import Any, Dict, List, Type, TypeVar, cast

import attr

from ..models.engine_config import EngineConfig
from ..models.model_metrics_options import ModelMetricsOptions
from ..models.report import Report

T = TypeVar("T", bound="ModelMetrics")


@attr.s(auto_attribs=True)
class ModelMetrics:
    """ """

    name: str
    lang: str
    timestamp: int
    timestamp_end: int
    quality: float
    status: str
    engine: str
    options: ModelMetricsOptions
    classes: List[str]
    report: Report
    config: EngineConfig

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        lang = self.lang
        timestamp = self.timestamp
        timestamp_end = self.timestamp_end
        quality = self.quality
        status = self.status
        engine = self.engine
        options = self.options.to_dict()

        classes = self.classes

        report = self.report.to_dict()

        config = self.config.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "lang": lang,
                "timestamp": timestamp,
                "timestamp_end": timestamp_end,
                "quality": quality,
                "status": status,
                "engine": engine,
                "options": options,
                "classes": classes,
                "report": report,
                "config": config,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        lang = d.pop("lang")

        timestamp = d.pop("timestamp")

        timestamp_end = d.pop("timestamp_end")

        quality = d.pop("quality")

        status = d.pop("status")

        engine = d.pop("engine")

        options = ModelMetricsOptions.from_dict(d.pop("options"))

        classes = cast(List[str], d.pop("classes"))

        report = Report.from_dict(d.pop("report"))

        config = EngineConfig.from_dict(d.pop("config"))

        model_metrics = cls(
            name=name,
            lang=lang,
            timestamp=timestamp,
            timestamp_end=timestamp_end,
            quality=quality,
            status=status,
            engine=engine,
            options=options,
            classes=classes,
            report=report,
            config=config,
        )

        return model_metrics

from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.engine_config import EngineConfig
from ..models.quality_figures import QualityFigures
from ..models.report_classes import ReportClasses
from ..types import UNSET, Unset

T = TypeVar("T", bound="Report")


@attr.s(auto_attribs=True)
class Report:
    """ """

    classes: ReportClasses
    micro_avg: QualityFigures
    macro_avg: Union[Unset, QualityFigures] = UNSET
    weighted_avg: Union[Unset, QualityFigures] = UNSET
    samples_avg: Union[Unset, QualityFigures] = UNSET
    config: Union[Unset, EngineConfig] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        classes = self.classes.to_dict()

        micro_avg = self.micro_avg.to_dict()

        macro_avg: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.macro_avg, Unset):
            macro_avg = self.macro_avg.to_dict()

        weighted_avg: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.weighted_avg, Unset):
            weighted_avg = self.weighted_avg.to_dict()

        samples_avg: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.samples_avg, Unset):
            samples_avg = self.samples_avg.to_dict()

        config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "classes": classes,
                "microAvg": micro_avg,
            }
        )
        if macro_avg is not UNSET:
            field_dict["macroAvg"] = macro_avg
        if weighted_avg is not UNSET:
            field_dict["weightedAvg"] = weighted_avg
        if samples_avg is not UNSET:
            field_dict["samplesAvg"] = samples_avg
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        classes = ReportClasses.from_dict(d.pop("classes"))

        micro_avg = QualityFigures.from_dict(d.pop("microAvg"))

        _macro_avg = d.pop("macroAvg", UNSET)
        macro_avg: Union[Unset, QualityFigures]
        if isinstance(_macro_avg, Unset):
            macro_avg = UNSET
        else:
            macro_avg = QualityFigures.from_dict(_macro_avg)

        _weighted_avg = d.pop("weightedAvg", UNSET)
        weighted_avg: Union[Unset, QualityFigures]
        if isinstance(_weighted_avg, Unset):
            weighted_avg = UNSET
        else:
            weighted_avg = QualityFigures.from_dict(_weighted_avg)

        _samples_avg = d.pop("samplesAvg", UNSET)
        samples_avg: Union[Unset, QualityFigures]
        if isinstance(_samples_avg, Unset):
            samples_avg = UNSET
        else:
            samples_avg = QualityFigures.from_dict(_samples_avg)

        _config = d.pop("config", UNSET)
        config: Union[Unset, EngineConfig]
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = EngineConfig.from_dict(_config)

        report = cls(
            classes=classes,
            micro_avg=micro_avg,
            macro_avg=macro_avg,
            weighted_avg=weighted_avg,
            samples_avg=samples_avg,
            config=config,
        )

        return report

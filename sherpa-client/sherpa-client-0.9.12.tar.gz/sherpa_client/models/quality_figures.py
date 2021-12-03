from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="QualityFigures")


@attr.s(auto_attribs=True)
class QualityFigures:
    """ """

    precision: float
    recall: float
    f1: float
    support: int
    roc_auc: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        precision = self.precision
        recall = self.recall
        f1 = self.f1
        support = self.support
        roc_auc = self.roc_auc

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "support": support,
            }
        )
        if roc_auc is not UNSET:
            field_dict["roc_auc"] = roc_auc

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        precision = d.pop("precision")

        recall = d.pop("recall")

        f1 = d.pop("f1")

        support = d.pop("support")

        roc_auc = d.pop("roc_auc", UNSET)

        quality_figures = cls(
            precision=precision,
            recall=recall,
            f1=f1,
            support=support,
            roc_auc=roc_auc,
        )

        return quality_figures

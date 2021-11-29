import enum
from typing import Optional
from uuid import UUID

from myst.connectors.model_connector import ModelConnector


@enum.unique
class GroupName(str, enum.Enum):
    FEATURES = "features"
    TARGETS = "targets"
    SAMPLE_WEIGHTS = "sample_weights"


class XGBoost(ModelConnector):
    def __init__(
        self,
        num_boost_round: Optional[int] = None,
        max_depth: Optional[int] = None,
        min_child_weight: Optional[int] = None,
        learning_rate: Optional[float] = None,
        subsample: Optional[float] = None,
        colsample_bytree: Optional[float] = None,
        colsample_bylevel: Optional[float] = None,
        colsample_bynode: Optional[float] = None,
        gamma: Optional[float] = None,
        reg_alpha: Optional[float] = None,
        reg_lambda: Optional[float] = None,
    ) -> None:
        super().__init__(
            uuid=UUID("b78ff94a-27b1-4986-a88a-536661239bb2"),
            parameters=dict(
                num_boost_round=num_boost_round,
                max_depth=max_depth,
                min_child_weight=min_child_weight,
                learning_rate=learning_rate,
                subsample=subsample,
                colsample_bytree=colsample_bytree,
                colsample_bylevel=colsample_bylevel,
                colsample_bynode=colsample_bynode,
                gamma=gamma,
                reg_alpha=reg_alpha,
                reg_lambda=reg_lambda,
            ),
        )

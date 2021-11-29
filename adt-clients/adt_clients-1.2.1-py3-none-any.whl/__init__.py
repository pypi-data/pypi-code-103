__version__ = "1.2.1"

__all__ = [
    "AnalyticDatasetClient",
    "AnalyticDatasetModel",
    "AnalyticDatasetDefinitionClient",
    "AnalyticDatasetDefinitionModel",
    "AnalyticDatasetMergeRequestModel",
    "JoinType",
    "ColumnSelectionType",
    "Granularity",
    "AnalyticDatasetFormat",
]

try:
    # Attempts to import the client class
    # Allowed to fail importing so the package metadata can be read for building
    from .analytic_dataset_client import AnalyticDatasetClient
    from .analytic_dataset_definition_client import AnalyticDatasetDefinitionClient
    from .models import (
        AnalyticDatasetModel,
        AnalyticDatasetDefinitionModel,
        AnalyticDatasetMergeRequestModel,
        Granularity,
        AnalyticDatasetFormat,
        JoinType,
        ColumnSelectionType,
    )
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    pass  # pragma: no cover

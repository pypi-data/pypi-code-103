"""Generated implementation of feature_store_run."""

# WARNING DO NOT EDIT
# This code was generated from feature-store-run.mcn

from __future__ import annotations

import abc  # noqa: F401
import dataclasses  # noqa: F401
import datetime  # noqa: F401
import enum  # noqa: F401
import isodate  # noqa: F401
import json  # noqa: F401
import jsonschema  # noqa: F401
import logging  # noqa: F401
import typing  # noqa: F401
import uuid  # noqa: F401

from ..commit import CommitId
from ..feature_id import FeatureId
from ..feature_store import FeatureStoreId, FeatureStoreVersionId
from ..job_metrics import JobMetrics
from ..jobs import FeatureStoreRunId, RunStatus
from ..schedule import ScheduleState
from ..summary_statistics import SummaryStatistics


@dataclasses.dataclass(frozen=True)
class FeatureStoreRun:
    """Details of a feature store run.
    
    Args:
        id (FeatureStoreRunId): A data field.
        created (datetime.datetime): A data field.
        featureStoreId (FeatureStoreId): A data field.
        featureStoreVersionId (FeatureStoreVersionId): A data field.
        commitId (CommitId): A data field.
        runStartDate (datetime.date): A data field.
        runEndDate (datetime.date): A data field.
        status (RunStatus): A data field.
        errorMessage (typing.Optional[str]): A data field.
        scheduleState (typing.Optional[ScheduleState]): A data field.
        statistics (typing.Optional[FeatureStoreExecutionStatistics]): A data field.
    """
    
    id: FeatureStoreRunId
    created: datetime.datetime
    featureStoreId: FeatureStoreId
    featureStoreVersionId: FeatureStoreVersionId
    commitId: CommitId
    runStartDate: datetime.date
    runEndDate: datetime.date
    status: RunStatus
    errorMessage: typing.Optional[str]
    scheduleState: typing.Optional[ScheduleState]
    statistics: typing.Optional[FeatureStoreExecutionStatistics]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FeatureStoreRun data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": FeatureStoreRunId.json_schema(),
                "created": {
                    "type": "string",
                    "format": "date-time"
                },
                "featureStoreId": FeatureStoreId.json_schema(),
                "featureStoreVersionId": FeatureStoreVersionId.json_schema(),
                "commitId": CommitId.json_schema(),
                "runStartDate": {
                    "type": "string",
                    "format": "date"
                },
                "runEndDate": {
                    "type": "string",
                    "format": "date"
                },
                "status": RunStatus.json_schema(),
                "errorMessage": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "scheduleState": {
                    "oneOf": [
                        {"type": "null"},
                        ScheduleState.json_schema(),
                    ]
                },
                "statistics": {
                    "oneOf": [
                        {"type": "null"},
                        FeatureStoreExecutionStatistics.json_schema(),
                    ]
                }
            },
            "required": [
                "id",
                "created",
                "featureStoreId",
                "featureStoreVersionId",
                "commitId",
                "runStartDate",
                "runEndDate",
                "status",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureStoreRun:
        """Validate and parse JSON data into an instance of FeatureStoreRun.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureStoreRun.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureStoreRun(
                id=FeatureStoreRunId.from_json(data["id"]),
                created=isodate.parse_datetime(data["created"]),
                featureStoreId=FeatureStoreId.from_json(data["featureStoreId"]),
                featureStoreVersionId=FeatureStoreVersionId.from_json(data["featureStoreVersionId"]),
                commitId=CommitId.from_json(data["commitId"]),
                runStartDate=datetime.date.fromisoformat(data["runStartDate"]),
                runEndDate=datetime.date.fromisoformat(data["runEndDate"]),
                status=RunStatus.from_json(data["status"]),
                errorMessage=(lambda v: v and str(v))(data.get("errorMessage", None)),
                scheduleState=(
                    lambda v: v and ScheduleState.from_json(v)
                )(
                    data.get("scheduleState", None)
                ),
                statistics=(
                    lambda v: v and FeatureStoreExecutionStatistics.from_json(v)
                )(
                    data.get("statistics", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FeatureStoreRun",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "id": self.id.to_json(),
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "featureStoreId": self.featureStoreId.to_json(),
            "featureStoreVersionId": self.featureStoreVersionId.to_json(),
            "commitId": self.commitId.to_json(),
            "runStartDate": self.runStartDate.isoformat(),
            "runEndDate": self.runEndDate.isoformat(),
            "status": self.status.to_json(),
            "errorMessage": (lambda v: v and str(v))(self.errorMessage),
            "scheduleState": (lambda v: v and v.to_json())(self.scheduleState),
            "statistics": (lambda v: v and v.to_json())(self.statistics)
        }


@dataclasses.dataclass(frozen=True)
class FeatureStoreExecutionStatistics:
    """Statistics calculated during a feature store run.
    
    Args:
        base (ExecutionStatistics): A data field.
        rowCount (typing.Optional[int]): A data field.
        featureStatistics (typing.List[SummaryStatistics]): A data field.
        jobMetrics (typing.Optional[JobMetrics]): A data field.
    """
    
    base: ExecutionStatistics
    rowCount: typing.Optional[int]
    featureStatistics: typing.List[SummaryStatistics]
    jobMetrics: typing.Optional[JobMetrics]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FeatureStoreExecutionStatistics data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "base": ExecutionStatistics.json_schema(),
                "rowCount": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "integer"},
                    ]
                },
                "featureStatistics": {
                    "type": "array",
                    "item": SummaryStatistics.json_schema()
                },
                "jobMetrics": {
                    "oneOf": [
                        {"type": "null"},
                        JobMetrics.json_schema(),
                    ]
                }
            },
            "required": [
                "base",
                "featureStatistics",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureStoreExecutionStatistics:
        """Validate and parse JSON data into an instance of FeatureStoreExecutionStatistics.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureStoreExecutionStatistics.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureStoreExecutionStatistics(
                base=ExecutionStatistics.from_json(data["base"]),
                rowCount=(lambda v: v and int(v))(data.get("rowCount", None)),
                featureStatistics=[SummaryStatistics.from_json(v) for v in data["featureStatistics"]],
                jobMetrics=(
                    lambda v: v and JobMetrics.from_json(v)
                )(
                    data.get("jobMetrics", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FeatureStoreExecutionStatistics",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "base": self.base.to_json(),
            "rowCount": (lambda v: v and v)(self.rowCount),
            "featureStatistics": [v.to_json() for v in self.featureStatistics],
            "jobMetrics": (lambda v: v and v.to_json())(self.jobMetrics)
        }


@dataclasses.dataclass(frozen=True)
class ExecutionStatistics:
    """Statistics about a feature store run itself.
    
    Args:
        executionStartTime (datetime.datetime): A data field.
        executionEndTime (typing.Optional[datetime.datetime]): A data field.
    """
    
    executionStartTime: datetime.datetime
    executionEndTime: typing.Optional[datetime.datetime]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ExecutionStatistics data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "executionStartTime": {
                    "type": "string",
                    "format": "date-time"
                },
                "executionEndTime": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date-time"},
                    ]
                }
            },
            "required": [
                "executionStartTime",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ExecutionStatistics:
        """Validate and parse JSON data into an instance of ExecutionStatistics.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ExecutionStatistics.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ExecutionStatistics(
                executionStartTime=isodate.parse_datetime(data["executionStartTime"]),
                executionEndTime=(
                    lambda v: v and isodate.parse_datetime(v)
                )(
                    data.get("executionEndTime", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing ExecutionStatistics",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "executionStartTime": self.executionStartTime.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "executionEndTime": (lambda v: v and v.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))(self.executionEndTime)
        }


@dataclasses.dataclass(frozen=True)
class FeatureCompletedRunsDays:
    """Number of completed runs in days for a feature.
    
    Args:
        featureId (FeatureId): A data field.
        runsDaysCompleted (int): A data field.
    """
    
    featureId: FeatureId
    runsDaysCompleted: int
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FeatureCompletedRunsDays data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "featureId": FeatureId.json_schema(),
                "runsDaysCompleted": {
                    "type": "integer"
                }
            },
            "required": [
                "featureId",
                "runsDaysCompleted",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureCompletedRunsDays:
        """Validate and parse JSON data into an instance of FeatureCompletedRunsDays.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureCompletedRunsDays.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureCompletedRunsDays(
                featureId=FeatureId.from_json(data["featureId"]),
                runsDaysCompleted=int(data["runsDaysCompleted"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FeatureCompletedRunsDays",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "featureId": self.featureId.to_json(),
            "runsDaysCompleted": int(self.runsDaysCompleted)
        }

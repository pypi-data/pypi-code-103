from uuid import UUID

from myst.models.timing import AbsoluteOrRelativeTiming
from myst.resources.resource import Resource


class Policy(Resource):
    """Describes when and over what natural time range to run a particular type of job for a node.

    Attributes:
        creator: the identifier of the user who created this resource
        schedule_timing: when the policy is scheduled to run, whether recurrent or once
        active: whether this policy is currently in effect
        node: the identifier of the node this policy applies to
        start_timing: the beginning of the natural time range for which this policy applies, inclusive
        end_timing: the end of the natural time range for which this policy applies, exclusive
    """

    creator: UUID
    schedule_timing: AbsoluteOrRelativeTiming
    active: bool
    node: UUID
    start_timing: AbsoluteOrRelativeTiming
    end_timing: AbsoluteOrRelativeTiming


class ModelFitPolicy(Policy):
    """Describes when and over what natural time range to run a fit job on a model."""


class TimeSeriesRunPolicy(Policy):
    """Describes when and over what natural time range to run a fit job on a model."""

from typing import Dict, Iterator, Optional

from boto3.session import Session

from cfp.exceptions import ParameterStoreResolutionError
from cfp.resolvers.resolver import Resolver
from cfp.sources import FromParameterStore
from cfp.types import ApiParameter, StackParameterKey


class ParameterStoreResolver(Resolver[FromParameterStore]):
    def __init__(self) -> None:
        # Map of Parameter Store names to CloudFormation names:
        self._map: Dict[str, StackParameterKey] = {}

        # We can assume that this resolver will handle only one region, but we
        # won't know what it is until we start reading sources:
        self._region: Optional[str] = None

        # Since we know this resolver will handle only one region, we can assume
        # that zero or one boto3 sessions will be encountered too:
        self._session: Optional[Session] = None

    def _consider_region(self, region: Optional[str]) -> None:
        if self._region is not None and self._region != region:
            raise ParameterStoreResolutionError(f"{self._region} != {region}")
        self._region = self._region or region

    def _consider_session(self, session: Optional[Session]) -> None:
        if self._session and session and self._session is not session:
            raise ParameterStoreResolutionError("boto3 session conflict")
        self._session = self._session or session

    def _get_session(self) -> Session:
        self._session = self._session or (
            Session(region_name=self._region) if self._region else Session()
        )
        return self._session

    def _queue(self, key: StackParameterKey, source: FromParameterStore) -> None:
        self._consider_region(source.region)
        self._consider_session(source.session)
        self._map[source.name] = key

    def resolve(self) -> Iterator[ApiParameter]:
        """
        Invokes the queued resolution tasks and returns an iterator of the
        values.
        """

        session = self._get_session()
        ssm = session.client("ssm")  # pyright: reportUnknownMemberType=false
        response = ssm.get_parameters(Names=[name for name in self._map])
        invalid_params = response.get("InvalidParameters", [])

        if invalid_params:
            invalid = ", ".join(invalid_params)
            raise ParameterStoreResolutionError(
                f"Systems Manager failed to resolve some parameters: {invalid}"
            )

        for p in response["Parameters"]:
            if "Name" not in p or "Value" not in p:
                continue

            yield ApiParameter(
                ParameterKey=self._map[p["Name"]],
                ParameterValue=p["Value"],
            )

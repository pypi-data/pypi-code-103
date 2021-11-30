from typing import Any, Dict, Optional, Tuple

import attr

CONFIG_VERSION = (1, 0)


@attr.s(slots=True)
class AuthConfig:
    auth_type: str = attr.ib(kw_only=True, default="None")
    username: Optional[str] = attr.ib(kw_only=True, default=None)
    password: Optional[str] = attr.ib(kw_only=True, default=None)
    api_key: Optional[str] = attr.ib(kw_only=True, default=None)
    token: Optional[str] = attr.ib(kw_only=True, default=None)


@attr.s(slots=True)
class PlanConfig:
    """Test plan configuration."""

    target_url: str = attr.ib(kw_only=True)
    spec_path: Optional[str] = attr.ib(kw_only=True, default=None)
    test_plan_path: Optional[str] = attr.ib(kw_only=True, default=None)
    # This is deprecated and should be removed in next version.
    auth: Optional[Tuple[str, str]] = attr.ib(kw_only=True, default=None)
    auth_type: Optional[str] = attr.ib(kw_only=True, default=None)
    report_to_saas: bool = attr.ib(kw_only=True, default=True)
    auth_config: AuthConfig = attr.ib(kw_only=True)
    headers: Dict[str, str] = attr.ib(kw_only=True, factory=dict)
    env_file_path: Optional[str] = attr.ib(kw_only=True, default=None)
    module_specific_config: Dict[str, Any] = attr.ib(kw_only=True, factory=dict)
    # Current config version
    version = CONFIG_VERSION

    # Shortcut to convert PlanConfig to dictionary
    asdict = attr.asdict

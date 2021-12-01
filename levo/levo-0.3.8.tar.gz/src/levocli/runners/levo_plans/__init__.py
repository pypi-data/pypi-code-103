"""The test module which communicates with Levo platform, gets the tests, runs them,
and reports the results back to Levo.
"""
import importlib
import os
import pathlib
import tempfile
from typing import Callable, Generator, List, Tuple

import click
from levo_commons.config import AuthConfig, PlanConfig
from levo_commons.events import InternalError
from levo_commons.utils import syspath_prepend

from ... import events
from ...config import TestPlanCommandConfig
from ...handlers import EventHandler
from ...logger import get_logger
from ...login import get_config_or_exit
from ...utils import format_exception
from . import local, remote
from .context import ExecutionContext
from .event_handler import LevoPlansEventHandler
from .logging import build_plan_logger
from .models import Plan
from .reporters.default import TestPlanConsoleOutputHandler
from .reporters.report_portal import TestPlanReportPortalHandler

TEST_PLAN_RUN_METHOD_NAME = "run_test_plan"

log = get_logger(__name__)


class PlanEventStream(events.EventStream):
    def stop(self) -> None:
        # TODO. Implement interruption
        raise NotImplementedError


def get_test_plan_entrypoint(module_path: str) -> Callable:
    """Load test case module & extract its entrypoint."""
    module = importlib.import_module(module_path)
    return getattr(module, TEST_PLAN_RUN_METHOD_NAME)


def should_process(path: pathlib.Path) -> bool:
    return path.is_dir() and path.name != "__pycache__"


def into_event_stream(plan: Plan, config: PlanConfig) -> events.EventStream:
    """Create a stream of Levo events."""
    return PlanEventStream(iter_cases(plan, config), lambda x: x)


def get_internal_error_event(exc: Exception) -> InternalError:
    exception_type = f"{exc.__class__.__module__}.{exc.__class__.__qualname__}"
    message = f"Could not run the test case."
    exception = format_exception(exc)
    exception_with_traceback = format_exception(exc, include_traceback=True)
    return InternalError(
        message=message,
        exception_type=exception_type,
        exception=exception,
        exception_with_traceback=exception_with_traceback,
        is_terminal=False,
    )


def iter_cases(plan: Plan, config: PlanConfig) -> Generator:
    # From the levo test framework, import levo.run_test_plan and run that with PlanConfig
    entrypoint = get_test_plan_entrypoint("levo")
    try:
        yield from entrypoint(config)
    except Exception as e:
        # This means we failed to run the test plan, which is considered as an error.
        # Hence, yield an error event here with details.
        yield get_internal_error_event(e)


def get_auth_config(input_config: TestPlanCommandConfig):
    if not input_config.auth:
        return None

    if input_config.auth_type.lower() == "basic":
        auth: Tuple[str, str] = input_config.auth
        return AuthConfig(auth_type="basic", username=auth[0], password=auth[1])
    elif input_config.auth_type.lower() == "token":
        return AuthConfig(auth_type="token", token=input_config.auth)
    elif input_config.auth_type.lower() == "apikey":
        return AuthConfig(auth_type="apikey", token=input_config.auth)
    else:
        msg = f"Unknown auth_type: {input_config.auth_type}"
        click.secho(msg, fg="red")
        raise click.UsageError(msg)


def cli_entrypoint(input_config: TestPlanCommandConfig):
    config = get_config_or_exit()
    auth_config = config.auth
    # Get workspace_id if we need to report to SaaS.
    # TODO: If we are not reporting to SaaS, for now we set this to empty string but
    # eventually we should figure out a better way to do this.
    workspace_id = (
        config.workspace_id
        if input_config.report_to_saas and config.workspace_id
        else ""
    )
    if input_config.test_plans_catalog:
        if not input_config.plan_name:
            raise click.UsageError(
                "Please specify a plan name when using --test-plans-catalog."
            )

        plan = local.get_plan(
            plan_name=input_config.plan_name,
            catalog=input_config.test_plans_catalog,
            workspace_id=workspace_id,
        )
        if plan is None:
            raise click.UsageError(
                f"Can not find a plan with LRN {input_config.plan_lrn}"
            )
    else:
        plan = remote.get_plan(
            plan_lrn=input_config.plan_lrn,
            workspace_id=workspace_id,
            local_dir=pathlib.Path(tempfile.mkdtemp()),
            authz_header=auth_config.token_type + " " + auth_config.access_token,
        )

    if not plan.name:
        click.secho("Could not resolve test plan name.", fg="red")
        raise click.exceptions.Exit(1)

    config = PlanConfig(
        spec_path="",  # This should be optional ideally.
        test_plan_path=os.path.join(plan.catalog, plan.name),
        target_url=input_config.target_url,
        auth=input_config.auth,
        auth_type=input_config.auth_type,
        report_to_saas=input_config.report_to_saas,
        auth_config=get_auth_config(input_config) if input_config.auth else None,
        env_file_path=input_config.env_file_path,
        headers=input_config.headers,
    )
    context = ExecutionContext(
        plan=plan, show_errors_tracebacks=input_config.show_errors_tracebacks
    )

    logger = build_plan_logger(plan.name, context)
    context.logger = logger

    reporters: List[EventHandler] = [TestPlanConsoleOutputHandler()]
    # Report the test results to ReportPortal, if enabled.
    if input_config.report_to_saas:
        reporters.append(TestPlanReportPortalHandler(plan, auth_config.access_token))

    reporter_names = [r.get_name() for r in reporters]
    log.debug(f"Initialized the reporters: {reporter_names}")

    handler = LevoPlansEventHandler(reporters=reporters, config=input_config)

    with syspath_prepend(plan.catalog):
        event_stream = into_event_stream(plan, config)
        return events.handle([handler], event_stream, context)


def export_plan(plan_lrn: str, local_dir: str):
    config = get_config_or_exit()
    auth_config = config.auth
    remote.get_plan(
        plan_lrn=plan_lrn,
        workspace_id=config.workspace_id if config.workspace_id else "",
        local_dir=pathlib.Path(local_dir),
        authz_header=auth_config.token_type + " " + auth_config.access_token,
    )
    click.echo(f"Exported the test plan to {local_dir}")

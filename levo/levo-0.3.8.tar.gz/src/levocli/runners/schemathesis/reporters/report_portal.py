import base64
import enum
import json
import time
import traceback
from typing import Dict, List, Optional, Union, cast

import attr
import click
import levo_commons.status
from levo_commons import events
from reportportal_client import ReportPortalService
from schemathesis.constants import CodeSampleStyle

from ....apitesting.runs.api_test_runs_pb2 import (  # type: ignore
    CATEGORY_FAILED,
    CATEGORY_SUCCESS,
    ApiEndpointTestsCategory,
)
from ....env_constants import TEST_RUNS_SERVICE_URL
from ....handlers import EventHandler
from ....logger import get_logger
from ....utils import fetch_schema_as_lines
from ...utils import get_formatted_request_response
from ..context import EndpointExecutionContext, ExecutionContext
from ..models import (
    BeforeExecutionPayload,
    FinishedPayload,
    Response,
    SerializedCase,
    SerializedCheck,
    SerializedError,
    SerializedTestResult,
    Status,
    get_unique_failures,
)
from .default import get_summary_message_parts

log = get_logger(__name__)

DISABLE_SCHEMA_VALIDATION_MESSAGE = (
    "\nYou can disable input schema validation with --validate-schema=false "
    "command-line option\nIn this case, Schemathesis cannot guarantee proper"
    " behavior during the test run"
)

STATUS_DICT = {
    Status.success: "PASSED",
    Status.failure: "FAILED",
    Status.error: "ERRORED",
}


class HandlerState(enum.Enum):
    """Different states for ReportPortal handler lifecycle."""

    # Instance is created. The default state
    NEW = enum.auto()
    # Launch started, ready to handle events
    ACTIVE = enum.auto()
    # Launch is interrupted, no events will be processed after it
    INTERRUPTED = enum.auto()


def timestamp():
    return str(int(time.time() * 1000))


def _get_endpoint_name(method, relative_path):
    return f"{method} {relative_path}"


def handle_before_execution(
    context: ExecutionContext,
    event: events.BeforeTestCaseExecution[BeforeExecutionPayload],
    service: ReportPortalService,
) -> None:
    endpoint_name = _get_endpoint_name(
        event.payload.method, event.payload.relative_path
    )

    if endpoint_name not in context.endpoint_to_context:
        # Ideally this shouldn't happen because the default handler should have added the context for endpoint already.
        # For now log the information and exit so that we can debug it further.
        click.secho(
            "Handler configuration seems to be wrong. Endpoint context is missing for Schemathesis run.",
            fg="red",
        )
        raise click.exceptions.Exit(1)

    endpoint_context = context.endpoint_to_context[endpoint_name]
    if endpoint_context.operations_processed == 0:
        item_id = service.start_test_item(
            name=endpoint_name,
            description=endpoint_name,
            start_time=timestamp(),
            item_type="SUITE",
        )
        endpoint_context.test_item_id = item_id
        log.info(
            f"Started the test suite for endpoint: {endpoint_name}",
            context=endpoint_context,
        )

    if event.payload.recursion_level > 0:
        # This value is not `None` - the value is set in runtime before this line
        context.operations_count += 1  # type: ignore


def _report_check_as_test_case(
    endpoint_name,
    check_name,
    checks,
    endpoint_context: EndpointExecutionContext,
    service,
):
    test_case_item_id = service.start_test_item(
        name=check_name,
        description=check_name,
        start_time=timestamp(),
        item_type="TEST",
        # Mark the test suite item id as parent_item_id
        parent_item_id=endpoint_context.test_item_id,
    )

    duration = 0
    successful_tests = 0
    failed_tests = 0
    errored_tests = 0
    for check in checks:
        duration += check.duration
        if check.value == Status.error:
            errored_tests += 1
        elif check.value == Status.failure:
            failed_tests += 1
        else:
            successful_tests += 1

    status = (
        Status.error
        if errored_tests > 0
        else Status.failure
        if failed_tests > 0
        else Status.success
    )
    summary = (
        "API Endpoint conforms to the schema as specified in the spec file."
        if status == Status.success
        else "Runtime behavior of the API Endpoint was not conforming to the spec."
        " Please check the log for more details."
    )
    test_item_attributes = {
        "elapsed_time": duration,
        "success_count": successful_tests,
        "failed_count": failed_tests,
        "errored_count": errored_tests,
        "summary": summary,
    }
    service.finish_test_item(
        item_id=test_case_item_id,
        end_time=timestamp(),
        status=STATUS_DICT[status],
        attributes=test_item_attributes,
    )
    log.debug(
        f"Finished the test case for check: {check_name} and endpoint: {endpoint_name}",
        attributes=test_item_attributes,
        item_id=test_case_item_id,
        status=status,
    )

    # Send request-response body if the test case has failed/errored.
    if status != Status.success:
        _send_endpoint_test_request_response_bodies(
            test_case_item_id, check_name, endpoint_context, service
        )
    return status


def _send_endpoint_test_request_response_bodies(
    test_item_id, check_name, endpoint_context: EndpointExecutionContext, service
):
    # Send one of the failed requests so that the user can understand the kind of failure.
    check_to_send: Optional[SerializedCheck] = None
    for result in endpoint_context.results:
        for check in result.checks_by_name[check_name]:
            if check.value != levo_commons.status.Status.success:
                check_to_send = check
                break
    if check_to_send:
        content = get_formatted_request_response(
            check_to_send.value,
            check_to_send.recorded_at,
            check_to_send.request,
            check_to_send.response,
        )
        attachment = {
            "name": f"request-response-{test_item_id}",
            "data": content,
            "mime": "text/plain",
        }
        service.log(timestamp(), attachment["name"], attachment=attachment)
        json_attachment = {
            "name": f"case-details-{test_item_id}",
            "data": json.dumps(attr.asdict(check_to_send)),
            "mime": "application/json",
        }
        service.log(timestamp(), attachment["name"], attachment=attachment)
        service.log(timestamp(), json_attachment["name"], attachment=json_attachment)
        log.debug(
            "Sending the request-response body for test.",
            item_id=test_item_id,
            attachment=attachment,
        )
    else:
        log.warn(
            f"No interaction found for failed test case of endpoint: {endpoint_context.name}"
        )


def get_hypothesis_output(hypothesis_output: List[str]) -> Optional[str]:
    """Show falsifying examples from Hypothesis output if there are any."""
    if hypothesis_output:
        return get_section_name("HYPOTHESIS OUTPUT") + "\n".join(hypothesis_output)
    return None


def get_errors(
    context: ExecutionContext, event: events.Finished[FinishedPayload]
) -> Optional[str]:
    """Get all errors in the test run."""
    if not event.payload.has_errors:
        return None

    lines = [get_section_name("ERRORS")]
    for endpoint_context in context.endpoint_to_context.values():
        for result in endpoint_context.results:
            if not result.has_errors:
                continue
            lines.append(get_single_error(context, result))
    if event.payload.generic_errors:
        lines.append(get_generic_errors(context, event.payload.generic_errors))
    return "\n".join(lines)


def get_single_error(
    context: ExecutionContext,
    result: SerializedTestResult,
) -> str:
    lines = [get_subsection(result)]
    for error in result.errors:
        lines.append(_get_error(context, error, result.seed))
    return "\n".join(lines)


def get_generic_errors(
    context: ExecutionContext,
    errors: List[SerializedError],
) -> str:
    lines = []
    for error in errors:
        lines.append(get_section_name(error.title or "Generic error", "_"))
        lines.append(_get_error(context, error))
    return "\n".join(lines)


def _get_error(
    context: ExecutionContext,
    error: SerializedError,
    seed: Optional[int] = None,
) -> str:
    if context.show_errors_tracebacks:
        message = error.exception_with_traceback
    else:
        message = error.exception
    if error.exception.startswith("InvalidSchema") and context.validate_schema:
        message += DISABLE_SCHEMA_VALIDATION_MESSAGE + "\n"
    if error.example is not None:
        get_example(context, error.example, seed=seed)
    return message


def get_failures(
    context: ExecutionContext, event: events.Finished[FinishedPayload]
) -> Optional[str]:
    """Get all failures in the test run."""
    if not event.payload.has_failures:
        return None
    relevant_results = []
    for endpoint_context in context.endpoint_to_context.values():
        relevant_results.extend(
            [result for result in endpoint_context.results if not result.is_errored]
        )
    if not relevant_results:
        return None
    lines = [get_section_name("FAILURES")]
    for result in relevant_results:
        if not result.has_failures:
            continue
        lines.append(get_failures_for_single_test(context, result))
    return "\n".join(lines)


def get_failures_for_single_test(
    context: ExecutionContext,
    result: SerializedTestResult,
) -> str:
    """Gets a failure for a single method / path."""
    lines = [get_subsection(result)]
    checks = get_unique_failures(result.checks)
    for idx, check in enumerate(checks, 1):
        message: Optional[str]
        if check.message:
            message = f"{idx}. {check.message}"
        else:
            message = None
        lines.append(
            get_example(context, check.example, check.response, message, result.seed)
        )
    return "\n".join(lines)


def reduce_schema_error(message: str) -> str:
    """Reduce the error schema output."""
    end_of_message_index = message.find(":", message.find("Failed validating"))
    if end_of_message_index != -1:
        return message[:end_of_message_index]
    return message


def get_example(
    context: ExecutionContext,
    case: Optional[SerializedCase],
    response: Optional[Response] = None,
    message: Optional[str] = None,
    seed: Optional[int] = None,
) -> str:
    lines = []
    if message is not None:
        if not context.verbosity:
            lines.append(reduce_schema_error(message))
    if case and case.text_lines:
        for line in case.text_lines:
            lines.append(line)

    if response is not None and response.body is not None:
        payload = base64.b64decode(response.body).decode(
            response.encoding or "utf8", errors="replace"
        )
        lines.append(f"----------\n\nResponse payload: `{payload}`\n")
    if context.code_sample_style == CodeSampleStyle.python and case:
        lines.append(
            f"Run this Python code to reproduce this failure: \n\n    {case.requests_code}\n"
        )
    if context.code_sample_style == CodeSampleStyle.curl and case:
        lines.append(
            f"Run this cURL command to reproduce this failure: \n\n    {case.curl_code}\n"
        )
    if seed is not None:
        lines.append(
            f"Or add this option to your command line parameters: --hypothesis-seed={seed}"
        )
    return "\n".join(lines)


def get_subsection(
    result: SerializedTestResult,
) -> str:
    return get_section_name(result.verbose_name, "_", result.data_generation_method)


def get_checks_statistics(total: Dict[str, Dict[Union[str, Status], int]]) -> str:
    lines = []
    for check_name, results in total.items():
        lines.append(get_check_result(check_name, results))
    return "Performed checks:" + "\n".join(lines)


def get_check_result(
    check_name: str,
    results: Dict[Union[str, Status], int],
) -> str:
    """Show results of single check execution."""
    success = results.get(Status.success, 0)
    total = results.get("total", 0)
    return check_name + ": " + f"{success} / {total} passed"


def get_internal_error(
    context: ExecutionContext, event: events.InternalError
) -> Optional[str]:
    message = None
    if event.exception:
        if context.show_errors_tracebacks:
            message = event.exception_with_traceback
        else:
            message = event.exception
        message = (
            f"Error: {message}\n"
            f"Add this option to your command line parameters to see full tracebacks: --show-errors-tracebacks"
        )
        if event.exception_type == "jsonschema.exceptions.ValidationError":
            message += "\n" + DISABLE_SCHEMA_VALIDATION_MESSAGE
    return message


def get_summary(event: events.Finished[FinishedPayload]) -> str:
    message = get_summary_output(event)
    return get_section_name(message)


def get_summary_output(event: events.Finished[FinishedPayload]) -> str:
    parts = get_summary_message_parts(event)
    if not parts:
        message = "Empty test suite"
    else:
        message = f'{", ".join(parts)} in {event.running_time:.2f}s'
    return message


def get_section_name(title: str, separator: str = "=", extra: str = "") -> str:
    """Print section name with separators in terminal with the given title nicely centered."""
    extra = extra if not extra else f" [{extra}]"
    return f" {title}{extra} ".center(80, separator)


def handle_finished(
    context: ExecutionContext,
    event: events.Finished[FinishedPayload],
    service: ReportPortalService,
):
    """Report the outcome of the whole testing session to Levo SaaS."""
    # Report each check for each endpoint as a test case.
    for endpoint_name, endpoint_context in context.endpoint_to_context.items():
        _report_finish_endpoint(endpoint_context, endpoint_name, service)
    report_log(get_summary(event), service)


def _report_finish_endpoint(
    endpoint_context: EndpointExecutionContext, endpoint_name, service
):
    # Report all the checks for this endpoint as test cases first.
    check_name_to_list: Dict[str, List[SerializedCheck]] = {}
    for result in endpoint_context.results:
        for check in result.checks:
            if check.name not in check_name_to_list:
                check_name_to_list[check.name] = []
            check_name_to_list[check.name].append(check)

    for check_name, checks in check_name_to_list.items():
        _report_check_as_test_case(
            endpoint_context.name, check_name, checks, endpoint_context, service
        )

    # Finish the test suite for this endpoint.
    test_item_attributes = {
        "elapsed_time": endpoint_context.duration,
        "success_count": endpoint_context.success_count,
        "failed_count": endpoint_context.failed_count,
        "errored_count": endpoint_context.errored_count,
    }
    service.finish_test_item(
        item_id=endpoint_context.test_item_id,
        end_time=timestamp(),
        status=STATUS_DICT[endpoint_context.status],
        attributes=test_item_attributes,
    )
    log.info(
        f"Test Suite for endpoint: {endpoint_name} finished with status: {endpoint_context.status}"
    )


def report_log(
    message: str, service: ReportPortalService, level="INFO", item_id=None
) -> None:
    if message is None:
        return
    service.log(time=timestamp(), message=message, item_id=item_id, level=level)
    log.debug("Reporting the log.", message=message, item_id=item_id)


def my_error_handler(exc_info):
    """
    This callback function will be called by async service client when error occurs.
    Return True if error is not critical and you want to continue work.
    :param exc_info: result of sys.exc_info() -> (type, value, traceback)
    :return:
    """
    traceback.print_exception(*exc_info)


def terminate_launch(
    service: ReportPortalService,
    status="PASSED",
    success_count=0,
    failed_count=0,
    errored_count=0,
) -> None:
    launch_attributes = {
        "success_count": success_count,
        "failed_count": failed_count,
        "errored_count": errored_count,
    }
    service.finish_launch(
        end_time=timestamp(), status=status, attributes=launch_attributes
    )
    log.info(f"Finished the launch with status: {status}")
    service.terminate()


class SchemathesisReportPortalHandler(EventHandler):
    def __init__(self, project, token, spec_path):
        self.service = ReportPortalService(
            endpoint=TEST_RUNS_SERVICE_URL, project=project, token=token
        )
        self.state = HandlerState.NEW
        self.spec = fetch_schema_as_lines(spec_path)

    def _set_state(self, state: HandlerState) -> None:
        self.state = state

    def _terminate_launch(
        self, status: str, success_count: int, failed_count: int, errored_count: int
    ) -> None:
        if self.state == HandlerState.ACTIVE:
            terminate_launch(
                self.service, status, success_count, failed_count, errored_count
            )

    def handle_event(self, context: ExecutionContext, event: events.Event) -> None:
        """Reports the test results to ReportPortal service."""
        if isinstance(event, events.Initialized):
            # Create a launch in report portal
            launch_name = "Schema conformance test"
            launch_attr = {
                "target_url": event.payload.base_url,
            }
            self.service.start_launch(
                name=launch_name,
                start_time=timestamp(),
                description=launch_name,
                attributes=launch_attr,
            )
            self._set_state(HandlerState.ACTIVE)
            context.operations_count = cast(
                int, event.payload.operations_count
            )  # INVARIANT: should not be `None`
            log.info(
                f"Test is ready to be run with {context.operations_count} endpoints."
            )
        if isinstance(event, events.BeforeTestCaseExecution):
            handle_before_execution(context, event, self.service)
        if isinstance(event, events.AfterTestCaseExecution):
            pass
        if isinstance(event, events.Finished):
            # Send the schema as an attachment.
            attachment = {
                "name": "schema",
                "data": "".join(self.spec),
                "mime": "text/plain",
            }
            self.service.log(timestamp(), "schema", attachment=attachment)
            handle_finished(context, event, self.service)
            status = {
                HandlerState.ACTIVE: STATUS_DICT[context.status],
                HandlerState.INTERRUPTED: "INTERRUPTED",
            }[self.state]
            self._terminate_launch(
                status,
                context.success_count,
                context.failed_count,
                context.errored_count,
            )
        if isinstance(event, events.Interrupted):
            log.info("Test run is interrupted.")
            self._set_state(HandlerState.INTERRUPTED)
        if isinstance(event, events.InternalError):
            self._terminate_launch(
                "FAILED",
                context.success_count,
                context.failed_count,
                context.errored_count,
            )

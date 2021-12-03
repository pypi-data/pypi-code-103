from wcd_geo_db_sources.conf import settings

from ..globals import get_registry
from ..exceptions import (
    ProcessNoRunner, ProcessParallelExecution, ProcessCantRerun
)
from ..models import ProcessState
from ..runner import ProcessRunner
from ..query import RERUNNABLES


__all__ = 'run_source', 'rerun_source', 'rerun_state'


def create_runner_from_source(source: str) -> ProcessRunner:
    registry = get_registry()
    runner = registry.get(source, None)

    if runner is None:
        raise ProcessNoRunner()

    return runner(debug_run=settings.SOURCE_IMPORT_DEBUG)


def run_source(source: str) -> bool:
    runner = create_runner_from_source(source)

    if ProcessState.objects.may_run().filter(source=source).exists():
        raise ProcessParallelExecution()

    return runner.run()


def rerun_source(source: str):
    runner = create_runner_from_source(source)
    state = ProcessState.objects.filter(source=source).may_rerun().first()

    if state is None:
        raise ProcessCantRerun()

    return runner.run(state=state)


def rerun_state(state: ProcessState):
    runner = create_runner_from_source(state.source)

    if state.status not in RERUNNABLES:
        raise ProcessCantRerun()

    return runner.run(state=state)

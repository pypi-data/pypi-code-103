import traceback
from typing import Callable, Optional, Sequence, TYPE_CHECKING
from contextlib import contextmanager
from django.db import transaction

from .exceptions import (
    ProcessFinished, ProcessCantProceed, ProcessNoStage, ProcessParallelExecution
)
from .const import ProcessStatus, ProcessStage

if TYPE_CHECKING:
    from .models import ProcessState


def stage(stage: ProcessStage):
    def wrapper(f: Callable):
        f._stage = stage

        return f

    return wrapper


EMPTY = object()


class ProcessRunner:
    MAX_RUNS: int = 1000
    source: str = None
    Status: ProcessStatus
    Stage: ProcessStage
    state: 'ProcessState'
    default_config: dict = None
    _debug_run: bool

    def __init__(self, debug_run: bool = False):
        assert self.source is not None, (
            'You must define `source` attribute with source name for '
            'this process to be able it to run.'
        )
        assert self.default_config is not None, (
            'You must provide default configuration for process.'
        )
        self._debug_run = debug_run

    def _save_state(self, fields: Sequence[str]):
        if len(fields) == 0:
            return

        saved = self.state.versioned_save(fields=fields)

        if not saved:
            raise ProcessParallelExecution(
                'Failed to change process state - parallel execution in process.'
            )

    def update_state(
        self,
        status: Optional[ProcessStatus] = EMPTY,
        state: Optional[dict] = EMPTY,
        stage: Optional[ProcessStage] = EMPTY,
        partial_state: Optional[dict] = EMPTY,
    ) -> None:
        fields = set()

        for field, value in (('status', status), ('state', state), ('stage', stage)):
            if value is EMPTY:
                continue

            fields.add(field)
            setattr(self.state, field, value)

        if partial_state is not EMPTY:
            fields.add('state')
            self.state.state = {**self.state.state, **partial_state}

        if len(fields) == 0:
            return False

        success = self.state.versioned_save(fields)

        if not success:
            raise ProcessParallelExecution(
                'State update failed due to an invalid version.'
            )

    def run(self, state: Optional['ProcessState'] = None) -> bool:
        self.state = state
        runs = self.MAX_RUNS

        self.initialize()

        with self.exception_resolver() as result:
            while runs > 0:
                runs -= 1

                self.run_next_stage()

        return result['state']

    def initialize(self) -> None:
        from .models import ProcessState, ProcessSourceConfig

        with self.handle_exception():
            with transaction.atomic():
                if self.state is None:
                    self.state = ProcessState.objects.create(
                        source=self.source
                    )

                instance, created = ProcessSourceConfig.objects.get_or_create(
                    defaults={'config': self.default_config}, source=self.source
                )
                self.config = instance.config

    def get_current_stage(self):
        return self.state.stage

    def run_next_stage(self):
        if self.state.status == self.state.Status.SUCCESS:
            raise ProcessFinished()

        self.update_state(status=self.state.Status.IN_PROGRESS)

        current_stage = self.get_current_stage()
        stage_runner = next(
            (
                a
                for a in (getattr(self, m, None) for m in dir(self))
                if (
                    callable(a) and
                    hasattr(a, '_stage') and
                    a._stage == current_stage
                )
            ),
            None
        )

        if stage_runner is None:
            raise ProcessNoStage(
                f'No such stage "{current_stage}" in a "{self.source}" '
                'process runner.'
            )

        stage_runner()

    @contextmanager
    def handle_exception(self):
        if self._debug_run:
            yield
            return

        try:
            yield
        except Exception as e:
            raise ProcessCantProceed(str(e), exception=e)

    @contextmanager
    def exception_resolver(self):
        result = {'state': True}

        if self._debug_run:
            yield result
            return

        try:
            yield result
        except ProcessCantProceed as e:
            self.update_state(
                status=self.state.Status.FAILED,
                partial_state={'exception': {
                    'message': str(e.underlying_exception or 'Cant proceed.'),
                    'traceback': traceback.format_exc(),
                }}
            )
            result['state'] = False
        except ProcessFinished:
            self.update_state(self.state.Status.SUCCESS)
            result['state'] = True
        except ProcessParallelExecution:
            result['state'] = False
        except Exception as e:
            self.update_state(
                status=self.state.Status.FAILED,
                partial_state={'exception': {
                    'message': str(e),
                    'traceback': traceback.format_exc(),
                }}
            )
            result['state'] = False

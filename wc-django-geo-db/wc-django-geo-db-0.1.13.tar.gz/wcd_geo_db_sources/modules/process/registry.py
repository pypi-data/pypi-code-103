from typing import Dict, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .runner import ProcessRunner


__all__ = 'ProcessRegistry', 'ProcessRegistryType'

ProcessRegistryType = Dict[str, Type['ProcessRunner']]


class ProcessRegistry(dict):
    def register(self, runner: Type['ProcessRunner']) -> Type['ProcessRunner']:
        assert runner.source is not None, (
            'You must define `source` attribute with source name for '
            'this process to be able it to run.'
        )
        assert runner.source not in self, (
            'Runner for this source has already been registered. '
            'Remove it manually to proceed.'
        )

        self[runner.source] = runner

        return runner

    def unregister(self, runner: Type['ProcessRunner']) -> Type['ProcessRunner']:
        assert runner.source in self, 'Register runner first.'
        assert self[runner.source] == runner, (
            'You are trying to unregister different runner with the '
            'same source. This is prohibited.'
        )

        return self.pop(runner.source)

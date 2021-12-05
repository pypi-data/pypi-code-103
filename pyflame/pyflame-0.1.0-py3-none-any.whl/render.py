# Copyright 2020-2021 Daniel Harding
# Distributed as part of the pyflame project under the terms of the MIT license

import shutil
import subprocess

from functools import lru_cache

from pyflame.exceptions import MissingFlamegraphScript
from pyflame.stack import unpack_stack


@lru_cache()
def _find_flamegraph_script():
    return shutil.which('flamegraph.pl')


def _unpack_stack_counts(stack_counts):
    return (
        (list(unpack_stack(packed_stack)), count)
        for packed_stack, count in stack_counts.items()
    )


def _format_stack(stack):
    return ";".join(
        "{}({}:{})".format(name, filename, firstlineno)
            for name, filename, firstlineno in stack
    )


def _run_flamegraph_script(args, stats):
    return subprocess.run(
        args=args,
        input=stats,
        stdout=subprocess.PIPE,
        check=True,
        encoding='utf-8',
    ).stdout


def stack_counts_to_svg(
    stack_counts,
    script_path=None,
    script_extra_args=None,
    include_stack=lambda stack: True,
    preprocess_stack=lambda stack: stack,
):
    if script_path is None:
        script_path = _find_flamegraph_script()
    if script_path is None:
        raise MissingFlamegraphScript

    if script_extra_args is None:
        script_extra_args = []

    return _run_flamegraph_script(
        [script_path] + script_extra_args,
        '\n'.join(
            '{} {}'.format(_format_stack(preprocess_stack(stack)), count)
            for stack, count in _unpack_stack_counts(stack_counts)
            if include_stack(stack)
        ),
    )

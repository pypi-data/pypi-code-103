import time

import click
import grpc

from jetpack import _runtime as runtime
from jetpack import cron
from jetpack._task.jetpack_function import JetpackFunction
from jetpack.cmd import util
from jetpack.config import symbols
from jetpack.config.symbols import Symbol

_using_new_cli = False


def is_using_new_cli() -> bool:
    """
    for legacy uses, we keep old cli. This function disables that logic to ensure
    we don't run the cli command twice.
    """
    return _using_new_cli


@click.group()
def cli() -> None:
    global _using_new_cli
    _using_new_cli = True


@click.command(help="Executes jetpack task")
@click.option("--entrypoint", required=True)
@click.option("--exec-id", required=True)
@click.option("--qualified-symbol", required=True)
@click.option("--encoded-args", default="")
def exec_task(
    entrypoint: str, exec_id: str, qualified_symbol: str, encoded_args: str
) -> None:
    util.load_user_entrypoint(entrypoint)
    func = symbols.get_symbol_table()[Symbol(qualified_symbol)]
    JetpackFunction(func).exec(exec_id, encoded_args)


@click.command(help="Registers jetpack functions with runtime")
@click.option("--entrypoint", required=True)
def register(entrypoint: str) -> None:
    util.load_user_entrypoint(entrypoint)
    # For now, we try a few times to register with runtime. Once the runtime
    # becomes a sidecar, we can remove this.
    tries = 3
    for i in range(tries):
        try:
            runtime.set_cron_jobs(cron.get_jobs())
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                if i == tries - 1:
                    # no more tries, just give up.
                    raise rpc_error
                print("runtime is not available. Sleep(5) and try again")
                time.sleep(5)
            else:
                raise rpc_error


cli.add_command(exec_task)
cli.add_command(register)

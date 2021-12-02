"""Stateful wrapper to execute shell commands."""

import asyncio
from typing import Coroutine, Optional, Sequence, Union


class SH:
    """Wrapper around an interactive shell process.

    This class can be used to execute multiple shell commands within a single shell
    session; shell output (stdout and stderr) is captured and returned as a string.
    The class must be used as a context manager; both synchronous and asynchronous
    modes are supported.

    Args:
        shell: The shell command to execute, as a sequence of strings. This must start
            an interactive shell, and defaults to `sh -i`.
        loop: Optional event loop to use. If not provided, the default event loop is
            used instead.

    Usage::

        # synchronous mode
        with SH() as sh:
            sh("x=1")
            print(sh("echo $x"))

        # asynchronous mode
        async with SH() as sh:
            await sh("x=1")
            print(await sh("echo $x"))

    Note:
        The class uses a custom prompt string to identify the end of a command. So,
        do not run any commands that change the prompt. Similarly, background jobs are
        not supported, if they produce any output. The behavior in these cases is
        undefined.
    """

    _prompt = "\ufffe".encode()

    def __init__(
        self,
        shell: Sequence[str] = ("sh", "-i"),
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        self._shell = shell
        self._loop = loop or asyncio.get_event_loop()
        self._process: Optional[asyncio.subprocess.Process] = None
        self._context_is_async = True

    async def __aenter__(self) -> "SH":
        self._process = await asyncio.create_subprocess_exec(
            *self._shell,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        assert self._process.stdin is not None
        assert self._process.stdout is not None

        _promptstr = self._prompt.decode()
        try:
            await self._run(f"PS1={_promptstr}; PS2={_promptstr}")
        except OSError as e:
            raise RuntimeError(f"SH: could not initialize: {e}") from None

        self._context_is_async = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self._process.communicate("exit\n".encode())
        finally:
            self._process = None

    def __enter__(self) -> "SH":
        self._loop.run_until_complete(self.__aenter__())
        self._context_is_async = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._loop.run_until_complete(self.__aexit__(exc_type, exc_val, exc_tb))

    async def _run(self, cmd: str) -> str:
        if self._process is None:
            raise TypeError("SH must be used as a context manager")

        assert self._process.stdin is not None
        assert self._process.stdout is not None

        out = b""
        for line in cmd.splitlines():
            self._process.stdin.write(f"{line}\n".encode())
            await self._process.stdin.drain()
            out += (await self._process.stdout.readuntil(self._prompt))[
                : -len(self._prompt)
            ]
        return out.decode().rstrip()

    def __call__(self, cmd: str) -> Union[Coroutine, str]:
        """Run command inside shell session.

        Args:
            cmd: The command to execute, as a string. The command is passed as-is, and
                should be escaped first if necessary.

        Note:
            This function can only be used inside a `with` or `async with` block.
        """
        run_coro = self._run(cmd)
        if self._context_is_async:
            return run_coro
        return self._loop.run_until_complete(run_coro)

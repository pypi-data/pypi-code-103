import subprocess
import os
import asyncio
import datetime


class Executor(object):
    def __init__(self):
        self.print_buffer = []
        self.done_condition = asyncio.Condition()
        self.done_state = []

    def printLine(self, line=""):
        self.print_buffer.append(line)

    def flushOutput(self):
        print(os.linesep.join(self.print_buffer))
        self.print_buffer = []

    async def __call__(self, event_info):
        self.printLine(">> {}".format(str(datetime.datetime.now())))
        self.printLine(
            ">> {} -> {}".format(
                event_info,
                self.__class__.__name__,
            )
        )
        self.done_state = []
        await self.execute()
        self.done_state += ["done"]
        self.flushOutput()
        async with self.done_condition:
            self.done_condition.notify_all()

    async def execute(self):
        self.printLine("NOP")

    async def awaitDone(self):
        async with self.done_condition:
            await self.done_condition.wait()


class ProcessExecutor(Executor):
    def __init__(self, command):
        self.command = command
        super().__init__()

    async def execute(self):
        process = await asyncio.create_subprocess_shell(
            self.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        self.printLine("$ {} ({})".format(self.command, process.returncode))
        stdout_lines = stdout.decode().splitlines()
        if len(stdout_lines) > 0:
            self.printLine()
            self.printLine("[[stdout]]")
            for line in stdout_lines:
                self.printLine(line)
        stderr_lines = stderr.decode().splitlines()
        if len(stderr_lines) > 0:
            self.printLine()
            self.printLine("[[stderr]]")
            for line in stderr_lines:
                self.printLine(line)
        self.printLine()
        if process.returncode == 0:
            self.done_state.append("success")
        else:
            self.done_state.append("fail")

from subprocess import run
from typing import IO, Union

from comprehemd import CodeBlock
from naughtty import NaughTTY
from thtml import Scope, write_html

from dinject.enums import Content, Host
from dinject.executors import make_executor
from dinject.parser import Parser
from dinject.types import Instruction

Reader = Union[str, IO[str]]


def execute(
    block: CodeBlock,
    instruction: Instruction,
    parser: Parser,
    writer: IO[str],
) -> None:
    """
    Executes `block` then writes the result to `writer`, with respect to
    `instruction`.
    """

    executor = make_executor(language=block.language, script=block.text)

    if not executor:
        # We don't support this language, so pass through.
        block.render(writer)
        return

    if instruction.host == Host.TERMINAL:
        n = NaughTTY(command=executor.arguments)
        n.execute()
        content = n.output
    else:
        process = run(executor.arguments, capture_output=True)
        if process.returncode == 0:
            content = process.stdout.decode("UTF-8")
        else:
            content = process.stderr.decode("UTF-8")

    content = content.rstrip() + "\n"

    parser.write_range_start(instruction, writer)
    writer.write("\n")

    if instruction.content == Content.HTML:
        write_html(
            text=content,
            writer=writer,
            scope=Scope.FRAGMENT,
            theme="plain",
        )
        writer.write("\n")
    else:
        block = CodeBlock(language="text", source=content, text=content)
        block.render(writer, fence=instruction.fence)

    writer.write("\n")
    parser.write_range_end(writer)

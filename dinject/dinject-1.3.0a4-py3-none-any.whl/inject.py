from io import StringIO
from logging import getLogger
from pathlib import Path
from shutil import move
from tempfile import NamedTemporaryFile
from typing import IO, Iterable, Optional, Union

from comprehemd import CodeBlock, MarkdownParser

from dinject.enums.range import Range
from dinject.execute import execute
from dinject.parser import Parser

Reader = Union[str, IO[str]]


def inject(
    reader: Reader,
    writer: IO[str],
    parser: Optional[Parser] = None,
) -> None:
    """Reads and injects from `reader` to `writer`."""

    logger = getLogger("dinject")
    logger.debug("Starting injection: %s", reader)

    if isinstance(reader, str):
        reader = StringIO(reader)

    is_skipping_range = False
    last_code: Optional[CodeBlock] = None
    parser = parser or Parser()

    for block in MarkdownParser().read(reader):
        logger.debug("Parsed block: %s", block)

        din = parser.get_instruction(block.source)

        if is_skipping_range:
            if din and din.range == Range.END:
                is_skipping_range = False
            continue

        if din and last_code:
            execute(
                block=last_code,
                instruction=din,
                parser=parser,
                writer=writer,
            )
            last_code = None
            if din.range == Range.START:
                is_skipping_range = True
            continue

        if isinstance(block, CodeBlock):
            last_code = block

        writer.write(block.source)
        writer.write("\n")


def inject_file(path: Path, parser: Optional[Parser] = None) -> None:
    """
    Executes the code blocks and injects the results into the Markdown document
    at `path`.
    """

    with NamedTemporaryFile("a", delete=False) as writer:
        with open(path, "r") as reader:
            inject(
                parser=parser,
                reader=reader,
                writer=writer,
            )
        move(writer.name, path)


def iterate_lines(reader: Reader) -> Iterable[str]:
    """Returns an line iterator."""

    it = reader.split("\n") if isinstance(reader, str) else reader

    for line in it:
        yield line.rstrip()

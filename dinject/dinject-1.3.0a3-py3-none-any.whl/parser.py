from re import match
from typing import IO, Dict, Optional

from comprehemd import Fence

from dinject.enums import Content, Host, Range
from dinject.exceptions import InstructionParseError
from dinject.types import Instruction, ParserOptions


class Parser:
    def __init__(
        self,
        keyword: str = "dinject",
        options: Optional[ParserOptions] = None,
    ) -> None:
        self._keyword = keyword
        self._options = options or ParserOptions()

    def get_instruction(self, line: str) -> Optional["Instruction"]:
        """Parses `line` as an Instruction`."""

        m = match(f"^<!--{self._keyword }(.*)-->$", line)
        if not m:
            return None

        wip: Dict[str, str] = {}

        for pair in m.group(1).split(" "):
            if not pair:
                continue
            if m := match("([a-z]+)=([a-z]+)", pair):
                wip[m.group(1)] = m.group(2)
            else:
                raise InstructionParseError(pair, line)

        return Instruction(
            content=self._options.force_content
            or Content[wip.get("as", Content.MARKDOWN.name).upper()],
            fence=Fence[wip.get("fence", Fence.BACKTICKS.name).upper()],
            host=self._options.force_host
            or Host[wip.get("host", Host.SHELL.name).upper()],
            range=Range[wip.get("range", Range.NONE.name).upper()],
        )

    def write_range_end(self, writer: IO[str]) -> None:
        """Writes an instruction to mark the end of an injection."""

        writer.write("<!--")
        writer.write(self._keyword)
        writer.write(f" range={Range.END.name.lower()}")
        writer.write("-->\n")

    def write_range_start(self, instruction: Instruction, writer: IO[str]) -> None:
        """Writes an instruction to mark the start of an injection."""

        writer.write("<!--")
        writer.write(self._keyword)
        writer.write(f" as={instruction.content.name.lower()}")
        writer.write(f" fence={instruction.fence.name.lower()}")
        writer.write(f" host={instruction.host.name.lower()}")
        writer.write(f" range={Range.START.name.lower()}")
        writer.write("-->\n")

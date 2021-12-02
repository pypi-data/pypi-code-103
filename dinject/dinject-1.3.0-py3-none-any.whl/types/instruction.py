from dataclasses import dataclass

from comprehemd import Fence

from dinject.enums import Content, Host, Range


@dataclass
class Instruction:
    """Document injection instruction"""

    content: Content = Content.MARKDOWN
    """Content type to inject the result as."""

    fence: Fence = Fence.BACKTICKS
    """Fence style for rendered Markdown."""

    host: Host = Host.SHELL
    """Execution host."""

    range: Range = Range.NONE
    """Injection site demarcation."""

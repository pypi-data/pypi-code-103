from typing import Any, Tuple
from typing_extensions import Protocol


class TextGenerator(Protocol):
    def generate_text(self, input_text: str, context: Any) -> Tuple[str, Any]:
        ...

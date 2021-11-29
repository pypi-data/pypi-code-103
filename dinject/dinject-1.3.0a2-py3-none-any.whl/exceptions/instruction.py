from dinject.exceptions.dinject import DinjectError


class InstructionError(DinjectError):
    def __init__(self, msg: str, line: str) -> None:
        super().__init__(f"{msg}: {line}")


class InstructionParseError(InstructionError):
    def __init__(self, context: str, line: str) -> None:
        super().__init__(f'failed to parse "{context}"', line)

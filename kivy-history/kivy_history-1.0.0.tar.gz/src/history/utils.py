from kivy.logger import Logger


def console_log(stack: list, index: int) -> None:
    """
    Log the current state of the stack.
    """
    data = [f'{v}' if n != index else f'[{v}]' for n, v in enumerate(stack)]
    Logger.info(f"History: Stack is { {' > '.join(data)} }")

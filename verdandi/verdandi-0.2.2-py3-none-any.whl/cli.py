from shutil import get_terminal_size
from typing import Iterable, List

from verdandi.result import BenchmarkResult


def print_stdout(result: BenchmarkResult) -> None:
    for iter_index, iter_stdout in enumerate(result.stdout, start=1):
        if not iter_stdout:
            continue

        print_header(f"{result.name}: iteration {iter_index}", padding_symbol="-")
        print(iter_stdout)


def print_stderr(result: BenchmarkResult) -> None:
    for iter_index, iter_stderr in enumerate(result.stderr, start=1):
        if not iter_stderr:
            continue

        print_header(f"{result.name}: iteration {iter_index}", padding_symbol="-")
        print(iter_stderr)


def print_exceptions(result: BenchmarkResult) -> None:
    for iter_index, iter_exc in enumerate(result.exceptions, start=1):
        print_header(f"{result.name}: iteration {iter_index}", padding_symbol="-")
        print(f"{iter_exc.__class__.__name__}: {str(iter_exc)}")


def print_results_as_table(results: Iterable[BenchmarkResult]) -> None:
    """
    Accepts a list of BenchmarkResult, formats them and prints out a table with details.
    """

    def format_table_row(row: List[str], width: int) -> str:
        s = "".join(str(cell).ljust(width) for cell in row[:-1])
        s += str(row[-1])
        return s

    headers = ["Name", "Result", "Duration (in seconds)", "Memory allocated (in bytes)"]
    col_width = max(len(result.name) for result in results) + 2

    print_header("", padding_symbol="-")
    print(format_table_row(headers, col_width))
    print_header("", padding_symbol="-")

    for r in results:
        print(format_table_row([r.name, r.rtype.name, f"{r.duration_sec:.4f}", str(r.memory_diff)], col_width))

    print_header("", padding_symbol="-")
    print()  # Empty line


def print_header(text: str, padding_symbol: str = "=") -> None:
    """
    Prints given text padded from both sides with `padding_symbol` up to terminal width
    """
    text_length = len(text)
    columns = get_terminal_size()[0]

    padding_length = ((columns - text_length) // 2) - 1  # Substract one whitespace from each side
    padding = padding_symbol * padding_length

    if text:
        print(f"{padding} {text} {padding}")
    else:
        print(padding * 2)

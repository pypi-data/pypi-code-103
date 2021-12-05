def test_pass(path: str, line: str, left: int | str | float, right: int | str | float) -> None:
    print(f"\x1b[38;5;107m{path}\x1b[0m | \x1b[38;5;107mPASSED\x1b[0m assert {line} "
          f"\n\tLeft value: \x1b[38;5;107m{left}\x1b[0m"
          f"\n\tRight value: \x1b[38;5;107m{right}\x1b[0m\n")


def test_fail(path: str, line: str, left: int | str | float, right: int | str | float) -> None:
    print(f"\x1b[38;5;1m{path}\x1b[0m | \x1b[38;5;1mFAIL\x1b[0m assert {line} "
          f"\n\tLeft value: \x1b[38;5;3m{left}\x1b[0m"
          f"\n\tRight value: \x1b[38;5;3m{right}\x1b[0m\n")


def fatal(location: str, msg: str) -> None:
    print(f"\x1b[38;5;1m{location} | {msg}\x1b[0m")

def error(msg: str) -> None:
    print(f"\x1b[38;5;1m{msg}\x1b[0m")

def warn(locate: str, msg: str) -> None:
    print(f"\x1b[38;5;3m{locate} | {msg}\x1b[0m")

"""Entrypoint."""

import fileinput
import sys
import termios
import tty

from . import game, load


def main() -> None:  # pragma: no cover
    """Entrypoint."""
    g = game(*load(list(fileinput.input())))
    print(next(g))
    old = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    try:
        while True:
            print(g.send(sys.stdin.read(1)))
    except StopIteration as e:
        print(e.value)
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)


if __name__ == "__main__":  # pragma: no cover
    main()

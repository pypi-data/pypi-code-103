from typing import NamedTuple


class Seq(NamedTuple):
    start: int
    size: int

    def __iter__(self):
        return SeqIter(self.start, self.size)


def seq(start: int = -1, size: int = -1):
    return Seq(start, size)


class SeqIter:
    next: int
    idx: int
    size: int

    def __init__(self, start: int, size: int):
        self.next, self.idx, self.size = start, 0, size

    def __iter__(self):
        return self

    def __next__(self):
        if self.idx < self.size:
            out = self.next
            self.next = self.next - 1 if self.next < 0 else self.next + 1
            self.idx += 1
            return out
        else:
            raise StopIteration

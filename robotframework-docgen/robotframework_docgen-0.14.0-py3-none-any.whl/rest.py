from contextlib import contextmanager


class RestWriter:
    """Helper class for writing reStructuredText"""

    INDENT = "  "

    def __init__(self):
        self.body = []
        self._indent = 0
        self._section = 0

    def save(self, path):
        with open(path, "w") as fd:
            fd.write(self.as_text())

    def write(self, text=""):
        for line in text.split("\n"):
            # Do not indent empty lines
            if not line.strip():
                self.body.append("")
                continue

            self.body.append(
                "{indent}{line}".format(indent=self.INDENT * self._indent, line=line)
            )

    def as_text(self):
        return "\n".join(self.body)

    def raw(self, text):
        self.write(text)
        self.write()

    @contextmanager
    def heading(self, content):
        try:
            self._heading(content)
            self._section += 1
            yield
        finally:
            self._section -= 1

    def _heading(self, content):
        chars = "#*=-"
        line = chars[self._section] * len(content)

        if self._section < 2:
            self.write(line)
        self.write(content)
        self.write(line)
        self.write()

    @contextmanager
    def field(self, name):
        try:
            self.write(f":{name}:")
            self._indent += 1
            yield
        finally:
            self._indent -= 1

    def fieldlist(self, *values):
        if not values:
            return
        for name, value in values:
            self.write(f":{name}: {value}")
        self.write()

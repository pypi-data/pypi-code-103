from re import Match



class NamedList(list):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.prefix = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'{self.prefix}{self.name} {list(map(str, self))}'

    def append(self, match: Match):
        line, prefix, content = match.group(0, 1, 2)

        if self.prefix is None:
            self.prefix = prefix

        if prefix == self.prefix:
            super().append(content)
        else:
            self[-1] += f'\n{line}'
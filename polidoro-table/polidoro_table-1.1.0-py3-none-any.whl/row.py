class Row:
    def __init__(self, title=None, columns=None, properties=None):
        self.title = title
        self.columns = columns or []
        self.properties = properties or []

    def __str__(self):
        return str(self.title)

    def __len__(self):
        return len(self.title or '')

    def __iter__(self):
        yield from self.columns

    def add_cell(self, cell):
        self.columns.append(cell)

    def add_property(self, property):
        self.properties.append(property)

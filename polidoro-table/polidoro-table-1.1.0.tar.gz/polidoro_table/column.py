from polidoro_table.cell import Cell


class Column:
    def __init__(self, headers, title=None, properties=None):
        self.title = Cell(title, self, headers)
        self.rows = []
        self.width = len(title or '')
        self.properties = properties or []

    def __str__(self):
        return str(self.title)

    def __len__(self):
        if self.width is None:
            self.width = max(len(c) for c in self.rows + [self.title])
        return self.width

    def add_cell(self, cell):
        self.width = None
        self.rows.append(cell)

    def add_property(self, property):
        self.properties.append(property)

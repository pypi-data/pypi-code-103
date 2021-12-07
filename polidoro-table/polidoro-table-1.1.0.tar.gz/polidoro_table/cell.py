from datetime import timedelta

from polidoro_table.property import Property


# noinspection PyShadowingBuiltins
class Cell:
    def __init__(self, value, column, row, properties=None):
        self.value = value
        self.column = column
        self.row = row
        self.properties = properties or []

    def __str__(self):
        def C(col_name):
            for c in self.row.columns:
                if c.column.title.value == col_name:
                    return c.value

        return Property.apply_properties(
            self.value,
            self.column.properties + self.row.properties + self.properties + [Property(size=self.column.width)],
            methods=dict(C=C, timedelta=timedelta)
        )

    def __len__(self):
        from polidoro_table import Format
        return len(Format.remove_format(str(self.value)))

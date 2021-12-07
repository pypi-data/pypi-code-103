from polidoro_table.borders import Border
from polidoro_table.cell import Cell
from polidoro_table.column import Column
from polidoro_table.property import Property
from polidoro_table.row import Row
from polidoro_table.string_utils import fill, Align

Border.set_default(Border.THIN)


class Table:
    def __init__(self,
                 title=None,
                 border=Border.default(),
                 footer=None,
                 show_headers=True,
                 width=None
                 ):
        from polidoro_table import Format
        self.title = title
        self.footer = footer
        self.border = border
        self.width = width
        self.show_headers = show_headers
        self.headers = Row()
        self.headers.add_property(Property(format=Format.BOLD, align=Align.CENTER, method=lambda v: v.upper()))
        self.columns = []
        self.rows = []

        self._rows_to_print = []
        self._assembled = False

    def print(self):
        self._assemble()
        print('\n'.join(self._rows_to_print))

    @property
    def height(self):
        return len(self._rows_to_print)

    def _adjust_width(self):
        self.width = self._adjust_columns_width()

    def _adjust_columns_width(self):
        from polidoro_table import Format
        title_len = len(Format.remove_format(self.title or ''))
        columns_len = sum(len(c) for c in self.columns) + len(self.columns) + 1
        goal_width = self.width or max(title_len + 2, columns_len)
        changeable_columns = self.columns[:]
        while changeable_columns and columns_len != goal_width:
            column_to_change = changeable_columns.pop(0)
            if columns_len > goal_width:
                column_to_change.width -= 1
            else:
                column_to_change.width += 1
            columns_len = sum(len(c) for c in self.columns) + len(self.columns) + 1
            changeable_columns.append(column_to_change)
        return columns_len

    def _add_row(self, row_to_print, separator='vertical', left_border=None, right_border=None):
        if row_to_print is None:
            self._add_separator()
        else:
            left_border = left_border or separator
            right_border = right_border or separator

            self._rows_to_print.append(
                self.border[left_border] +
                self.border[separator].join(str(c) for c in row_to_print) +
                self.border[right_border]
            )

    def _add_first_row(self):
        separator = 'mid_top'
        if self.title:
            separator = 'horizontal'
        self._add_row([fill('', len(c), char=self.border['horizontal']) for c in self.columns],
                      left_border='top_left', right_border='top_right', separator=separator)

    def _add_separator(self, separator='mid'):
        self._add_row([fill('', len(c), char=self.border['horizontal']) for c in self.columns],
                      left_border='mid_left', right_border='mid_right', separator=separator)

    def _add_title(self):
        self._add_row([fill(self.title, self.width - 2, align=Align.CENTER)])
        self._add_separator(separator='mid_top')

    def _add_headers(self):
        self._add_row(self.columns)
        self._add_separator()

    def _add_footer(self):
        self._rows_to_print.pop()
        self._add_separator(separator='mid_bot')
        self._add_row([fill(self.footer, self.width)])
        self._add_separator()

    def _add_last_row(self):
        self._rows_to_print.pop()
        separator = 'mid_bot'
        if self.footer:
            separator = 'horizontal'
        self._add_row([fill('', len(c), char=self.border['horizontal']) for c in self.columns],
                      left_border='bot_left', right_border='bot_right', separator=separator)

    def _assemble(self):
        if self._assembled:
            return

        if not self.columns:
            raise Exception('Must have at least 1 column')

        self._adjust_width()

        self._add_first_row()

        if self.title:
            self._add_title()

        if self.show_headers:
            self._add_headers()

        for row in self.rows:
            self._add_row(row)
        self._add_separator()

        if self.footer:
            self._add_footer()

        self._add_last_row()

        self._assembled = True

    def add_column(self, column):
        self.columns.append(Column(self.headers, column))

    def add_columns(self, columns):
        for c in columns:
            self.add_column(c)

    def add_row(self, row=None, **kwargs):
        if row is None:
            r = None
        else:
            r = Row(**kwargs)
            for i in range(len(row)):
                value = row[i]
                col = self.columns[i]

                cell = Cell(value, col, r)
                r.add_cell(cell)
                col.add_cell(cell)
        self.rows.append(r)

    def return_table_lines(self, erase=False):
        from polidoro_table import erase_lines, up_lines
        if erase:
            erase_lines(self.height)
        else:
            up_lines(self.height)

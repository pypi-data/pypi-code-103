class Preview:
    def __init__(self, pad):
        self.pad = pad
        self.internal_row = 0 # so we know whether to update or not

    def update(self, row: int, *args):
        self.internal_row = row

    def draw(self):
        self.pad.clear()
        width = self.pad.getmaxyx()[1]
        self.pad.addstr(0, 0, f'{"─" * width}')
        for row,line in enumerate(self.content):
            self.pad.addstr(row + 1, 1, line)

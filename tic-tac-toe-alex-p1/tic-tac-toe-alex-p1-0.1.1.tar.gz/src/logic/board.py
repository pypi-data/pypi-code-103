from settings import BOARD_SETTINGS


class Board:
    """  Class that represents our tic-tac-toe battlefield. """
    def __init__(self):
        self.board = [list("   ") for _ in range(3)]

    def reset_board(self):
        """  Simply reset the board with empty characters. """
        self.board = [list("   ") for _ in range(3)]

    def print_board(self, stdscr):
        """ Print board's graphical representation. """
        stdscr.addstr(2, 0, "Use arrows to move,  [SPACE] Mark spot,  [Q] Quit")
        stdscr.addstr(BOARD_SETTINGS["Y_OFFSET"], BOARD_SETTINGS["X_OFFSET"], "  │   │  ")
        stdscr.addstr(BOARD_SETTINGS["Y_OFFSET"] + 1, BOARD_SETTINGS["X_OFFSET"], "──┼───┼──")
        stdscr.addstr(BOARD_SETTINGS["Y_OFFSET"] + 2, BOARD_SETTINGS["X_OFFSET"], "  │   │  ")
        stdscr.addstr(BOARD_SETTINGS["Y_OFFSET"] + 3, BOARD_SETTINGS["X_OFFSET"], "──┼───┼──")
        stdscr.addstr(BOARD_SETTINGS["Y_OFFSET"] + 4, BOARD_SETTINGS["X_OFFSET"], "  │   │  ")

    def mark_play(self, stdscr, symbol, row, column, y_pos, x_pos):
        """
        Update board with given indexes and the board's graphical representation with given coordinates.

        Parameters:
            symbol: Character to be used in play marking.
            row, column: Coordinates to be used in curses printing.
            y_pos, x_pos: Indexes to be used in the actual board list.
        Return:
            Updated Board instance.
        """
        stdscr.addch(row, column, symbol)
        self.board[y_pos][x_pos] = symbol
        return self

    def get_board_state(self):
        """ Board attribute getter. """
        return self.board

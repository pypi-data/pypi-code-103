import copy
import curses
import itertools
import time

import settings
from board import Board
from player import Player
from base import TextUI
from ranking import Ranking


class TicTacToeTextUI(TextUI):
    """
    Child class of @Rui Rei's 'TextUI' parent class, where tic-tac-toe game logic is written.
    Probably fun to code review. Probably.
    """
    def __init__(self):
        super().__init__()
        self.x_pos = 1
        self.y_pos = 1
        self.played = False
        self.player1 = None
        self.player2 = None
        self.board = Board()
        self.game_over = True
        self.ranking = Ranking()
        self.player_choice = None
        self.current_player = None
        self.start_time = None
        self.end_time = 0
        self.elapsed_time = 0
        self.total_time = 0
        self.board_states = []

    def reset(self):
        """ Reset class attributes in case players wish to play again. """
        self.x_pos = 1
        self.y_pos = 1
        self.played = False
        self.player1 = None
        self.player2 = None
        self.board.reset_board()
        self.game_over = True
        self.board_states = []
        self.player_choice = None
        self.current_player = None
        self.start_time = None
        self.end_time = 0
        self.elapsed_time = 0
        self.total_time = 0

    def draw(self):
        """
        Method called in @Rui Rei's "TextUI" class in mainloop.
        Handle class attribute initialization and screen printing if first time called in a match,
        or screen updates if match is ongoing.
        """
        if self.game_over:
            curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Initialize curses color pair
            self.screen.bkgd(" ", curses.color_pair(1) | curses.A_BOLD)  # Set color pair on curses screen
            self.screen.clear()
            curses.echo()
            self.screen.nodelay(False)
            self.player1 = self.create_player(1)
            self.player2 = self.create_player(
                2,
                forbidden_name=self.player1.name,
                forbidden_symbol=self.player1.symbol,
            )
            self.screen.clear()
            curses.noecho()
            self.screen.nodelay(True)
            self.player_choice = itertools.cycle([self.player1, self.player2])
            self.current_player = next(self.player_choice)
            self.print_title()
            self.board.print_board(self.screen)
            self.screen.addstr(12, 0, f"{self.current_player.name}'s turn")
            self.game_over = False
            self.start_time = time.time()

        else:
            self.screen.move(10, 0)
            self.screen.clrtoeol()
            self.screen.addstr(10, 0, (str(round(self.elapsed_time, 3)) + " secs"))
            row, column = self.screen.getyx()
            self.screen.move(12, 0)
            self.screen.clrtoeol()
            self.screen.move(row, column)
            self.screen.addstr(12, 0, f"{self.current_player.name}'s turn")
            self.screen.move(
                settings.BOARD_SETTINGS["Y_OFFSET"] + self.y_pos * settings.BOARD_SETTINGS["Y_STEP"],
                settings.BOARD_SETTINGS["X_OFFSET"] + self.x_pos * settings.BOARD_SETTINGS["X_STEP"],
            )

    def print_title(self):
        """ Print a rather suggestive game title. """
        self.screen.addstr(0, 16, "Game of the cock")
        self.screen.hline(1, 0, "-", 49)

    def check_tie(self):
        """
        Verify if the current game state resulted in a tie.
        Iterate through the game board and check if it contains a witespace string,
        if it does, the game is still not over.

        Return:
            is_tie: Boolean True if current game state is a tie, False if not.
        """
        is_tie = True
        for row in self.board.board:
            if " " in row:
                is_tie = False

        if is_tie:
            self.screen.addstr(10, 0, "It's a tie!")

        return is_tie

    def check_win(self):
        """
        Verify if the current game state resulted in a win.
        This is called after every play, so the winner is always the current player.

        Return:
            Boolean True if current play resulted in a win, False if not.
        """

        def all_same(symbol_list):
            """
            Check if all elements of a list are the same.

            Parameters:
                symbol_list: List to check (Duh).
            """
            if symbol_list.count(symbol_list[0]) == len(symbol_list) and symbol_list[0] != " ":
                return True
            else:
                return False

        # Check horizontal winner
        for row in self.board.board:
            if all_same(row):
                self.screen.addstr(
                    10,
                    0,
                    f"{self.current_player.name} is the winner horizontally in {str(round(self.current_player.temp_time, 3))} secs!\nTotal play time: {str(round(self.total_time, 3))} secs",
                )
                return True

        # Check vertical winner
        for col in range(3):
            check = []
            for row in self.board.board:
                check.append(row[col])
            if all_same(check):
                self.screen.addstr(
                    10,
                    0,
                    f"{self.current_player.name} is the winner vertically in {str(round(self.current_player.temp_time, 3))} secs!\nTotal play time: {str(round(self.total_time, 3))} secs",
                )
                return True

        # Check upper-left-to-lower-right diagonal winner
        diags = []
        for ix in range(3):
            diags.append(self.board.board[ix][ix])
        if all_same(diags):
            self.screen.addstr(
                10,
                0,
                f"{self.current_player.name} is the winner diagonally (Upper left to lower right) in {str(round(self.current_player.temp_time, 3))} secs!\nTotal play time: {str(round(self.total_time, 3))} secs",
            )
            return True

        # Check lower-left-to-upper-right diagonal winner
        diags = []
        for col, row in enumerate(reversed(range(3))):
            diags.append(self.board.board[row][col])
        if all_same(diags):
            self.screen.addstr(
                10,
                0,
                f"{self.current_player.name} is the winner diagonally (Lower left to upper right) in {str(round(self.current_player.temp_time, 3))} secs!\nTotal play time: {str(round(self.total_time, 3))} secs",
            )
            return True

        return False

    def create_player(self, player_id, forbidden_name=None, forbidden_symbol=None):
        """
        Display player creation screen, get user input and verify if input is valid.

        Parameters:
            player_id: Flag that indicates if it is the first or second player created.
            forbidden_name: In case that it is player 2, this parameter contains the first player's name.
            forbidden_symbol: In case that it is player 2, this parameter contains the first player's symbol.
        Return:
            Created Player object.
        """
        self.print_title()
        forbidden_symbols = ["", " ", forbidden_symbol]
        forbidden_names = ["", forbidden_name]
        curses.echo()
        self.screen.nodelay(False)
        self.screen.addstr(2, 0, f"Create player {player_id}")
        self.screen.addstr(3, 0, "Name:")
        name = self.screen.getstr(3, 6).decode("UTF-8").strip(" ")
        valid_name = False
        while not valid_name:
            if name not in forbidden_names:
                valid_name = True
            else:
                self.screen.clear()
                self.print_title()
                self.screen.addstr(2, 0, f"Create player {player_id}")
                self.screen.addstr(3, 0, "Name:")
                self.screen.addstr(
                    5,
                    0,
                    f"* Name must not be blank.\n* Name must be different from the other player's name.",
                )
                name = self.screen.getstr(3, 6).decode("UTF-8").strip(" ")
        self.screen.move(5, 0)
        self.screen.clrtobot()

        valid_symbol = False
        while not valid_symbol:
            self.screen.addstr(4, 0, "Symbol:")
            symbol = self.screen.getstr(4, 8).decode("UTF-8")
            if len(symbol) == 1 and symbol not in forbidden_symbols:
                valid_symbol = True
            else:
                self.screen.clear()
                self.print_title()
                self.screen.addstr(2, 0, f"Create player {player_id}")
                self.screen.addstr(3, 0, f"Name: {name}")
                self.screen.addstr(
                    6,
                    0,
                    "* Symbol must not be blank.\n* Symbol must be only 1 character long.\n* Symbol must be different from the other player's symbol.",
                )
        self.screen.clear()
        return Player(name, symbol)

    def play_again(self, row):
        """
        Handle screen input and output to verify if players wish to play again.

        Parameters:
            row: Line number to start printing screen output.
        Return:
            will_play_again: Boolean True if players wish to play again, False if not.
        """
        will_play_again = False
        curses.echo()
        self.screen.nodelay(False)
        valid_answer = False
        while not valid_answer:
            self.screen.addstr(row, 0, "Play again? (y/n):")
            again = self.screen.getstr(row, 19).decode("UTF-8").strip(" ")
            if again in settings.POSITIVE_ANSWERS:
                self.screen.addstr(row + 2, 0, "Here we go again!\n(Press any key)")
                valid_answer = True
                will_play_again = True
            elif again in settings.NEGATIVE_ANSWERS:
                self.screen.addstr(
                    row + 2, 0, "Then make like a banana and split!\n(Press any key)"
                )
                valid_answer = True
                will_play_again = False
            else:
                self.screen.addstr(
                    row + 2,
                    0,
                    "Not a valid answer... Please choose wisely...\n(Press any key)",
                )
                self.screen.move(row, 0)
                self.screen.clrtoeol()

        self.screen.getkey()
        self.screen.nodelay(True)

        return will_play_again

    def play(self):
        """  Handle play made from pressing 'spacebar'. Do nothing if spot is already marked. """
        row, column = self.screen.getyx()
        if self.screen.inch(row, column) == settings.COLOR_CODE:  # curses.COLOR_BLACK
            self.played = True
            self.board.mark_play(
                self.screen,
                self.current_player.symbol,
                row,
                column,
                self.y_pos,
                self.x_pos,
            )
            self.board_states.append(copy.deepcopy(self.board.get_board_state()))
            self.end_time = time.time()
            self.elapsed_time = self.end_time - self.start_time
            self.current_player.update(game_over=False, temp_time=self.elapsed_time)
            self.total_time += self.elapsed_time

            row = 13
            if self.check_win():
                self.game_over = True
                self.current_player.update(temp_time=self.current_player.temp_time, game_over=True, won=True,
                                           keep_time=True)
                other_player = next(self.player_choice)
                other_player.update(temp_time=other_player.temp_time, game_over=True, won=False)
                self.ranking.update(self.current_player, other_player)

                row = self.ranking.print_ranking(self.screen, row)

            elif self.check_tie():
                self.game_over = True
                self.screen.addstr(11, 0, f"Total play time: {str(round(self.total_time, 3))} secs.")
                self.screen.move(12, 0)
                self.screen.clrtoeol()

            self.current_player = next(self.player_choice)
            self.start_time = time.time()

            if self.game_over:
                if self.play_again(row):
                    self.reset()
                else:
                    self.stop()

    def input(self, key):
        """ Manage key input operations. """
        if key == "KEY_UP":
            self.y_pos = max(0, self.y_pos - 1)
        elif key == "KEY_DOWN":
            self.y_pos = min(2, self.y_pos + 1)
        elif key == "KEY_LEFT":
            self.x_pos = max(0, self.x_pos - 1)
        elif key == "KEY_RIGHT":
            self.x_pos = min(2, self.x_pos + 1)
        elif key == "q" or key == "Q":
            self.stop()
        elif key == " ":
            self.play()

import copy
import curses

from base import TextUI

CH_PLAYER_X = 'X'
CH_PLAYER_O = 'O'
X_SHIFT = 1
Y_SHIFT = 4
MAX_MOVES = 9


class Tictactoe(TextUI):
    """ Class of Tic Tac Toe game
    @:param TextUI from base file (TextUI - courses)
    """

    def __init__(self):
        super().__init__()
        self.x_pos = 1
        self.y_pos = 1
        self.count_moves = 0
        self.board_game = [list('   ') for _ in range(3)]
        self.game_states = []
        self.player_flag = False
        self.end_game = False

    def print_title(self):
        """ Print title of game """
        self.screen.addstr(1, 20, 'TIC TAC TOE', curses.A_BOLD and curses.A_UNDERLINE)

    def print_board(self):
        """ Print board of game """
        self.screen.addstr(2, 3, 'Use arrows to move, [SPACE] Draw, [Q] Quit')
        self.screen.addstr(Y_SHIFT, X_SHIFT + 4, '{} │ {} │ {}'.format(
            self.board_game[0][0], self.board_game[0][1], self.board_game[0][2]))
        self.screen.addstr(Y_SHIFT + 1, X_SHIFT + 4, '──┼───┼──')
        self.screen.addstr(Y_SHIFT + 2, X_SHIFT + 4, '{} │ {} │ {}'.format(
            self.board_game[1][0], self.board_game[1][1], self.board_game[1][2]))
        self.screen.addstr(Y_SHIFT + 3, X_SHIFT + 4, '──┼───┼──')
        self.screen.addstr(Y_SHIFT + 4, X_SHIFT + 4, '{} │ {} │ {}'.format(
            self.board_game[2][0], self.board_game[2][1], self.board_game[2][2]))

    def print_players(self):
        """ Print identification of players in each move """
        self.screen.addstr(Y_SHIFT + 6, X_SHIFT + 4, 'Player {}'.format(CH_PLAYER_X),
                           curses.A_BOLD and curses.A_UNDERLINE if self.player_flag == 0 else 0)
        self.screen.addstr(Y_SHIFT + 7, X_SHIFT + 4, 'Player {}'.format(CH_PLAYER_O),
                           curses.A_BOLD and curses.A_UNDERLINE if self.player_flag == 1 else 0)

    def switch_player(self):
        """ Change the player """
        self.player_flag = not self.player_flag
        self.print_players()

    def check_victory(self, board, y, x) -> bool:
        """ Check for victory """
        if board[0][x] == board[1][x] == board[2][x]:                   # check horizontal line
            return True
        elif board[y][0] == board[y][1] == board[y][2]:                 # check vertical line
            return True
        elif x == y and board[0][0] == board[1][1] == board[2][2]:      # check diagonal
            return True
        elif x + y == 2 and board[0][2] == board[1][1] == board[2][0]:  # check diagonal
            return True
        return False

    def print_result(self):
        """ Print the result of the game. """
        if self.check_victory(self.board_game, self.y_pos, self.x_pos):
            self.screen.addstr(Y_SHIFT + 2, X_SHIFT + 20, 'Player {} wins'.format(
                CH_PLAYER_X if self.player_flag else CH_PLAYER_O), curses.A_REVERSE)
            self.screen.addstr(Y_SHIFT + 3, X_SHIFT + 17, 'Press any key to quit', curses.A_BLINK)
            self.end_game = True
            curses.curs_set(0)
        elif self.count_moves == MAX_MOVES:
            self.screen.addstr(Y_SHIFT + 2, X_SHIFT + 20, 'Nobody win', curses.A_REVERSE)
            self.screen.addstr(Y_SHIFT + 3, X_SHIFT + 17, 'Press any key to quit', curses.A_BLINK)
            self.end_game = True
            curses.curs_set(0)

    def draw(self):
        """ Draw all the TUI of game """
        curses.resize_term(20, 50)
        self.screen.border()
        self.print_title()
        self.print_board()
        x_step = 4
        y_step = 2
        if not self.end_game:
            self.print_players()
            self.screen.move(Y_SHIFT + self.y_pos * y_step, X_SHIFT + self.x_pos * x_step + 4)
        else:
            self.print_result()

    def move(self):
        """ Make the update of each move in game. """
        # Get x and y of screen
        y, x = self.screen.getyx()
        # Validates if the move can be done (empty cell)
        if self.screen.inch(y, x) == ord(" "):
            # Update number of moves
            self.count_moves += 1
            # Draw the new move
            self.board_game[self.y_pos][self.x_pos] = CH_PLAYER_O if self.player_flag else CH_PLAYER_X
            # Save each game state
            self.game_states.append(copy.deepcopy(self.board_game))
            # Check for results
            self.print_result()
            # Switch player
            self.switch_player()

    def input(self, key):
        """ All the input options for play the game. """
        if not self.end_game:
            if key == "KEY_UP":
                self.y_pos = max(0, self.y_pos - 1)
            elif key == "KEY_DOWN":
                self.y_pos = min(2, self.y_pos + 1)
            elif key == "KEY_LEFT":
                self.x_pos = max(0, self.x_pos - 1)
            elif key == "KEY_RIGHT":
                self.x_pos = min(2, self.x_pos + 1)
            elif key == " ":
                self.move()
            elif key == "q" or key == "Q":
                self.stop()
        else:
            if key:
                self.stop()


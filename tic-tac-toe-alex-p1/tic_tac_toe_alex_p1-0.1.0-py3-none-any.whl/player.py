class Player:
    """ Class that represents a daring tic-tac-toe player and stores each player's info. """
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol
        self.total_games = 0
        self.temp_time = 0
        self.best_time = float("inf")
        self.wins = 0

    def update(self, temp_time=float("inf"), game_over=False, won=False, keep_time=True):
        """
        Update some player info, depending on when this is called.

        Parameters:
            temp_time: time to update a player's play time.
            game_over: Boolean True if the match has ended, False if not.
            won: Boolean True if player has won the match, False if not.
            keep_time: Boolean True if player's 'temp_time' should persist, False if not.
        """
        if game_over:
            self.total_games += 1
            if won:
                self.wins += 1
                self.best_time = min(self.best_time, temp_time)
            if not keep_time:
                self.temp_time = 0
        else:
            self.temp_time += temp_time

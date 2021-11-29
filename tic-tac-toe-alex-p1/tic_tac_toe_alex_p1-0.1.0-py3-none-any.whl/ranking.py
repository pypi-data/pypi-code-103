class Ranking:
    """
    Class that represents the game session's 'high-scores' (Shortest time to win a match).
    A well-intentioned attempt to add some competitiveness to the game of tic-tac-toe.
    """
    def __init__(self):
        self.ranking = []

    def update(self, player1, player2):
        """
        Iterate through each player in the ranking and call Player.update() if they already exist.
        Append players to the ranking if they are not already a part of the fun.
        Also, sort the ranking list from shortest winning time to longest.

        Parameters:
            player1: Winning player.
            player2: Losing player.
        """

        p1_existed = False
        p2_existed = False

        for player in self.ranking:
            if player.name == player1.name:
                player.update(temp_time=player1.temp_time, game_over=True, won=True)
                p1_existed = True
            elif player.name == player2.name:
                player.update(temp_time=player2.temp_time, game_over=True, won=False)
                p2_existed = True

        if not p1_existed:
            self.ranking.append(player1)
        if not p2_existed:
            self.ranking.append(player2)

        self.ranking.sort(key=lambda p: p.best_time)

    def print_ranking(self, screen, row):
        """
        Print current session's player ranking,
        containing each player's shortest winning time, total wins and total games played

        Parameters:
            screen: Game's curses screen.
            row: Line number to start printing the ranking.
        Return:
            row: Line number where future awesome things will be printed.
        """
        screen.move(12, 0)
        screen.clrtobot()
        for player in self.ranking:
            if player.best_time == float("inf"):
                temp_best_time = "-----"
            else:
                temp_best_time = str(round(player.best_time, 3))
            screen.addstr(
                row,
                0,
                f"{player.name}: Best time: {temp_best_time}     Wins: {player.wins}     Total games played: {player.total_games}",
            )
            row += 1
        row += 1
        return row

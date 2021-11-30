
class MatchupHistory:
    def __init__(self, manager_name, opponent_name):
        self.manager_name = manager_name
        self.opponent_name = opponent_name
        self.manager_avg_score = None
        self.opponent_avg_score = None
        self.manager_wins = 0
        self.opponent_wins = 0
        self.matchup_history_df = None

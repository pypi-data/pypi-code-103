from deez_stats.helpers.telo import Elo


class WeeklyMatchup:
    def __init__(self):
        self.is_playoffs = 0
        self.is_consolation = 0
        self.manager_id = 0
        self.manager_name = None
        self.manager_points_total = 0
        self.manager_win_probability = 0
        self.manager_projected_points = 0
        self.manager_outcome = None
        self.manager_curr_elo = 0
        self.manager_updated_elo = 0
        self.manager_elo_change = 0
        self.opponent_id = 0
        self.opponent_name = None
        self.opponent_score = 0
        self.opponent_points_total = 0
        self.opponent_win_probability = 0
        self.opponent_projected_points = 0
        self.opponent_outcome = None
        self.opponent_curr_elo = 0
        self.opponent_updated_elo = 0
        self.opponent_elo_change = 0

    def eval_result_from_matchup(self):
        if self.manager_points_total > self.opponent_points_total:
            self.manager_result = 'W'
            self.opponent_result = 'L'
        elif self.manager_points_total < self.opponent_points_total:
            self.manager_result = 'L'
            self.opponent_result = 'W'
        else:
            self.manager_result = 'T'
            self.opponent_result = 'T'

        elo = Elo(self.manager_curr_elo)
        elo.matchup_result(self.opponent_curr_elo, self.manager_result)
        self.manager_updated_elo = elo.RpA
        self.opponent_updated_elo = elo.RpB
        self.manager_elo_change = self.manager_updated_elo - self.manager_curr_elo
        self.opponent_elo_change = self.opponent_updated_elo - self.opponent_curr_elo

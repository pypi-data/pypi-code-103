from .helpers import database_query as dbq


class Standings:
    def __init__(self, season, week, manager_name):
        self.current_rank = 0
        self.manager_name = manager_name
        self.elo = 0
        self.elo_change = 0
        self.rank_change = 0

        dates = dbq._get_previous_season_week(season, week)
        self.season = dates[0]
        self.week = dates[1]
        dates = dbq._get_previous_season_week(self.season, self.week)
        self.prev_season = dates[0]
        self.prev_week = dates[1]
        self.create_standings()

    def create_standings(self):
        curr_manager_df = dbq.get_weekly_manager_df(self.season, self.week, self.manager_name)
        self.elo = int(curr_manager_df['elo'])
        self.elo_change = int(curr_manager_df['elo_change'])

        curr_df = dbq.get_weekly_df(self.season, self.week)
        prev_df = dbq.get_weekly_df(self.prev_season, self.prev_week)
        curr_df['ranking'] = curr_df['elo'].rank(ascending=False)
        prev_df['ranking'] = prev_df['elo'].rank(ascending=False)

        curr_idx = curr_df.index[curr_df['manager_name'] == self.manager_name][0]
        prev_idx = prev_df.index[prev_df['manager_name'] == self.manager_name][0]
        self.current_rank = int(curr_df['ranking'][curr_idx])
        prev_rank = int(prev_df['ranking'][prev_idx])
        self.rank_change = int(prev_rank - self.current_rank)

import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.cm as cm


class Elo:
    def __init__(self, K=32, init_elo=500, num_teams=12, weeks=10):
        self.K = K
        self.init_elo = init_elo
        self.num_teams = num_teams
        self.weeks = weeks
        self.num_matchups = self.num_teams // 2
        self.team_skill = np.arange(1, self.num_teams + 1, 1)
        # self.team_skill = self.num_teams * [10]
        self.teams = {}
        for i in range(self.num_teams):
            self.teams[i] = {'elo': self.init_elo, 'skill': self.team_skill[i]}
        self.schedule = None
        self.elo_hist = []

    def get_expected_elo(self, elos):
        Q_A = 10 ** (elos[0] / 400)
        Q_B = 10 ** (elos[1] / 400)
        E_A = Q_A / (Q_A + Q_B)
        E_B = Q_B / (Q_A + Q_B)
        return [E_A, E_B]

    def update_elo(self, R, E, team_keys, outcome, week):
        Rp_A = int(round(R[0] + self.K * (outcome[0] - E[0])))
        Rp_B = int(round(R[1] + self.K * (outcome[1] - E[1])))
        self.teams[team_keys[0]]['elo'] = Rp_A
        self.teams[team_keys[1]]['elo'] = Rp_B
        self.elo_hist[week][team_keys[0]] = Rp_A
        self.elo_hist[week][team_keys[1]] = Rp_B

    def run_h2h_matchup(self, skills):
        return [1, 0] if (skills[0]) > (skills[1]) else [0, 1]

    def run_season(self):
        for week in range(len(self.schedule)):
            if week == 0:
                self.elo_hist.append(self.num_teams * [self.init_elo])
            else:
                self.elo_hist.append(self.num_teams * [0])
            for j in range(self.num_matchups):
                game = elo.schedule[week - 1][j - 1]
                team_keys = [game[0], game[1]]
                R = [self.teams[team_keys[0]]['elo'], self.teams[team_keys[1]]['elo']]
                skills = [self.teams[team_keys[0]]['skill'], self.teams[team_keys[1]]['skill']]
                E = self.get_expected_elo(R)
                outcome = self.run_h2h_matchup(skills)
                self.update_elo(R, E, team_keys, outcome, week)

    def create_balanced_round_robin(self):
        self.schedule = []
        players = list(self.teams.keys())
        n = len(players)
        map = list(range(n))
        mid = n // 2
        for i in range(n - 1):
            l1 = map[:mid]
            l2 = map[mid:]
            l2.reverse()
            round = []
            for j in range(mid):
                t1 = players[l1[j]]
                t2 = players[l2[j]]
                if j == 0 and i % 2 == 1:
                    # flip the first match only, every other round
                    # (this is because the first match always involves the last player in the list)
                    round.append((t2, t1))
                else:
                    round.append((t1, t2))
            self.schedule.append(round)
            # rotate list by n/2, leaving last element at the end
            map = map[mid:-1] + map[:mid] + map[-1:]
        return self.schedule

    def create_random_weeks(self):
        self.schedule = []
        for i in range(self.weeks):
            round = []
            players = list(self.teams.keys())
            for j in range(len(players) // 2):
                t1 = players.pop(random.randint(0, len(players) - 1))
                t2 = players.pop(random.randint(0, len(players) - 1))
                round.append([t1, t2])
            self.schedule.append(round)

    def plot_elo_history(self):
        new_arr = np.array(self.elo_hist).T
        colors = cm.rainbow(np.linspace(0, 1, elo.num_teams))
        for i in range(self.num_teams):
            plt.plot(np.arange(0, self.weeks), new_arr[i], color=colors[i])
        plt.legend(self.teams.keys())
        plt.show()


elo = Elo(K=32, init_elo=700, num_teams=12, weeks=100)

elo.create_random_weeks()
# elo.create_balanced_round_robin()
elo.run_season()
elo.plot_elo_history()

class Elo:
    def __init__(self, ra):
        self.K = 32
        self.RA = ra
        self.RB = 0
        self.EA = 0
        self.EB = 0
        self.SA = 0
        self.SB = 0
        self.RpA = 0
        self.RpB = 0

    def matchup_result(self, rb, result):
        self.RB = rb
        if result == 'W':
            self.SA = 1
            self.SB = 0
        elif result == 'L':
            self.RB = rb
            self.SA = 0
            self.SB = 1
        elif result == 'T':
            self.RB = rb
            self.SA = 0.5
            self.SB = 0.5

        self.update_elo()

    def update_elo(self):
        self.EA = 1 / (1 + 10 ** ((self.RB - self.RA) / 400))
        self.EB = 1 / (1 + 10 ** ((self.RA - self.RB) / 400))
        self.RpA = int(self.RA + round(self.K * (self.SA - self.EA)))
        self.RpB = int(self.RB + round(self.K * (self.SB - self.EB)))

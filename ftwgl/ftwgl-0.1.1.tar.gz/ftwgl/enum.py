from enum import Enum


class UserTeamRole(str, Enum):
    leader = 'leader'
    captain = 'captain'
    member = 'member'
    inactive = 'inactive'
    invited = 'invited'


class MatchType(str, Enum):
    group = 'group'
    playoff = 'playoff'
    grand_final = 'grand_final'
    silver_final = 'silver_final'


class GameType(int, Enum):
    team_survivor = 4
    capture_the_flag = 7

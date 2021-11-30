from yahoo_fantasy_api import yhandler
from .helpers import json_query as jq


class ManagerInfo:
    def __init__(self, sc, league_key, team_id):
        self.sc = sc
        self.yhandler = yhandler.YHandler(sc)
        self.league_key = league_key
        self.team_id = str(team_id)
        self.team_key = self.league_key + '.t.' + self.team_id
        self.team_name = None
        self.team_url = None
        self.team_logo_url = None
        self.waiver_priority = None
        self.faab_balance = None
        self.number_of_moves = None
        self.number_of_trades = None
        self.manager_id = None
        self.manager_name = None
        self.manager_logo_url = None
        self.raw_manager_info = None
        self._update_ManagerInfo()

    def _get_manager_info_raw(self):
        manager_info = self.yhandler.get('team/' + self.team_key)
        return manager_info

    def _clean_manager_name(self):
        """Handles formatting names since there is no uniformity

        """
        cleaned_names = jq.get_cleaned_names()
        try:
            self.manager_name = cleaned_names[self.manager_name]
        except KeyError:  # not everyone's name is wrong so pass on the correct names
            pass

    def _update_ManagerInfo(self):
        self.raw_manager_info = self._get_manager_info_raw()
        self.raw_manager_info = self.raw_manager_info['fantasy_content']

        self.team_name = list(jq.search_json_key(self.raw_manager_info, '.team[0].name'))[0]
        self.team_url = list(jq.search_json_key(self.raw_manager_info, '.team[0].url'))[0]
        self.team_logo_url = list(jq.search_json_key(self.raw_manager_info, '.team[0].team_logos[0].team_logo.url'))[0]
        self.waiver_priority = list(jq.search_json_key(self.raw_manager_info, '.team[0].waiver_priority'))[0]
        self.faab_balance = list(jq.search_json_key(self.raw_manager_info, '.team[0].faab_balance'))[0]
        self.number_of_moves = list(jq.search_json_key(self.raw_manager_info, '.team[0].number_of_moves'))[0]
        self.number_of_trades = list(jq.search_json_key(self.raw_manager_info, '.team[0].number_of_trades'))[0]
        self.manager_id = list(jq.search_json_key(self.raw_manager_info, '.team[0].managers[0].manager.manager_id'))[0]
        self.manager_name = list(jq.search_json_key(self.raw_manager_info, '.team[0].managers[0].manager.nickname'))[0]
        self._clean_manager_name()
        self.manager_logo_url = list(jq.search_json_key(self.raw_manager_info, '.team[0].managers[0].manager.image_url'))[0]

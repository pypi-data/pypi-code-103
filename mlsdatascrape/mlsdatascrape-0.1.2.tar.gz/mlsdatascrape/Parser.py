from typing import List, Dict, Any


class Parser:

    def __init__(self, table_obj):
        self.table_obj = table_obj

    # parse_club_table - parses the season table and creates a list of dictionaries for each club
    def parse_club_table(self):
        # create an array of club names
        clubs = self.table_obj.find('tbody').find_all('tr')

        cells = []
        season_table: List[Dict[str, Any]] = []

        for row in clubs:
            cells.append(row.find_all('td'))

        for cell in cells:
            count = 0
            club = {}
            while count < len(cell):
                club[str(cell[count].get('data-stat'))] = cell[count].get_text().strip()
                count += 1
            season_table.append(club)

        return season_table
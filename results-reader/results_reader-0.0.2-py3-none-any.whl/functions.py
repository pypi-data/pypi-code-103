""" Helper Methods"""
import click
from icecream import ic
import pandas as pd
import re


def parse_file_data(file=None):

    with open(f"{file}") as file_data:
        temp=""
        entry_1 = ""
        entry_2 = ""
        team1_score = ""
        team2_score = ""
        team1_name = ""
        team2_name = ""
        orig_list = []
        final_score_list = {}
        for line in file_data:
            temp = line.split(',')
            # Get ONLY the name, remove whitespaces and NL tag
            team1_name = ''.join((c for c in temp[0] if not c.isdigit())).strip("\n").strip()
            team2_name = ''.join((c for c in temp[1]if not c.isdigit())).strip("\n").strip()
            team1_score = re.search(r'\d+', temp[0]).group()
            team2_score = re.search(r'\d+', temp[1]).group()
            # Initialize new Keys with value of 0
            if team1_name not in final_score_list:
                final_score_list[str(team1_name)] = 0
            if team2_name not in final_score_list:
                final_score_list[str(team2_name)] = 0

            if team1_score < team2_score:
                final_score_list[team2_name] += 3
                final_score_list[team1_name] += 0
            elif team2_score < team1_score:
                final_score_list[team1_name] += 3
                final_score_list[team2_name] += 0
            elif team1_score == team2_score:
                final_score_list[team1_name] += 1
                final_score_list[team2_name] += 1
        df = pd.DataFrame(data=list(final_score_list.items()), columns=['Teams', 'Points'])
        df.sort_values(by=['Points', 'Teams'], axis=0, ascending=[False, True],
                       kind='quicksort', ignore_index=True, inplace=True)
        df.set_index(keys=['Teams'],inplace=True, drop=True)
        return df


def parse_input_string(input_string: str):

    return True
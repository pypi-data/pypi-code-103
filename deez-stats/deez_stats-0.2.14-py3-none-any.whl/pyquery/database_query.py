import sqlite3
import pandas as pd
import pathlib
from deez_stats.matchup_history import MatchupHistory

INIT_ELO = 700
HERE = (pathlib.Path(__file__).parent)
DATABASE_FILE = (HERE / 'files/database/history.db')


def execute_sqlite(sql_query):
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()
    result = cursor.execute(sql_query)
    result = list(result)
    cursor.close()
    connection.close()
    return result


def execute_commit(sql_query):
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()
    result = cursor.execute(sql_query)
    result = list(result)
    cursor.close()
    connection.commit()
    connection.close()
    return result


def execute_row_factory(sql_query):
    connection = sqlite3.connect(DATABASE_FILE)
    # connection.row_factory = lambda cursor, row: row[0]
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    result = cursor.execute(sql_query)
    # result = list(result)
    cursor.close()
    connection.close()
    return result


def get_matchup_history(manager_name, opponent_name):
    """Gets all of the historical matchups and run some basic stats

    """
    mh = MatchupHistory(manager_name, opponent_name)

    all_historical_matchups = find_all_historical_matchups(manager_name, opponent_name)

    columns = ['Season', 'Manager Score', 'Opponent Score', 'Result']
    mh.matchup_history_df = pd.DataFrame(all_historical_matchups, columns=columns)

    mh.manager_avg_score = mh.matchup_history_df['Manager Score'].mean()
    mh.opponent_avg_score = mh.matchup_history_df['Opponent Score'].mean()

    try:
        mh.manager_wins = mh.matchup_history_df.Result.value_counts().W
    except AttributeError:
        mh.manager_wins = 0

    try:
        mh.opponent_wins = mh.matchup_history_df.Result.value_counts().L
    except AttributeError:
        mh.opponent_wins = 0
    return mh


def find_all_historical_matchups(manager_name, opponent_name):
    """Finds all of the historical matchups in the database

    """
    query_string = '''
        SELECT  season,
                manager_score,
                opponent_score,
                result
        FROM    schedule
        WHERE   manager_name = "{}" AND opponent_name = "{}"
    '''.format(manager_name, opponent_name)
    result = execute_sqlite(query_string)
    return result


def update_weekly_results(li, update=False):
    managers = list(li.manager_names.values())

    for matchup in li.weekly_matchups:
        row = [li.season]
        row.append(li.week)
        row.append(matchup.manager_name)
        row.append(matchup.manager_points_total)
        row.append(matchup.opponent_name)
        row.append(matchup.opponent_points_total)
        
        matchup.eval_result_from_matchup()
        row.append(matchup.manager_result)
        row.append(matchup.manager_updated_elo)
        row.append(matchup.manager_elo_change)

        if update is True:
            update_database_row(row)
        else:
            print(row)

        row = [li.season]
        row.append(li.week)
        row.append(matchup.opponent_name)
        row.append(matchup.opponent_points_total)
        row.append(matchup.manager_name)
        row.append(matchup.manager_points_total)
        row.append(matchup.opponent_result)
        row.append(matchup.opponent_updated_elo)
        row.append(matchup.opponent_elo_change)

        if update is True:
            update_database_row(row)
        else:
            print(row)

        managers.remove(matchup.manager_name)
        managers.remove(matchup.opponent_name)

    if li.is_quarterfinals or li.is_semifinals or li.is_finals:
        for manager in managers:
            row = [li.season]
            row.append(li.week)
            row.append(manager)
            row.append('NULL')  # manager points total
            row.append('NULL')  # opponent name
            row.append('NULL')  # opponent points total
            row.append('NULL')  # result
            row.append(get_current_elo(li.season, li.week, manager))
            row.append(0)       # elo change
            if update is True:
                update_database_row(row)
            else:
                print(row)


def update_database_row(row):
    query_string = '''
        INSERT INTO     schedule (
                        season,
                        week,
                        manager_name,
                        manager_score,
                        opponent_name,
                        opponent_score,
                        result,
                        elo,
                        elo_change)
        VALUES          ({}, {}, '{}', {}, '{}', {}, '{}', {}, {})
    '''.format(*row)
    execute_commit(query_string)




def get_current_elo(season, week, manager_name):
    if season == 2015 and week == 1:
        current_elo = INIT_ELO  # only for year 1 week 1
    else:
        p_season, p_week, p_year_flg = _get_previous_season_week(season, week)
        query_string = '''
            SELECT  elo
            FROM    schedule
            WHERE   season = {} AND week = {} AND manager_name="{}"
        '''.format(p_season, p_week, manager_name)
        current_elo = execute_sqlite(query_string)
        if current_elo:
            current_elo = current_elo[0][0]
        else:
            current_elo = INIT_ELO
    return current_elo


def _get_previous_season_week(season, week):
    p_year_flg = False
    if (week - 1) == 0:
        season = season - 1
        if season > 2020:
            week = 17
        else:
            week = 16
        p_year = True
    else:
        week = week - 1
        season = season
        p_year_flg = False
    return [season, week, p_year_flg]


def get_past_matchups(season, week):
    query_string = '''
        SELECT  *
        FROM    schedule
        WHERE   season = "{}" AND week = "{}"
    '''.format(season, week)
    result = execute_sqlite(query_string)
    return result


def get_table_column_names(table):
    query_string = '''
        PRAGMA table_info({})
    '''.format(table)
    result = execute_sqlite(query_string)
    result = [i[1] for i in result]
    return result


def get_weekly_df(season, week):
    current_week_df = pd.DataFrame(get_past_matchups(season, week))
    current_week_df.columns = get_table_column_names('schedule')
    return current_week_df


# miscellaneous functions that may be helpful

# def get_manager_score_history(manager_name):
#     query_string = '''
#         SELECT  manager_score
#         FROM    schedule
#         WHERE   manager_name = "{}"
#         ORDER BY manager_score DESC;
#     '''.format(manager_name)
#     result = execute_row_factory(query_string)
#     return result

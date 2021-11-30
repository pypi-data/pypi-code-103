# from . import database_query as dbq

# df = pd.DataFrame(dbq.get_schedule_table())
# df.columns = dbq.get_table_column_names('schedule')
# manager_scores = df['manager_score']
# opponent_scores = df['opponent_score']
# df['delta'] = manager_scores - opponent_scores
# df_new = df.dropna()
# df_new = df_new.drop(df_new[df_new['delta'] <= 0].index)

# largest_win_idx = df_new['delta'].idxmax()
# smallest_win_idx = df_new['delta'].idxmin()

# print(df.iloc[smallest_win_idx])


# manager_name = 'Tom'
# df = pd.DataFrame(dbq.get_manager_score_history(manager_name))
# df.columns = dbq.get_table_column_names('schedule')
# manager_scores = df['manager_score']
# opponent_scores = df['opponent_score']

# highest_score_idx = manager_scores.idxmax()
# lowest_score_idx = manager_scores.idxmin()

# df['delta'] = manager_scores - opponent_scores
# df_new = df.dropna()
# df_new = df_new.drop(df_new[df_new['delta'] < 0].index)
# largest_win_idx = df_new['delta'].idxmax()
# smallest_win_idx = df_new['delta'].idxmin()

# highest_score = week_info(manager_name, highest_score_idx)
# lowest_score = week_info(manager_name, lowest_score_idx)
# largest_win = week_info(manager_name, largest_win_idx)
# smallest_win = week_info(manager_name, smallest_win_idx)

# print('{}\'s highest score was {} in {} week {} against {} who had {}.'.format(*highest_score))
# print('{}\'s lowest score was {} in {} week {} against {} who had {}.'.format(*lowest_score))
# print('{}\'s largest win was {} in {} week {} against {} who had {}.'.format(*largest_win))
# print('{}\'s smallest win was {} in {} week {} against {} who had {}.'.format(*smallest_win))

# print('\
# Manager: {}\n\
# Highest Score: {}\n\
# Lowest Score: {}'.format(manager_name, manager_score_max, manager_score_min))


# league = yfa.League(leagueinfo.sc, leagueinfo.league_key)
# data = yq.json_query(leagueinfo.sc, 'league/{}/players;player_keys=406.p.30123/stats;week=1'.format(leagueinfo.league_key))

# data = league.yhandler.get_player_raw(leagueinfo.league_id, ids='29399')

# jq.dump_to_outfile(data, num=1)
# print(roster)

# manager_score_history = []
# columns = []

# for i in range(1, leaguestats.league_size + 1):
#     manager_score_history.append(dbq.get_manager_score_history(leaguestats.manager_names[i]))
#     columns.append(leaguestats.manager_names[i])

# df = pd.DataFrame(manager_score_history).T
# df.columns = columns
# df = df.reindex(df.mean().sort_values(ascending=False).index, axis=1)


# od.display(df)

# df.boxplot()
# plt.xlabel('Manager Names')
# plt.ylabel('Historical Scores')
# plt.title('Box and Whisker Plot of Manager Scores')
# plt.show()


# team = yfa.Team(leaguestats.sc, leaguestats.league_id + '.t.1')
# print(team.roster())

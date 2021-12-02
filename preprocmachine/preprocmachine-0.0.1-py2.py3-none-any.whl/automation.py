"""A tool to automate preprocessing phase."""

import pandas as pd
from .preprocessing.outlier_detection import (
    apply_Local_Factor_Outlier_Detection,
    apply_MAD_Score_Based_Outlier_Detection,
)
from .preprocessing.feature_selection import (
    apply_K_Best_Feature_Selection,
    apply_Variance_Based_Feature_Selection,
    apply_Missing_Ratio_Feature_Selection,
)
from .preprocessing.imputation import (
    apply_most_frequent_value_imputer,
    apply_mean_imputer,
    apply_median_imputer,
)
from .preprocessing.normalization import (
    apply_Min_Max_Normalization,
    apply_Z_Score_Normalization,
    apply_Quantile_Normalization,
)
from .algorithms.linear_regression import lr_get_mse
from .utils.greedy import epsilon


def preprocmachine(df, target, goal="LinReg", gamma=0.8):

    numExpl = 300

    start = [lr_get_mse]
    imputation = [
        # apply_KNN_Imputation,
        apply_most_frequent_value_imputer,
        apply_mean_imputer,
        apply_median_imputer,
    ]
    outlier_detection = [
        apply_MAD_Score_Based_Outlier_Detection,
        # apply_Inter_Quantile_Range_Outlier_Detection,
        apply_Local_Factor_Outlier_Detection,
    ]
    normalization = [
        apply_Z_Score_Normalization,
        apply_Min_Max_Normalization,
        apply_Quantile_Normalization,
    ]
    feature_selection = [
        apply_Missing_Ratio_Feature_Selection,
        apply_K_Best_Feature_Selection,
        apply_Variance_Based_Feature_Selection,
    ]
    goal = [lr_get_mse]

    statefuncs = (
        start
        + imputation
        + outlier_detection
        + normalization
        + feature_selection
        + goal
    )
    statenames = []
    for i in statefuncs:
        statenames.append(i.__name__)

    # generate r table
    threshold1 = len(start) - 1
    threshold2 = threshold1 + len(imputation)
    threshold3 = threshold2 + len(outlier_detection)
    threshold4 = threshold3 + len(normalization)
    threshold5 = threshold4 + len(feature_selection)
    threshold6 = threshold5 + len(goal)

    r_table = []
    for i in range(len(statefuncs)):
        temp = []
        for j in range(len(statefuncs)):
            if i == len(statefuncs) - 1:
                temp.append(0)
            elif j == len(statefuncs) - 1:
                temp.append(1)
            elif (
                (i > threshold5 and j <= threshold6)
                or (i > threshold4 and j <= threshold5)
                or (i > threshold3 and j <= threshold4)
                or (i > threshold2 and j <= threshold3)
                or (i > threshold1 and j <= threshold2)
                or i == j
            ):
                temp.append(-1)
            else:
                temp.append(0)
        r_table.append(temp)

    #     initialize Q matrix

    q_table = []
    for i in range(len(statefuncs)):
        temp = []
        for j in range(len(statefuncs)):
            temp.append(0)
        q_table.append(temp)

    #     establish possible entry points
    entry_range = 0
    goal_state = len(statefuncs) - 1

    safecopy = pd.DataFrame.copy(df)

    for i in range(numExpl):

        # clear_output(wait=False)
        print("Starting exploration", i + 1, "/", numExpl)
        state = 0
        route = []  # will store state history for this exploration
        total_q = 0
        route.append(state)
        currExploreDF = pd.DataFrame.copy(df)
        currExploreDF, currExploreError = statefuncs[state](currExploreDF, target)

        while state != goal_state:
            possible_states = [i for i, val in enumerate(r_table[state]) if val >= 0]
            possible_qs = [q_table[state][i] for i in possible_states]
            prob = (i / numExpl) * 0.7
            next_state = epsilon(possible_states, possible_qs, prob)
            print("Moved from", state, "-->", next_state)

            # apply new state's proc to current df
            currExploreDF, newExploreError = statefuncs[next_state](
                currExploreDF, target
            )

            if currExploreError == float("inf") and newExploreError == float("inf"):
                newReward = -1
            elif currExploreError == float("inf"):
                newReward = 1
            elif newExploreError == float("inf"):
                newReward = -2
            else:
                newReward = (
                    (currExploreError - newExploreError) / currExploreError
                ) * 100
            reward = newReward
            currExploreError = newExploreError

            # find max Q value out of all possible actions from new state
            possible_states = [
                i for i, val in enumerate(r_table[next_state]) if val >= 0
            ]
            possible_qs = [q_table[next_state][i] for i in possible_states]
            max_q = max(possible_qs)

            # calculate new Q value for this state
            q_table[state][next_state] = (
                reward + gamma * max_q + r_table[state][next_state]
            )

            total_q += q_table[state][next_state]

            # move to next state
            state = next_state

            # record path
            route.append(state)

    print("Current Q table")
    for i in range(0, len(q_table)):
        print(q_table[i])

    # find best route
    best_route = []
    q_vals = []
    state = 0
    q = 0
    route.append(state)
    while state != len(statefuncs) - 1:
        possible_states = [i for i, val in enumerate(r_table[state]) if val >= 0]
        possible_qs = [q_table[state][i] for i in possible_states]
        # choose highest q and get corresponding state
        max_q = max(possible_qs)
        q_vals.append(max_q)
        q += max_q
        index = possible_qs.index(max_q)
        next_state = possible_states[index]
        best_route.append(next_state)
        state = next_state

    # print route in names
    route_names = []
    for i in best_route:
        route_names.append(statenames[i])
    print(best_route)
    print(route_names)
    print(q_vals)

    # run best route
    df1, initialerror = lr_get_mse(safecopy, "target")
    df2 = pd.DataFrame.copy(safecopy)
    finalerror = 0
    for i in range(0, len(best_route) - 1):
        df2, finalerror = statefuncs[best_route[i]](df2, target)
    print("MSE:", initialerror, "-->", finalerror)
    print("Diff:", initialerror - finalerror)
    return df2

from random import random, choice

from relic_engine import get_relic_list, get_set_data

import utility

num_runs_dict = {
    'Solo': 1,
    '1b1': 4,
    '2b2': 2,
    '3b3': (4 / 3),
    '4b4': 1,
    '8b8': 1
}

chance_dict = {
    0.253: ((25 + (1 / 3)) / 100),
    0.233: ((23 + (1 / 3)) / 100),
    0.2: 0.2,
    0.17: 0.17,
    0.167: (1 / 6),
    0.13: 0.13,
    0.11: 0.11,
    0.1: 0.1,
    0.06: 0.06,
    0.04: 0.04,
    0.02: 0.02
}

relic_list = get_relic_list()


def get_drop_priority(relics, min_price=30, set_data=None):
    plat_list = []
    ducat_list = []
    if set_data is None:
        set_data = get_set_data()

    for relic in relics:
        for drop in relic_list[relic]['Intact']['drops']:
            if utility.get_set_price(drop, set_data) >= min_price:
                plat_list.append([drop, utility.get_price(drop)])
            else:
                ducat_list.append([drop, utility.get_ducats(drop)])

    drop_prioity = {k: v + 1 for v, k in enumerate([item[0] for item in
                                                    sorted(plat_list, key=lambda x: x[1], reverse=True)])}

    drop_prioity.update({k: v + 101 for v, k in enumerate([item[0] for item in
                                                           sorted(ducat_list, key=lambda x: x[1], reverse=True)])})

    return drop_prioity


def get_possible_rewards(relics, refinement):
    drops = []
    for relic in relics:
        drops.append(relic_list[relic][refinement]['drops'])

    return drops


def get_drop(reward_lists):
    random_num = random()

    reward_list = choice(reward_lists)

    chance = 0
    for i in reward_list:
        chance += (chance_dict[reward_list[i]['chance']])
        if random_num < chance:
            return [i, reward_list[i]['tier']]

    return ['Forma Blueprint', "Uncommon"]


def get_best_drop(drops, drop_order):
    drops = [drop[0] for drop in drops]

    drops.sort(key=lambda val: drop_order[val])

    return drops[0]


def get_reward_screen(relics):
    reward_screen = []
    for relic in relics:
        reward_screen.append(get_drop(relic))

    return reward_screen


def process_run(drops, offcycle_drops, style, drop_priority):
    if style == 'Solo':
        num_drops = 1
    else:
        num_drops = int(style[:1])

    if offcycle_drops:
        if style == "4b4":
            num_offcycle_drops = 4
        else:
            num_offcycle_drops = 4 - num_drops
    else:
        num_offcycle_drops = 0

    relics = []
    relics.extend(drops for _ in range(num_drops))
    relics.extend(offcycle_drops for _ in range(num_offcycle_drops))

    reward_screen = get_reward_screen(relics)
    best_drop = get_best_drop(reward_screen, drop_priority)

    return best_drop


def simulate_relic(relics, offcycle_relics, refinement, offcycle_refinement, style, amount, drop_priority):
    reward_list = []

    drops = get_possible_rewards(relics, refinement)
    offcycle_drops = get_possible_rewards(offcycle_relics, offcycle_refinement)

    reward_list.extend(
        process_run(drops, offcycle_drops, style, drop_priority) for _ in range(int(amount * num_runs_dict[style])))

    return reward_list

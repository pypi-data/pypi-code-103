from random import random, choice

from relic_engine import get_relic_list, get_set_data
import itertools

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

def get_set_name(item_name):
    if "Kavasa" not in item_name:
        return item_name.split("Prime", 1)[0] + "Prime"
    else:
        return "Kavasa Prime Kubrow Collar"


def get_set_price(item_name, set_data):
    if item_name != "Forma Blueprint":
        return set_data[get_set_name(item_name)]['plat']
    else:
        return 0


def get_price(item_name, set_data):
    if item_name != "Forma Blueprint":
        return set_data[get_set_name(item_name)]['parts'][item_name]['plat']
    else:
        return 0


def get_ducats(item_name, set_data):
    if item_name != "Forma Blueprint":
        return set_data[get_set_name(item_name)]['parts'][item_name]['ducats']
    else:
        return 0


def get_drop_priority(relics, min_price=30, set_data=None):
    plat_list = []
    ducat_list = []
    if set_data is None:
        set_data = get_set_data()

    for relic in relics:
        for drop in relic_list[relic]['Intact']['drops']:
            if get_set_price(drop, set_data) >= min_price:
                plat_list.append([drop, get_price(drop, set_data)])
            else:
                ducat_list.append([drop, get_ducats(drop, set_data)])

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
    drops.sort(key=lambda val: drop_order[val[0]])

    return drops[0][0], drops


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

    num_offcycle_drops = []
    if style != "4b4":
        if len(offcycle_drops) > 0:
            if len(offcycle_drops) == 1:
                num_offcycle_drops = [4 - num_drops]
            elif len(offcycle_drops) == 2:
                if style == "2b2":
                    num_offcycle_drops = [1,1]
                elif style == "1b1":
                    num_offcycle_drops = random.sample([1,2],2)
            elif len(offcycle_drops) == 3:
                if style == "2b2":
                    num_offcycle_drops = random.sample([0,1, 2], 3)
                elif style == "1b1":
                    num_offcycle_drops = [1,1,1]
            else:
                num_offcycle_drops = [4 - num_drops]
    elif style == "4b4" and len(offcycle_drops) == 1:
        num_offcycle_drops = [4]

    relics = []
    relics.extend(drops for _ in range(num_drops))
    for i in range(len(offcycle_drops)):
        relics.extend(offcycle_drops[i] for _ in range(num_offcycle_drops[i]))

    best_drop, reward_screen = get_best_drop(get_reward_screen(relics), drop_priority)

    return best_drop, reward_screen


def simulate_relic(relics, offcycle_relics, refinement, offcycle_refinement, style, amount, drop_priority):
    reward_list = []
    reward_screen = []
    offcycle_drops = []

    drops = get_possible_rewards(relics, refinement)

    for i in range(len(offcycle_relics)):
        offcycle_drops.append(get_possible_rewards(offcycle_relics[i], offcycle_refinement[i]))

    reward_list, reward_screen = zip(*[process_run(drops, offcycle_drops, style, drop_priority)
                                       for _ in itertools.repeat(None, int(amount * num_runs_dict[style]))])

    return list(reward_list), list(reward_screen)

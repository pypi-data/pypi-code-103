import json
import os
import pkgutil
import re
import time

import requests
from bs4 import BeautifulSoup


def get_wfcd_api():
    wfcd_api = requests.get(
        "https://raw.githubusercontent.com/WFCD/warframe-items/master/data/json/All.json").json()

    wfcd_api_parsed = {}

    for item in wfcd_api:
        wfcd_api_parsed[item['name']] = item
        if 'components' in wfcd_api_parsed[item['name']]:
            component_dict = {}
            for component in wfcd_api_parsed[item['name']]['components']:
                component_dict[component['name']] = component

            wfcd_api_parsed[item['name']]['components'] = component_dict

    return wfcd_api_parsed


def fix_name(item_name):
    if len(item_name.split()) > 3:
        if item_name.split(" ")[2] == "Systems" \
                or item_name.split(" ")[2] == "Chassis" \
                or item_name.split(" ")[2] == "Neuroptics" \
                or item_name.split(" ")[2] == "Harness" \
                or item_name.split(" ")[2] == "Wings":
            item_name = item_name.rsplit(' ', 1)[0]

    return item_name


# Get price information
def price_info(item_name):
    item_name = item_name.replace('&', "and")
    item_name = item_name.replace(' ', '_').lower()

    time.sleep(0.33)

    url = "https://api.warframe.market/v1/items/" + item_name + "/statistics"

    data = requests.get(url).json()['payload']
    if 'error' in data:
        price_data = 'N/A'
    else:
        if '90days' in data['statistics_closed']:
            price_data = int(data['statistics_closed']['90days'][-1]['avg_price'])
        elif '48hours' in data['statistics_closed']:
            price_data = int(data['statistics_closed']['48hours'][-1]['avg_price'])
        else:
            price_data = 'N/A'

    return price_data


# Get ducat information
def ducat_info(item_name, wfcd_api):
    set_name = get_set_name(item_name)
    part_name = get_part_name(item_name)

    try:
        ducat_data = wfcd_api[set_name]['components'][part_name]['primeSellingPrice']
    except KeyError:
        ducat_data = "N/A"
    return ducat_data


# Get vaulted status
def vaulted_info(item_name):
    url = "https://warframe.fandom.com/wiki/" + item_name

    html = requests.get(url)

    if "/wiki/Category:Vaulted" in html.text:
        vaulted_status = True
    elif "Baro Ki'Teer Offering" in html.text:
        vaulted_status = True
    else:
        vaulted_status = False

    return vaulted_status


# Get category info
def category_info(item_name, wfcd_api):
    try:
        category = wfcd_api[item_name]['category']
    except KeyError:
        category = "N/A"

    return category


# Get required item counts
def required_info(item_name, wfcd_api):
    set_name = item_name.split("Prime", 1)[0] + "Prime"
    part_name = item_name.split("Prime ", 1)[1]

    if set_name == "Kavasa Prime":
        part_name = set_name + " " + part_name
        set_name = set_name + " Kubrow Collar"
        if "Blueprint" in part_name:
            part_name = "Blueprint"

    try:
        required = wfcd_api[set_name]['components'][part_name]['itemCount']
    except KeyError:
        required = "N/A"

    return required


def get_relic_list(rebuild=False):
    if not rebuild:
        data = pkgutil.get_data(__name__, "relic_list.json")
        relic_list = json.loads(data)
        return relic_list
    else:
        url = 'https://n8k6e2y6.ssl.hwcdn.net/repos/hnfvc0o3jnfvc873njb03enrf56.html'

        source = requests.get(url).text

        soup = BeautifulSoup(source, 'lxml')

        tables = soup.find_all('tr',
                               string=re.compile("Relic .Intact|Relic .Exceptional|Relic .Flawless|Relic .Radiant"))

        relic_list = {}

        for table in tables:
            items = table.find_all_next("tr", limit=6)

            relic = table.find("th").contents[0].split("Relic")[0].rstrip()
            refinement = table.find("th").contents[0].split("(")[1][0:-1].rstrip()

            x = {'drops': {}}
            for item in items:
                item_contents = item.find_all("td")

                item_name = item_contents[0].contents[0]
                item_chance = round(float(item_contents[1].contents[0].split("(")[1][0:-2]) / 100, 3)

                if refinement == "Intact":
                    if item_chance == 0.253:
                        tier = "Common"
                        tier_id = 0
                    elif item_chance == 0.11:
                        tier = "Uncommon"
                        tier_id = 1
                    elif item_chance == 0.02:
                        tier = "Rare"
                        tier_id = 2
                elif refinement == "Exceptional":
                    if item_chance == 0.233:
                        tier = "Common"
                        tier_id = 0
                    elif item_chance == 0.13:
                        tier = "Uncommon"
                        tier_id = 1
                    elif item_chance == 0.04:
                        tier = "Rare"
                        tier_id = 2
                elif refinement == "Flawless":
                    if item_chance == 0.2:
                        tier = "Common"
                        tier_id = 0
                    elif item_chance == 0.17:
                        tier = "Uncommon"
                        tier_id = 1
                    elif item_chance == 0.06:
                        tier = "Rare"
                        tier_id = 2
                elif refinement == "Radiant":
                    if item_chance == 0.167:
                        tier = "Common"
                        tier_id = 0
                    elif item_chance == 0.2:
                        tier = "Uncommon"
                        tier_id = 1
                    elif item_chance == 0.1:
                        tier = "Rare"
                        tier_id = 2

                x['drops'][item_name] = {'chance': item_chance, 'tier': tier, 'tier_id': tier_id}

            relic_drops = dict(sorted(x.items(), key=lambda x: x[1]))

            if relic not in relic_list:
                relic_list[relic] = {}

            relic_list[relic][refinement] = relic_drops

            vaulted = vaulted_info(relic.replace(" ", "_"))
            relic_list[relic][refinement]['vaulted'] = vaulted

        for i in range(0, 5):
            relic_list.popitem()

        return relic_list


PAlist = {
    "prime access": {
        "Ash": "Carrier,Vectis",
        "Atlas": "Dethcube,Tekko",
        "Banshee": "Euphona,Helios",
        "Chroma": "Gram,Rubico",
        "Ember": "Sicarus,Glaive",
        "Equinox": "Stradavar,Tipedo",
        "Frost": "Latron,Reaper",
        "Gara": "Astilla, Volnus",
        "Hydroid": "Ballistica,Nami Skyla",
        "Inaros": "Karyst,Panthera",
        "Ivara": "Baza,Aksomati",
        "Limbo": "Destreza,Pyrana",
        "Loki": "Bo,Wyrm",
        "Mag": "Boar,Dakra",
        "Mesa": "Akjagara,Redeemer",
        "Mirage": "Akbolto,Kogake",
        "Nekros": "Galatine,Tigris",
        "Nezha": "Guandao,Zakti",
        "Nova": "Soma,Vasto",
        "Nyx": "Hikou,Scindo",
        "Oberon": "Sybaris,Silva & Aegis",
        "Octavia": "Pandero,Tenora",
        "Rhino": "Ankyros,Boltor",
        "Saryn": "Nikana,Spira",
        "Titania": "Corinth,Pangolin",
        "Trinity": "Kavasa,Dual Kamas",
        "Valkyr": "Cernos,Venka",
        "Vauban": "Akstiletto,Fragor",
        "Volt": "Odonata",
        "Wukong": "Ninkondi,Zhuge",
        "Zephyr": "Kronen,Tiberon"
    }
}


def access_info(set):
    PA = "N/A"
    if set.split("Prime")[0].rstrip() in PAlist['prime access']:
        PA = set.split("Prime")[0].rstrip()
    else:
        for frame in PAlist['prime access']:
            if set.split("Prime")[0].rstrip() in PAlist['prime access'][frame].split(","):
                PA = frame
    return PA


def get_set_data(rebuild=False):
    if not rebuild:
        data = pkgutil.get_data(__name__, "set_data.json")
        set_data = json.loads(data)
        return set_data
    else:
        # List of prime parts
        part_list = []

        # List of prime sets
        set_list = []

        relic_list = get_relic_list(True)
        wfcd_api = get_wfcd_api()

        for relic in relic_list:
            for reward in relic_list[relic]['Intact']['drops']:
                set_name = reward.split("Prime", 1)[0] + "Prime"

                if reward != "Forma Blueprint":
                    if reward not in part_list:
                        part_list.append(reward)

                    if [set_name] not in set_list and set_name != "Kavasa Prime":
                        set_list.append([set_name])

        set_list.append(["Kavasa Prime Kubrow Collar"])

        # Sorts part_list and set_list alphabetically
        part_list = sorted(part_list)
        set_list.sort(key=lambda x: x[0])

        set_data = {}

        for i in range(len(set_list)):
            for j in range(len(part_list)):
                if set_list[i][0].split()[0] == part_list[j].split()[0]:
                    set_list[i].append(part_list[j])

        for i in range(len(set_list)):
            parts = {'parts': {}}
            for j in range(len(set_list[i]) - 1):
                parts['parts'][set_list[i][j + 1]] = {'plat': price_info(fix_name(set_list[i][j + 1])),
                                                      'ducats': ducat_info(fix_name(set_list[i][j + 1]), wfcd_api),
                                                      'required': required_info(fix_name(set_list[i][j + 1]), wfcd_api)}

            set_data[set_list[i][0]] = parts
            set_data[set_list[i][0]]['vaulted'] = vaulted_info(set_list[i][0].split("Prime", 1)[0].rstrip() + "_Prime")
            set_data[set_list[i][0]]['type'] = category_info(set_list[i][0], wfcd_api)
            set_data[set_list[i][0]]['plat'] = price_info(set_list[i][0] + "_set")
            set_data[set_list[i][0]]['prime-access'] = access_info(set_list[i][0])

        return set_data


def get_set_name(item_name):
    if "Kavasa" not in item_name:
        return item_name.split("Prime", 1)[0] + "Prime"
    else:
        return "Kavasa Prime Kubrow Collar"


def get_part_name(item_name):
    if "Kavasa" not in item_name:
        return item_name.split(" Prime ", 1)[1]
    elif "Blueprint" in item_name:
        return "Blueprint"
    else:
        return item_name


def calculate_average(relic, style, modifier, drops):
    chance_left = 1
    chance_used = 1
    average_return = 0

    relic_rewards = []

    for drop in relic['drops']:
        relic_rewards.append([drop, relic['drops'][drop]['price']])

    relic_rewards.sort(key=lambda x: x[1], reverse=True)

    for i in range(len(relic_rewards)):
        item_name = relic_rewards[i][0]

        chance = relic['drops'][item_name]['chance']
        price = relic['drops'][item_name]['price']

        adj_chance = 1 - (chance / chance_left)

        actual_chance = adj_chance ** modifier

        item_chance = 1 - actual_chance

        item_chance = chance_used * item_chance

        chance_left = chance_left - chance

        chance_used = chance_used * actual_chance

        adj_price = price * item_chance

        relic['drops'][item_name]['calculated_chance'][style] = item_chance * drops

        relic['drops'][item_name]['calculated_price'][style] = adj_price * drops

        average_return += adj_price * drops

    relic['average_return'][style] = round(average_return, 0)

    return relic


def get_average_return(relic):
    solo = 0
    for drop in relic['drops']:
        solo += relic['drops'][drop]['price'] * relic['drops'][drop]['chance']

    solo = solo
    one_by_one = solo * 4

    relic['average_return']['solo'] = round(solo, 0)
    relic['average_return']['1b1'] = round(one_by_one, 0)

    relic = calculate_average(relic, "2b2", 2, 2)
    relic = calculate_average(relic, "3b3", 3, (4 / 3))
    relic = calculate_average(relic, "4b4", 4, 1)

    return relic


def update_relic_data(relic_data, set_data):
    for relic in relic_data:
        for refinement in relic_data[relic]:
            for part in relic_data[relic][refinement]['drops']:
                if "Forma" not in part:
                    relic_data[relic][refinement]['drops'][part]['price'] = \
                        set_data[get_set_name(part)]['parts'][part]['plat']

                    relic_data[relic][refinement]['drops'][part]['ducats'] = \
                        set_data[get_set_name(part)]['parts'][part]['ducats']
                else:
                    relic_data[relic][refinement]['drops'][part]['price'] = 0
                    relic_data[relic][refinement]['drops'][part]['ducats'] = 0

                relic_data[relic][refinement]['drops'][part]['calculated_chance'] = \
                    {"solo": relic_data[relic][refinement]['drops'][part]['chance'],
                     "1b1": relic_data[relic][refinement]['drops'][part]['chance'] * 4}

                relic_data[relic][refinement]['drops'][part]['calculated_price'] = \
                    {"solo": relic_data[relic][refinement]['drops'][part]['price'] *
                             relic_data[relic][refinement]['drops'][part]['chance'],
                     "1b1": relic_data[relic][refinement]['drops'][part]['price'] *
                            relic_data[relic][refinement]['drops'][part]['chance'] * 4}
            relic_data[relic][refinement]['average_return'] = {}
            relic_data[relic][refinement] = get_average_return(relic_data[relic][refinement])

    return relic_data


def get_relic_data(rebuild=False):
    if not rebuild:
        data = pkgutil.get_data(__name__, "relic_data.json")
        relic_data = json.loads(data)
        return relic_data
    else:
        relic_data = get_relic_list(True)
        set_data = get_set_data(True)
        relic_data = update_relic_data(relic_data, set_data)

    return relic_data


def update_prices_and_averages(set_data, relic_data):
    for prime_set in set_data:
        set_data[prime_set]['plat'] = price_info(prime_set + "_set")

        for part in set_data[prime_set]['parts']:
            set_data[prime_set]['parts'][part]['plat'] = price_info(fix_name(part))

    relic_data = update_relic_data(relic_data, set_data)

    return set_data, relic_data

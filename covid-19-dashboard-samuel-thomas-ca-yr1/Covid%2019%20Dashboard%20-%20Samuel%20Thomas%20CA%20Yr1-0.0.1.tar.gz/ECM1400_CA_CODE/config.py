"""[This is a function that handles the config file ie read/write commands ]
"""
import json
config_json = open('config.json', 'r', encoding='UTF-8')
contents = json.load(config_json)
key = contents["Profile"]['Key']
headlines = contents["Profile"]['News']
schedule_config = contents['Profile']['Schedules']
location = contents['Profile']['Location']


def schedule_update_remove(update_name: str) -> None:
    """[This function will remove a schedule from the config file]

    Args:
        update_name (str): [schedules title]
    """
    for sched in schedule_config:
        if sched['title'] == update_name:
            schedule_config.remove(sched)
            break
    write_json(contents)


def write_json(data: dict) -> None:
    """[a function that dumps data in the config file]

    Args:
        data (dict): [the new config files data]
    """    ''''''
    with open('config.json', 'w', encoding='UTF-8') as file:
        json.dump(data, file, indent=2)

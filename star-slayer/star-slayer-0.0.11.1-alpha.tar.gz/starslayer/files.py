"""
Files Module. It reads (and writes) in files to define persistent
variables in the behaviour of the game.
"""

import pkgutil

from .consts import KEYS_PATH, LEVEL_PATH, PROFILES_PATH

StrDict = dict[str, str]
ProfilesDict = dict[str, StrDict]
LevelList = list[str | int]
LevelDict = dict[str, int | LevelList]

def map_keys(file_name: str=KEYS_PATH) -> StrDict:
    """
    Opens 'file_name' and creates a dictionary where every key is assigned
    to an action.
    """

    keys_dict = dict()

    with open(file_name) as file:

        for line in file:

            if line == '\n':
                continue

            keys, action = ''.join(line.split('=')).split()

            for key in keys.split(','):

                keys_dict[key] = action

    return keys_dict

def list_actions(keys_dict: StrDict=map_keys()) -> list[str]:
    """
    Returns a list of all the actions in the keys file, without repetitions.
    """

    actions_list = list()

    for action in keys_dict.values():

        if not action in actions_list:

            actions_list.append(action)

    return actions_list

def list_repeated_keys(value: str, keys_dict: StrDict=map_keys()) -> list[str]:
    """
    Given a value to search for and a dictionary (by default the one that 'map_keys' returns),
    it returns a list of all the keys that have such value.
    """

    return [key for (key, val) in keys_dict.items() if val == value]

def map_profiles(file_name: str=PROFILES_PATH) -> ProfilesDict:
    """
    Opens 'file_name' and creates a dictionary where every key is assigned
    to a dictionary filled with color values.
    """

    profiles_dict = dict()
    current_name = ''

    with open(file_name) as file:

        for line in file:

            if line == '\n' or line[0] == '#': # is a comment

                continue

            type, key, *value = ''.join(line.split('=')).split()

            if type == "!t": # is a new Profile

                profiles_dict[key] = dict()
                current_name = key

            elif type == "!v": # is a 'key-value' pair

                value = ''.join(value)
                profiles_dict[current_name][key] = (value if not value == '/' else '')

    return profiles_dict

def map_level(game_level: int) -> LevelDict:
    """
    Defines a dictionary with all the variables a level should have.
    """

    level_dict = dict()
    current_time = -1

    with open(LEVEL_PATH.format(level=game_level)) as file:

        for line in file:

            if line == '\n' or not line.split():

                continue
            
            if line.lstrip()[:2] == '#t':

                _, time = line.split()
                level_dict['total_time'] = int(time)

            elif line.lstrip()[:2] == '#l':

                _, current_time = line.split()
                level_dict[current_time] = list()

            elif line.lstrip()[:2] == '#s':

                ship_dict = dict()
                attributes = line.split('#s')[1].split()

                for attribute in attributes:

                    atr, val = attribute.split('-')
                    ship_dict[atr] = (None if val == '/' else (val if not val.isnumeric() else int(val)))
                
                level_dict[current_time].append(ship_dict)

    return level_dict

def print_profiles(profiles_dict: ProfilesDict, file_name: str="test.txt") -> None:
    """
    Opens 'file_name' and, if existent, edits within the information of the dictionary
    of the keys. If not, it creates one instead.
    """

    pass

def print_keys(keys_dict: StrDict, file_name: str=KEYS_PATH) -> None:
    """
    Opens 'file_name' and, if existent, edits within the information of the dictionary
    of the keys. If not, it creates one instead.
    """

    with open(file_name, mode='w') as f:

        dict_values = list_actions(keys_dict)

        for value in dict_values:

            if not value == dict_values[0]:

                f.write("\n\n")

            repeated_keys = list_repeated_keys(value, keys_dict)

            if len(repeated_keys) > 1 and '/' in repeated_keys:

                repeated_keys.remove('/')

            f.write(f"{','.join(repeated_keys)} = {value}")

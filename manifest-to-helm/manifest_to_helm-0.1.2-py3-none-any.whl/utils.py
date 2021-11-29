import copy

def get_from_key_list(data, keys):
    is_dict = not (keys[0][0] == '[' and keys[0][-1] == ']')
    if data == None:
        return None
    if is_dict:
        if len(keys) > 1:
            if type(data) != dict:
                return None

            # if the key doesn't exist then return None
            if not keys[0] in data.keys():
                return None
            # if we aren't at the last key then go a level deeper
            return get_from_key_list(data[keys[0]], keys[1:])
        else:
            if type(data) != dict:
                return None
            # if the key doesn't exist then return None
            if not keys[0] in data.keys():
                return None
            # return the value we want
            return data[keys[0]]
    else:
        index = int(keys[0][1:-1])
        if len(keys) > 1:
            if type(data) != list:
                return None

            # if the index is out of range then return None
            if index > len(data):
                return None
            # if we aren't at the last key then go a level deeper
            return get_from_key_list(data[index], keys[1:])
        else:
            if type(data) != list:
                return None
            # if the index is out of range then return None
            if index > len(data):
                return None
            # return the value we want
            return data[index]

def set_from_key_list(data, keys, value):
    is_dict = not (keys[0][0] == '[' and keys[0][-1] == ']')
    if is_dict:
        if data == None:
            data = {}
        if type(data) != dict:
            return None
    else:
        if data == None:
            data = []
        if type(data) != list:
            return None

    if is_dict:
        if not keys[0] in data.keys():
            if len(keys) == 1:
                data[keys[0]] = copy.deepcopy(value)
                return data
            else:
                if keys[1][0] == '[' and keys[1][-1] == ']':
                    data[keys[0]] = []
                else:
                    data[keys[0]] = {}
        if len(keys) > 1:
            # if we aren't at the last key then go a level deeper
            ret = copy.deepcopy(set_from_key_list(data[keys[0]], keys[1:], value))
            if ret == None:
                return None
            else:
                data[keys[0]] = ret
        else:
            # return the value we want
            data[keys[0]] = value
        return data
    else:
        index = int(keys[0][1:-1])
        if len(keys) == 1:
            while len(data) < index + 1:
                data.append(None)
            data[index] = copy.deepcopy(value)
            return data
        if len(data) < index + 1:
            while len(data) < index + 1:
                data.append(None)
            if keys[1][0] == '[' and keys[1][-1] == ']':
                data[index] = []
            else:
                data[index] = {}
        if len(keys) > 1:
            # if we aren't at the last key then go a level deeper
            ret = copy.deepcopy(set_from_key_list(data[index], keys[1:], value))
            if ret == None:
                return None
            else:
                while len(data) < index + 1:
                    data.append(None)
                data[index] = ret
        else:
            while len(data) < index + 1:
                data.append(None)
            # set the value we want
            data[index] = value
        return data
# Techman's python3 function Library
import sys
import os
VERSION = 1.13


def is_compatible(min_ver):  # checks if this version of Library is >= to min_ver param
    return VERSION >= min_ver


# ask => Takes in a prompt, asks for input, and returns True for "yes" and False for "no" based on response (Syntax: ask('Yes or no? '))
def ask(prompt, yes_list=["yes", "y", '1'], no_list=['no', 'n', '0']):
    response = input(prompt).lower()
    if response in yes_list:
        return True
    elif response in no_list:
        return False
    else:
        print('Invalid Option, use {yes} or {no}\n'.format(
            yes=yes_list[0], no=no_list[0]))
        return ask(prompt, yes_list, no_list)

# check => Takes in a string and returns True for "yes" and False for "no" based on string, also returns None for invalid option (Syntax: ask('yes'))


def check(string, yes_list=["yes", "y", '1'], no_list=['no', 'y', '0']):
    string = string.lower()
    if string in yes_list:
        return True
    elif string in no_list:
        return False
    else:
        return None


DEFAULTS = {
    'path': '{}'.format(os.path.dirname(sys.argv[0]))
}


def is_first_open(name, **params):
    if params.get('message') is None:
        params['message'] = None
    if params.get('path') is None:
        params['path'] = DEFAULTS['path']

    try:
        open("{}/.{}.cashe".format(params['path'], name), "r").close()
        return False
    except FileNotFoundError:
        if params['message'] != None:
            print(params['message'])
        with open("{}/.{}.cashe".format(params['path'], name), "w") as cashe:
            cashe.write("first_open was completed")
        return True


def reset_first_open(name, **params):
    if params.get('path') is None:
        params['path'] = DEFAULTS['path']

    import os
    try:
        os.remove("{}/.{}.cashe".format(params['path'], name))
        return True
    except FileNotFoundError:
        return False


def does_config_exist(name, **params):
    if params.get('path') == None:
        params['path'] = DEFAULTS['path']
    if params.get('key_to_check') == None:
        params['key_to_check'] = None

    import json
    try:
        with open("{}/.{}.config".format(params['path'], name), 'r') as file:
            config = json.loads(file.read().replace('\'', '\"'))
            if params['key_to_check'] != None:
                if config.get(params['key_to_check']) == None:
                    print('[ERROR]: Corrupt config file'.format(
                        key=params['key_to_check']))
                    return False
            return True
    except FileNotFoundError:
        return False
    except json.decoder.JSONDecodeError:
        print('[ERROR]: JSON Decode Error')
        return False


def write_config(name, config, **params):
    if params.get('path') is None:
        params['path'] = DEFAULTS['path']

    import json
    try:
        with open("{}/.{}.config".format(params['path'], name), 'w') as file:
            file.write(str(config).replace('\'', '\"').replace(
                'True', 'true').replace('False', 'false'))
            return config
    except:
        return None


def read_config(name, **params):
    if params.get('path') is None:
        params['path'] = DEFAULTS['path']

    import json
    if does_config_exist(name, path=params['path']):
        with open("{}/.{}.config".format(params['path'], name), 'r') as file:
            return json.loads(file.read().replace('\'', '\"'))
    else:
        return None


def update_config(name, new_values, **params):
    if params.get('path') is None:
        params['path'] = DEFAULTS['path']

    if does_config_exist(name, path=params['path']):
        config = read_config(name, path=params['path'])
    else:
        config = {}
    config.update(new_values)
    return write_config(name, config, path=params['path'])


def reset_config(name, **params):
    if params.get('path') is None:
        params['path'] = DEFAULTS['path']

    import os
    try:
        os.remove("{}/.{}.config".format(params['path'], name))
        return True
    except FileNotFoundError:
        return False


def set_clipboard(value, *args):
    try:
        import clipboard
        module = 'clipboard'
    except ModuleNotFoundError:
        try:
            import pyperclip
            module = 'pyperclip'
        except ModuleNotFoundError:
            if install('pyperclip') == False:
                module = None
                return False
            else:
                module = 'pyperclip'
                import pyperclip
    if module == 'clipboard':
        clipboard.set(value)
        return True
    elif module is not None:
        pyperclip.copy(value)
        return True


def is_package_installed(module):
        import sys
        import importlib.util
        if module in sys.modules:
            return True
        elif importlib.util.find_spec(module) is not None:
            return True
        else:
            return False

def install(module, **params):
        import subprocess
        import sys
        if not is_package_installed(module):
            try:
                if params.get('pip_v') is not None:
                    subprocess.check_call([params['pip_v'], "install", module])
                else:
                    try:
                        subprocess.check_call(
                            [sys.executable, "-m", "pip", "install", module])
                    except:
                        try:
                            subprocess.check_call(["pip3", "install", module])
                        except:
                            subprocess.check_call(["pip", "install", module])
            except:
                print('Failed to install dependency "{m}", please install it manually with "pip3 install {m}"'.format(
                    m=module))
                return False
            finally:
                return True
        else:
            return True
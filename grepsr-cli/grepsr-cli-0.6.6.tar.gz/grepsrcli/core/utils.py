import json
from pathlib import Path
from os import listdir, path, mkdir
import re
from jinja2 import Template
from .config import load_config
from terminaltables import SingleTable
from .message_log import Log


def get_plugin_path(plugin_name, type='php', all_types=False):
    """ returns the path of the plugin if plugin name exist

    Args:
        plugin_name (str): name of the service plugin .
        type (str, optional): php|py|node. Defaults to 'php'.
        all_types: retuns the path regardless the plugin types i.e php, py and node
    """
    config = load_config('config.yml')
    if all_types == False:
        if type == 'php':
            if _generate_plugin_path(plugin_name, config['php']['paths']):
                return _generate_plugin_path(plugin_name, config['php']['paths'])
            else:
                return False
        elif type == 'node':
            if _generate_plugin_path(plugin_name, config['node']['paths']):
                return _generate_plugin_path(plugin_name, config['node']['paths'])
            else:
                return False
        elif type == 'py':
            if _generate_plugin_path(plugin_name, config['python']['paths']):
                return _generate_plugin_path(plugin_name, config['python']['paths'])
            else:
                return False
        elif type == 'php_next':
            if _generate_plugin_path(plugin_name, config['php_next']['paths']):
                return _generate_plugin_path(plugin_name, config['php_next']['paths'])
            else:
                return False
        else:
            Log.error("Invalid params for type.")
            return False
    else:
        # todo: do not hardcode this
        base_paths_list = [
            config['php']['paths'] if 'php' in config else None,
            config['node']['paths'] if 'node' in config else None,
            config['python']['paths'] if 'python' in config else None,
            config['php_next']['paths'] if 'php_next' in config else None
        ]

        for base_paths in base_paths_list:
            if base_paths is not None and _generate_plugin_path(plugin_name, base_paths):
                return _generate_plugin_path(plugin_name, base_paths)
        Log.error("Plugin name not found.")
        return False


def create_boilerplate(folder_path, boilerplate, data, extention,):
    """ to create boilerplate for a given path

    Args:
        folder_path (str): the destination path
        boilerplate (str): the name of the boilerplate
        data (dict): the data to be rendered
    """

    service_name = path.basename(folder_path)
    try:
        mkdir(folder_path)
    except OSError as err:
        Log.error(err)
        return

    dest_path = '{}/{}.{}'.format(
                folder_path, service_name, extention)

    render_boilerplate(boilerplate=boilerplate, data=data,
                       destination_path=dest_path)

    Log.info(
        'Plugin created at {}'.format(dest_path))


def show_schema(base_path):
    """ this method will show the schema of a plugin if it has schema.json

    Args:
        base_path (str): the base path of the plugin  eg: /home/vtx-services/aaa_com/
    """

    schema_path = base_path + '/schema.json'
    if path.exists(schema_path):
        try:
            with open(schema_path, 'r') as f:
                schema = f.read()
                schema = json.loads(schema)
                for page in schema.keys():
                    Log.standout(f"Schema for Page: {page}")
                    schema_heading = ['field', 'type', 'pattern']
                    table_data = [
                        schema_heading
                    ]

                    for th, td in schema[page]['schema']['properties'].items():
                        if 'pattern' in td:
                            row = [th, td['type'], td['pattern']]
                        else:
                            row = [th, td['type'], '']

                        table_data.append(row)

                    print(SingleTable(table_data).table)
                return True
        except:
            Log.warn("Schema Structured Incorrectly")
    else:
        Log.warn("Schema Not Found")
        return False


def get_plugin_info(plugin_path):
    """ get plugin's info like service_name,pid,description from the plugin's base folder.
    It does so by reading the file and looking at the info from plugin which is commented
    at the beginning.

    Args:
        plugin_path (str): the path of the directory where we find the plugin.
    """
    plugin_file_path = listdir(plugin_path)

    files = [f for f in plugin_file_path]
    plugin_file = ''
    for file in files:
        if path.basename(plugin_path) in file:
            plugin_file = file
            break

    if plugin_file:
        try:
            with open(f'{plugin_path}/{plugin_file}') as f:
                script = f.read()

                pid = re.search(r'pid\s*\:\s*([0-9]+)', script, re.IGNORECASE)
                pid = pid[1]

                report_name = re.search(
                    r'name\s*\:\s*(.*)', script, re.IGNORECASE)
                report_name = report_name[1]

                desc = re.search(r'description\s*\:\s*(.*)',
                                 script, re.IGNORECASE)
                desc = desc[1]

                return {
                    'pid': pid,
                    'report_name': report_name,
                    'desc': desc
                }
        except:
            pass


def render_boilerplate(boilerplate, data, destination_path):
    """parse boilerplate from template directory to start a project

    Args:
        boilerplate (str): name of boilerplate template
        data (dict): input for the boilerplate
        destination_path: the final path where the final content needs to be saved
    """

    template_dir = Path(__file__).parent.parent.absolute()
    template_file = '{}/templates/{}'.format(template_dir, boilerplate)
    with open(template_file) as file:
        template = Template(file.read())
        with open(destination_path, 'w') as dest_file:
            dest_file.write(template.render(data))


def _generate_plugin_path(plugin_name, paths):

    for service_path in paths:
        plugin_path = f'{service_path}/{plugin_name}'
        plugin_path = path.expanduser(plugin_path)
        if(path.exists(plugin_path)):
            return plugin_path
    return False
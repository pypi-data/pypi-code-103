"""
Модуль для работы с конфигурацией из командной строки
"""
from sys import argv
from os import getenv
from os.path import exists as path_exists, isfile
from json import dumps as json_dump, loads as json_load
import argparse
from config import __version__

new_element = None
root_template = None

# TODO: добавить типы переменных


def __dump_json__(file_path, json):
    with open(file_path, 'w') as file:
        file.write(json_dump(json, indent=4))


def __wait_confirmation__(message: str) -> bool:
    print(message)
    answer = input()
    if answer.lower() != "yes" and answer.lower() != 'y':
        return False
    return True


def __parse_element__(element, name_parent_element, parent_element):
    global new_element
    global root_template
    if element.get('$ref'):
        path_element = element['$ref'].split('/')
        for i in path_element:
            match i:
                case "#":
                    element = root_template
                case _:
                    element = element[i]
        __parse_element__(element, name_parent_element, parent_element)
    else:
        if element['type'] == 'object':
            parent_element[name_parent_element] = {}
            parent_element = parent_element[name_parent_element]
            for i in element['required']:
                __parse_element__(element['properties'][i], i, parent_element)
        else:
            parent_element[name_parent_element] = element.get('default')


def __update_add_command__(**kwargs):
    params = kwargs['params']
    template = kwargs['template']
    with open(params.config_file, 'r') as config_file:
        config = json_load(config_file.read())
    for i in params.elements:
        if i not in template['properties']:
            print(f'Элемента {i} нет в шаблоне')
            return
        if i in config.keys() and __wait_confirmation__(f'{i} элемент уже есть в конфигурации, перезаписать (y/n)'):
            continue
        global new_element
        new_element = {}
        __parse_element__(template['properties'][i], i, new_element)
        config[i] = new_element[i]

    __dump_json__(params.config_file, config)
    print(f"{'Элемент добавлен' if len(params.elements) == 1 else 'Элементы добавлены'}")


def __update_delete_command__(**kwargs):
    params = kwargs['params']
    with open(params.config_file, 'r') as config_file:
        config = json_load(config_file.read())

    for i in params.elements:
        if i in config.keys():
            del config[i]
            print(f"{i} элемент удален")
        else:
            print(f"{i} элемент отсутсвует в конфиге")

    __dump_json__(params.config_file, config)

    print('Удаление выполнено')


def create_command(params):
    """
    Команда создания конфига из шаблона
    """
    # TODO: сделать чтение конфига лога из шаблона
    if not getenv('TEMPLATE_CONFIG', default=None):
        print("Не определена переменная окружения TEMPLATE_CONFIG")
        return
    template = json_load(open(getenv("TEMPLATE_CONFIG")).read())

    if params.list_elements:
        message = "Список доступных элементов: "
        for i in template['properties']:
            message += f"{i}, "
        print(message[:-2])
        return
    if path_exists(params.config_file) and \
            not __wait_confirmation__('Файл конфигурации уже существует, перезаписать его? (y/n)'):
        return
    if params.elements:
        elements = params.elements
        elements.append('logging')
    else:
        elements = ['logging']
    config = {}
    global root_template
    root_template = template

    for i in elements:
        if i not in template['properties']:
            print(f'Элемента {i} нет в шаблоне')
            return
        global new_element
        new_element = {}
        __parse_element__(template['properties'][i], i, new_element)
        config[i] = new_element[i]

    __dump_json__(params.config_file, config)
    print('Конфигурация создана')


def update_command(params):
    """
    Команда обновления конфига
    """
    if not getenv('TEMPLATE_CONFIG', default=None):
        print("Не определена переменная окружения TEMPLATE_CONFIG")
        return
    if not path_exists(params.config_file) and not isfile(params.config_file):
        print("Указанного файла не существует")
        return

    template = json_load(open(getenv("TEMPLATE_CONFIG")).read())
    update_methods = {
        "add": __update_add_command__,
        "delete": __update_delete_command__
    }
    update_methods[params.update_command](params=params, template=template)


methods = {
    "create": create_command,
    "update": update_command
}


def create_parse():
    """
    Команда создания парсинга аргументов
    """
    parser = argparse.ArgumentParser(add_help=False)

    parent_group = parser.add_argument_group(title="Параметры")
    parent_group.add_argument('--version', action='version', help='Вывести номер версии',
                              version='%(prog)s {}'.format(__version__))
    parent_group.add_argument("--help", "-h", action="help", help="Справка")

    subparsers = parser.add_subparsers(dest="command", title="Возможные команды",
                                       description="Команды, которые должны быть в качестве первого параметра %(prog)s")

    create_command_parser = subparsers.add_parser("create", add_help=False)
    create_command_parser.add_argument('config_file')
    create_command_parser.add_argument('-e', '--elements', nargs='+', help="Элементы, которые нужно добавить в конфиг. "
                                                                           "Для работы этого параметра требуется "
                                                                           "указать переменную окружения "
                                                                           "TEMPLATE_CONFIG")
    create_command_parser.add_argument('--list-elements', action='store_true', default=False)
    create_command_parser.add_argument('-h', '--help', action='help', help='Справка')

    update_command_parser = subparsers.add_parser('update', add_help=False)
    update_command_parser.add_argument('config_file')
    update_command_parser.add_argument('update_command', choices=['add', 'delete'])
    update_command_parser.add_argument('elements', nargs='+')
    update_command_parser.add_argument('-h', '--help', action='help', help='Справка')

    return parser


if __name__ == '__main__':
    main_parser = create_parse()
    parsed_params = main_parser.parse_args(argv[1:])

    methods[parsed_params.command](parsed_params)

# coding=utf-8

class DefinedCmd:
    HELP_CMD_SAMPLE = 'Print sample input of template files'
    HELP_CMD_BLOC = 'Create template files for a BLoC'
    HELP_CMD_MODEL = 'Create a model file from a JSON format'
    HELP_CMD_NETWORK = 'Create a Restful API service'
    HELP_CMD_UI = 'Generate Flutter component from Figma design link'

    class Argument:
        HELP_EXTENSION = 'extension of sample file'
        HELP_NAME_MODEL = 'object name of the JSON file'
        HELP_APPEND_FILE = 'append to the existed file'
        HELP_UI_COMPONENT = 'type of UI component we want to generate'

        @staticmethod
        def help_source(target: str):
            return f'source for {target}, support [pasteboard] ' \
                   'or [file path], default is [pasteboard]'

        @staticmethod
        def help_path(target: str):
            return f'path to the {target} file'

    class Required:
        INPUT_FILE = '[file] argument is required in file input option'


SUPPORTED_SOURCES = [
    'pb',
    'file'
]

POSTMAN_SOURCE = 'postman'

SUPPORTED_TEMPLATES = [
    'bloc',
    'model',
    'network',
    'ui'
]

SUPPORTED_SOURCE_FORMAT = [
    'json',
    'yaml'
]

SUPPORTED_UI_COMPONENT = [
    'string',
    'color',
    'image',
    'font',
    'widget',
    'enum',
    'translate'
]

DATE_REGEX = r'(\d{4})[-/](\d{2})[-/](\d{2})'

PYTHON_TO_DART_TYPES = {
    'int': 'num',
    'float': 'num',
    'bool': 'bool',
    'str': 'String',
    'NoneType': 'dynamic',
    'None': 'dynamic'
}

DART_TYPES_DEFAULT_VALUES = {
    'int': '0',
    'double': '0.0',
    'num': '0',
    'bool': 'false',
    'String': '',
    'DateTime?': 'null',
    'dynamic': 'null',
}

DART_TYPES_MOCK_VALUES = {
    'Int': '1',
    'Bool': 'true',
    'Double': '1.0',
    'String': '"foobar"',
    'Date': 'DateTime()',
    'dynamic': 'null',
}

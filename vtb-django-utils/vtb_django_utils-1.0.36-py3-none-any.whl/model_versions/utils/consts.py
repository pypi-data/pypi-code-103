import re

START_VERSION = '1.0.0'
VERSION_DELIMITER = '.'
VERSION_REGEX = re.compile(r'(\d)+.(\d)+.(\d)+')
VERSION_PATTERN_REGEX = re.compile(r'^([\d]+\.){1,2}$')

RE_VERSION = re.compile(r'^[\d]+.[\d]+.[\d]+$')

# messages
THERE_IS_NO_VERSION_DATA = 'There is no data for this version'
DOES_NOT_EXIST_VERSION = 'Version {0} does not exist'

# поля в БД
REL_VERSION_FIELD_END = '_version'
REL_VERSION_PATTERN_FIELD_END = '_version_pattern'
REL_VERSION_CALCULATED_FIELD_END = '_version_calculated'

# суффикс модели с версиями
VERSION_MODEL_SUFFIX = 'Version'

# сообщения об ошибках
ERR_VERSIONED_OBJ_NOT_SELECTED = "You must select {0} to select it's version"
ERR_VERSIONED_OBJ_DONT_MATCH_SELECTED_VERSION = 'Selected version {0} cannot be used with {1} {2}'
ERR_SELECTED_VERSION_AND_PATTERN = "You can\'t use both {0} version and version pattern at same time"
ERR_WRONG_VERSION_FORMAT = 'You must specify version in pattern like "{num}.{num}.{num}"'
ERR_WRONG_VERSION_PATTERN_FORMAT = 'You must specify version in pattern like "{num}. | {num}.{num}."'

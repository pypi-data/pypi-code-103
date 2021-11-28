# main.py
# (C) 2020 Masato Kokubo
from abc import abstractmethod
import configparser
import datetime
import inspect
import logging
from logging import config
import os
import sys
import traceback
from typing import Dict, List, Sequence, Tuple

from debugtrace.log_buffer import LogBuffer
from debugtrace import _print as pr
from debugtrace import version

_config_path: str
_config: configparser.ConfigParser

_logger_name              : str
_logging_config_file      : str
_logging_logger_name      : str
_logging_level            : str
_is_enabled               : bool
_enter_format             : str
_leave_format             : str
_maximum_indents          : int
_indent_string            : str
_data_indent_string       : str
_limit_string             : str
_non_output_string        : str # Currently unused
_cyclic_reference_string  : str
_varname_value_separator  : str
_key_value_separator      : str
_print_suffix_format      : str
_count_format             : str
_minimum_output_count     : int
_length_format            : str
_minimum_output_length    : int
_log_datetime_format      : str
_maximum_data_output_width: int
_bytes_count_in_line      : int
_collection_limit         : int
_bytes_limit              : int
_string_limit             : int
_reflection_nest_limit    : int

# Current nesting level
_nest_level: int = 0

# Previous nesting level
_previous_nest_level: int = 0

# The last output content
_last_print_buff: LogBuffer

# Reflected objects
_reflected_objects: List[object] = []

class _LoggerBase(object):
    '''
    Abstract base class for logger classes.
    '''
    @abstractmethod
    def print(self, message: str) -> None:
        '''
        Outputs the message.

        Args:
            message (str): The message to output
        '''
        pass

class _Std(_LoggerBase):
    '''
    Abstract base class for StdOut and StdErr classes.
    '''
    def __init__(self, iostream):
        '''
        Initializes this object.

        Args:
            iostream: Output destination
        '''
        self.iostream = iostream
    
    def print(self, message: str) -> None:
        '''
        Outputs the message.

        Args:
            message (str): The message to output
        '''
    #   TODO: When called from _DebugTrace .__ del__, an error occurs in datetime.strftime
    #   pr._print(datetime.datetime.now().strftime(_log_datetime_format) + ' ' + message, self.iostream)
        pr._print(str(datetime.datetime.now()) + ' ' + message, self.iostream)

class StdOut(_Std):
    '''
    A logger class that outputs to sys.stdout.
    '''
    def __init__(self):
        '''
        Initializes this object.
        '''
        super().__init__(sys.stdout)

    def __str__(self):
        '''
        Returns a string representation of this object.

        Returns:
            str: A string representation of this object
        '''
        return 'sys.stsdout'

class StdErr(_Std):
    '''
    A logger class that outputs to sys.stderr.
    '''
    def __init__(self):
        '''
        Initializes this object.
        '''
        super().__init__(sys.stderr)

    def __str__(self):
        '''
        Returns a string representation of this object.

        Returns:
            str: A string representation of this object
        '''
        return 'sys.stderr'

class Logger(_LoggerBase):
    '''
    A logger class that outputs using the logging package.
    '''
    def __init__(self):
        '''
        Initializes this object.
        '''
        if os.path.exists(_logging_config_file):
            config.fileConfig(_logging_config_file)
        else:
            pr._print('debugtrace: (' + _config_path + ') _logging_config_file = ' + _logging_config_file + \
                ' (Not found)', sys.stderr)

        self.logger = logging.getLogger(_logging_logger_name)
        self._logging_level = \
            logging.CRITICAL if _logging_level == 'CRITICAL' else \
            logging.ERROR    if _logging_level == 'ERROR'    else \
            logging.WARNING  if _logging_level == 'WARNING'  else \
            logging.INFO     if _logging_level == 'INFO'     else \
            logging.DEBUG    if _logging_level == 'DEBUG'    else \
            logging.NOTSET   if _logging_level == 'NOTSET'   else \
            logging.DEBUG

    def print(self, message: str) -> None:
        '''
        Outputs the message.

        Args:
            message (str): The message to output
        '''
        self.logger.log(self._logging_level, message)

    def __str__(self):
        '''
        Returns a string representation of this object.

        Returns:
            str: A string representation of this object
        '''
        return "logging.Logger('" + _logging_logger_name + "'), logging level: " + _logging_level

_logger : _LoggerBase

def _get_config_value(key: str, fallback: object) -> object:
    '''
    Gets the value related the key from debugtrace.ini file.

    Args:
        key (str): The key
        fallback (object): Value to return when the value related the key is undefined

    Returns:
        object: Value related the key
    '''
    value = fallback
    try:
        if type(fallback) == bool:
            value = _config.getboolean('debugtrace', key, fallback=fallback)
        elif type(fallback) == int:
            value = _config.getint('debugtrace', key, fallback=fallback)
        else:
            value = _config.get('debugtrace', key, fallback=fallback)
            value = value.replace('\\s', ' ')

    except BaseException as ex:
        pr._print('debugtrace: (' + _config_path + ') key: ' + key + ', error: '  + str(ex), sys.stderr)

    return value

def init(config_path: str = './debugtrace.ini'):
    '''
    Initialize debugtrace.

    Args:
        config_path (str): The path of the configuration file.
    '''
    global _config_path
    global _config
    global _logger_name
    global _logging_config_file
    global _logging_logger_name
    global _logging_level
    global _is_enabled
    global _enter_format
    global _leave_format
    global _maximum_indents
    global _indent_string
    global _data_indent_string
    global _limit_string
    global _non_output_string
    global _cyclic_reference_string
    global _varname_value_separator
    global _key_value_separator
    global _print_suffix_format
    global _count_format
    global _minimum_output_count
    global _length_format
    global _minimum_output_length
    global _log_datetime_format
    global _maximum_data_output_width
    global _bytes_count_in_line
    global _collection_limit
    global _bytes_limit
    global _string_limit
    global _reflection_nest_limit
    global _last_print_buff
    global _logger

    # Read a configuration file (debugtrace.ini)
    _config_path = config_path
    _config = configparser.ConfigParser()
    if os.path.exists(_config_path):
        _config.read(_config_path)
    else:
        _config_path = '<No config file>'

    _logger_name               = _get_config_value('logger'                      , 'stderr'                  ).lower()
    _logging_config_file       = _get_config_value('logging_config_file'         , 'logging.conf'            )
    _logging_logger_name       = _get_config_value('logging_logger_name'         , 'debugtrace'               )
    _logging_level             = _get_config_value('logging_level'               , 'DEBUG'                   ).upper()
    _is_enabled                = _get_config_value('is_enabled'                  , True                      )
    _enter_format              = _get_config_value('enter_format'                , 'Enter {0} ({1}:{2})'     )
    _leave_format              = _get_config_value('leave_format'                , 'Leave {0} ({1}:{2}) duration: {3}')
    _maximum_indents           = _get_config_value('maximum_indents'             , 32                        )
    _indent_string             = _get_config_value('indent_string'               , '| '                      )
    _data_indent_string        = _get_config_value('data_indent_string'          , '  '                      )
    _limit_string              = _get_config_value('limit_string'                , '...'                     )
    _non_output_string         = _get_config_value('non_output_string'           , '...'                     )
    _cyclic_reference_string   = _get_config_value('cyclic_reference_string'     , '*** Cyclic Reference ***')
    _varname_value_separator   = _get_config_value('varname_value_separator'     , ' = '                     )
    _key_value_separator       = _get_config_value('key_value_separator'         , ': '                      )
    _print_suffix_format       = _get_config_value('print_suffix_format'         , ' ({1}:{2})'              )
    _count_format              = _get_config_value('count_format'                , 'count:{}'                )
    _minimum_output_count      = _get_config_value('minimum_output_count'        , 5                         )
    _length_format             = _get_config_value('length_format'               , 'length:{}'               )
    _minimum_output_length     = _get_config_value('minimum_output_length'       , 5                         )
    _log_datetime_format       = _get_config_value('log_datetime_format'         , '%Y-%m-%d %H:%M:%S.%f'    )
    _maximum_data_output_width = _get_config_value('maximum_data_output_width'   , 70                        )
    _bytes_count_in_line       = _get_config_value('bytes_count_in_line'         , 16                        )
    _collection_limit          = _get_config_value('collection_limit'            , 512                       )
    _bytes_limit               = _get_config_value('bytes_limit'                 , 8192                      )
    _string_limit              = _get_config_value('string_limit'                , 8192                      )
    _reflection_nest_limit     = _get_config_value('reflection_nest_limit'       , 4                         )

    _last_print_buff = LogBuffer(_maximum_data_output_width)

    # Decides the logger class
    _logger = StdErr()
    if _logger_name == 'stdout':
        _logger = StdOut()
    elif _logger_name == 'stderr':
        _logger = StdErr()
    elif _logger_name == 'logger':
        _logger = Logger()
    else:
        pr._print('debugtrace: (' + _config_path + ') logger = ' + _logger_name + ' (Unknown)', sys.stderr)

    if _is_enabled:
        _logger.print('DebugTrace-py ' + version.VERSION)
        _logger.print('  config file path: ' + _config_path)
        _logger.print('　logger: ' + str(_logger))
        _logger.print('')

class _PrintOptions(object):
    '''
    Hold output option values.
    '''
    def __init__(self,
        force_reflection: bool,
        output_private: bool,
        output_method: bool,
        collection_limit: int,
        string_limit: int,
        bytes_limit: int,
        reflection_nest_limit:int
        ) -> None:
        '''
        Initializes this object.
        Args:
            force_reflection (bool): If true, outputs using reflection even if it has a __str__or __repr__ method
            output_private (bool): If true, also outputs private members when using reflection
            output_method (bool): If true, also outputs method members when using reflection
            collection_limit (int): Output limit of collection elements (overrides debugtarace.ini value)
            string_limit (int): Output limit of string characters (overrides debugtarace.ini value)
            bytes_limit (int): Output limit of byte array elements (overrides debugtarace.ini value)
            reflection_nest_limit (int): Nest limits when using reflection (overrides debugtarace.ini value)
        '''
        global _collection_limit
        global _string_limit
        global _bytes_limit
        global _reflection_nest_limit
        self.force_reflection = force_reflection
        self.output_private   = output_private
        self.output_method    = output_method
        self.collection_limit      = _collection_limit      if collection_limit      is None else collection_limit     
        self.string_limit          = _string_limit          if string_limit          is None else string_limit         
        self.bytes_limit           = _bytes_limit           if bytes_limit           is None else bytes_limit          
        self.reflection_nest_limit = _reflection_nest_limit if reflection_nest_limit is None else reflection_nest_limit

def _up_nest() -> None:
    '''
    Ups the code nest level.
    '''
    global _nest_level
    global _previous_nest_level
    _previous_nest_level = _nest_level
    _nest_level += 1

def _down_nest() -> None:
    '''
    Downs the code nest level.
    '''
    global _nest_level
    global _previous_nest_level
    _previous_nest_level = _nest_level
    _nest_level -= 1

def _get_indent_string(data_nest_lebel: int = 0) -> str:
    '''
    Returns a string with the current code indent combined with the data indent.

    Args:
        data_nest_lebel (int): The data nest level

    Returns:
        a indent string
    '''
    indent_str = _indent_string * min(max(0, _nest_level), _maximum_indents)
    data_indent_str = _data_indent_string * min(max(0, data_nest_lebel), _maximum_indents)
    return indent_str + data_indent_str

def _to_string(name: str, value: object, print_options: _PrintOptions) -> LogBuffer:
    '''
    Returns a LogBuffer containing a string representation of the the name and value.

    Args:
        name (str): The name related to the value
        value (object): The value
        print_options (_PrintOptions): Output options 

    Returns:
        LogBuffer: a LogBuffer
    '''
    buff = LogBuffer(_maximum_data_output_width)

    separator = None
    if name is not None:
        buff.append(name)
        separator = _varname_value_separator

    if value is None:
        # None
        buff.no_break_append(separator).append('None')

    elif isinstance(value, str):
        # str
        value_buff = _to_string_str(value, print_options)
        buff.append_buffer(separator, value_buff)

    elif isinstance(value, bytes) or isinstance(value, bytearray):
        # bytes
        value_buff = _to_string_bytes(value, print_options)
        buff.append_buffer(separator, value_buff)

    elif isinstance(value, int) or isinstance(value, float) or \
        isinstance(value, datetime.date) or isinstance(value, datetime.time) or \
        isinstance(value, datetime.datetime):
        # int, float, datetime.date, datetime.time, datetime.datetime
        buff.no_break_append(separator).append(str(value))

    elif isinstance(value, list) or \
            isinstance(value, set) or isinstance(value, frozenset) or \
            isinstance(value, tuple) or \
            isinstance(value, dict):
        # list, set, frozenset, tuple, dict
        value_buff = _to_string_iterable(value, print_options)
        buff.append_buffer(separator, value_buff)

    else:
        has_str, has_repr = _has_str_repr_method(value)
        value_buff = LogBuffer(_maximum_data_output_width)
        if not print_options.force_reflection and (has_str or has_repr):
            # has __str__ or __repr__ method
            if has_repr:
                value_buff.append('repr(): ')
                value_buff.no_break_append(repr(value))
            else:
                value_buff.append('str(): ')
                value_buff.no_break_append(str(value))
            buff.append_buffer(separator, value_buff)

        else:
            # use refrection
            if any(map(lambda obj: value is obj, _reflected_objects)):
                # cyclic reference
                value_buff.no_break_append(_cyclic_reference_string)
            elif len(_reflected_objects) > print_options.reflection_nest_limit:
                # over reflection level limitation
                value_buff.no_break_append(_limit_string)
            else:
                _reflected_objects.append(value)
                value_buff = _to_string_refrection(value, print_options)
                _reflected_objects.pop()
            buff.append_buffer(separator, value_buff)

    return buff

def _to_string_str(value: str, print_options: _PrintOptions) -> LogBuffer:
    '''
    Returns a LogBuffer containing a string representation of the string value.

    Args:
        value (str): The string value
        print_options (_PrintOptions): Output options 

    Returns:
        LogBuffer: a LogBuffer
    '''
    has_single_quote = False
    has_double_quote = False
    single_quote_buff = LogBuffer(_maximum_data_output_width)
    double_quote_buff = LogBuffer(_maximum_data_output_width)
    if len(value) >= _minimum_output_length:
        single_quote_buff.no_break_append('(')
        single_quote_buff.no_break_append(_length_format.format(len(value)))
        single_quote_buff.no_break_append(')')
        double_quote_buff.no_break_append('(')
        double_quote_buff.no_break_append(_length_format.format(len(value)))
        double_quote_buff.no_break_append(')')
    single_quote_buff.no_break_append("'")
    double_quote_buff.no_break_append('"')

    count = 1
    for char in value:
        if count > print_options.string_limit:
            single_quote_buff.no_break_append(_limit_string)
            double_quote_buff.no_break_append(_limit_string)
            break
        if char == "'":
            single_quote_buff.no_break_append("\\'")
            double_quote_buff.no_break_append(char)
            has_single_quote = True
        elif char == '"':
            single_quote_buff.no_break_append(char)
            double_quote_buff.no_break_append('\\"')
            has_double_quote = True
        elif char == '\\':
            single_quote_buff.no_break_append('\\\\')
            double_quote_buff.no_break_append('\\\\')
        elif char == '\n':
            single_quote_buff.no_break_append('\\n')
            double_quote_buff.no_break_append('\\n')
        elif char == '\r':
            single_quote_buff.no_break_append('\\r')
            double_quote_buff.no_break_append('\\r')
        elif char == '\t':
            single_quote_buff.no_break_append('\\t')
            double_quote_buff.no_break_append('\\t')
        elif char < ' ':
            num_str = format(ord(char), '02X')
            single_quote_buff.no_break_append('\\x' + num_str)
            double_quote_buff.no_break_append('\\x' + num_str)
        else:
            single_quote_buff.no_break_append(char)
            double_quote_buff.no_break_append(char)
        count += 1

    double_quote_buff.no_break_append('"')
    single_quote_buff.no_break_append("'")
    if has_single_quote and not has_double_quote:
        return double_quote_buff
    return single_quote_buff

def _to_string_bytes(value: bytes, print_options: _PrintOptions) -> LogBuffer:
    '''
    Returns a LogBuffer containing a string representation of the bytes value.

    Args:
        value (bytes): The bytes value
        print_options (_PrintOptions): Output options 

    Returns:
        LogBuffer: a LogBuffer
    '''
    bytes_length = len(value)
    buff = LogBuffer(_maximum_data_output_width)
    buff.no_break_append('(')
    if type(value) == bytes:
        buff.no_break_append('bytes')
    elif type(value) == bytearray:
        buff.no_break_append('bytearray')
    if bytes_length >= _minimum_output_length:
        buff.no_break_append(' ')
        buff.no_break_append(_length_format.format(bytes_length))
    buff.no_break_append(')[')

    is_multi_lines = bytes_length >= _bytes_count_in_line

    if is_multi_lines:
        buff.line_feed()
        buff.up_nest()

    chars = ''
    count = 0
    for element in value:
        if count != 0 and count % _bytes_count_in_line == 0:
            if is_multi_lines:
                buff.no_break_append('| ')
                buff.no_break_append(chars)
                buff.line_feed()
                chars = ''
        if (count >= print_options.bytes_limit):
            buff.no_break_append(_limit_string)
            break
        buff.no_break_append('{:02X} '.format(element))
        chars += chr(element) if element >= 0x20 and element <= 0x7E else '.'
        count += 1

    if is_multi_lines:
        # padding
        full_length = 3 * _bytes_count_in_line
        current_length = buff.length
        if current_length == 0:
            current_length = full_length
        buff.no_break_append(' ' * (full_length - current_length))
    buff.no_break_append('| ')
    buff.no_break_append(chars)

    if is_multi_lines:
        buff.line_feed()
        buff.down_nest()
    buff.no_break_append(']')

    return buff

def _to_string_refrection(value: object, print_options: _PrintOptions) -> LogBuffer:
    '''
    Returns a LogBuffer containing a string representation of the value with reflection.

    Args:
        value (bytes): The value to append
        print_options (_PrintOptions): Output options 

    Returns:
        LogBuffer: a LogBuffer
    '''
    buff = LogBuffer(_maximum_data_output_width)

    buff.append(_get_type_name(value))

    body_buff = _to_string_refrection_body(value, print_options)

    is_multi_lines = body_buff.is_multi_lines or buff.length + body_buff.length > _maximum_data_output_width

    buff.no_break_append('{')
    if is_multi_lines:
        buff.line_feed()
        buff.up_nest()

    buff.append_buffer(None, body_buff)

    if is_multi_lines:
        if buff.length > 0:
            buff.line_feed()
        buff.down_nest()
    buff.no_break_append('}')

    return buff

def _to_string_refrection_body(value: object, print_options: _PrintOptions) -> LogBuffer:
    '''
    Returns a LogBuffer containing the body of a string representation of the value with reflection.

    Args:
        value (bytes): The value to append
        print_options (_PrintOptions): Output options 

    Returns:
        LogBuffer: a LogBuffer
    '''
    buff = LogBuffer(_maximum_data_output_width)

    members = []
    try:
        base_members = inspect.getmembers(value,
            lambda v: not inspect.isclass(v) and
                (print_options.output_method or not inspect.ismethod(v)) and
                not inspect.isbuiltin(v))

        members = [m for m in base_members
                if (not m[0].startswith('__') or not m[0].endswith('__')) and
                    (print_options.output_private or not m[0].startswith('_'))]
    except BaseException as ex:
        buff.append(str(ex))
        return buff

    was_multi_lines = False
    index = 0
    for member in members:
        if index > 0:
            buff.no_break_append(', ')

        name = member[0]
        value = member[1]
        member_buff = LogBuffer(_maximum_data_output_width)
        member_buff.append(name)
        member_buff.append_buffer(_key_value_separator, _to_string(None, value, print_options))
        if index > 0 and (was_multi_lines or member_buff.is_multi_lines):
            buff.line_feed()
        buff.append_buffer(None, member_buff)

        was_multi_lines = member_buff.is_multi_lines
        index += 1

    return buff

def _to_string_iterable(values: object, print_options: _PrintOptions) -> LogBuffer:
    '''
    Returns a LogBuffer containing a string representation of the iterable value.

    Args:
        value (object): The iterable value to append
        print_options (_PrintOptions): Output options 

    Returns:
        LogBuffer: a LogBuffer
    '''
    open_char = '{' # set, frozenset, dict
    close_char = '}'
    if isinstance(values, list):
        # list
        open_char = '['
        close_char = ']'
    elif isinstance(values, tuple):
        # tuple
        open_char = '('
        close_char = ')'
    
    buff = LogBuffer(_maximum_data_output_width)
    buff.append(_get_type_name(values, len(values)))
    buff.no_break_append(open_char)

    body_buff = _to_string_iterable_body(values, print_options)
# 1.1.0
    if open_char == '(' and len(values) == 1:
        # A tuple with 1 element 
        body_buff.no_break_append(',')
####

    is_multi_lines = body_buff.is_multi_lines or buff.length + body_buff.length > _maximum_data_output_width

    if is_multi_lines:
        buff.line_feed()
        buff.up_nest()

    buff.append_buffer(None, body_buff)

    if is_multi_lines:
        buff.line_feed()
        buff.down_nest()

    buff.no_break_append(close_char)

    return buff

def _to_string_iterable_body(values: object, print_options: _PrintOptions) -> LogBuffer:
    '''
    Returns a LogBuffer containing the body of a string representation of the iterable value.

    Args:
        value (object): The iterable value to append
        print_options (_PrintOptions): Output options 

    Returns:
        LogBuffer: a LogBuffer
    '''
    buff = LogBuffer(_maximum_data_output_width)

    was_multi_lines = False
    index = 0
    for element in values:
        if index > 0:
            buff.no_break_append(', ')

        if index >= print_options.collection_limit:
            buff.append(_limit_string)
            break

        element_buff = LogBuffer(_maximum_data_output_width)
        if isinstance(values, dict):
            # dictionary
            element_buff = _to_string_key_value(element, values[element], print_options)
        else:
            # list, set, frozenset or tuple
            element_buff = _to_string(None, element, print_options)

        if index > 0 and (was_multi_lines or element_buff.is_multi_lines):
            buff.line_feed()
        buff.append_buffer(None, element_buff)

        was_multi_lines = element_buff.is_multi_lines
        index += 1

# 1.1.0
    if isinstance(values, dict) and len(values) == 0:
        buff.no_break_append(':')
####

    return buff

def _to_string_key_value(key: object, value: object, print_options: _PrintOptions) -> LogBuffer:
    '''
    Returns a LogBuffer containing a string representation of the the key and value.

    Args:
        key (object): The key related to the value
        value (object): The value
        print_options (_PrintOptions): Output options 

    Returns:
        LogBuffer: a LogBuffer
    '''
    buff = LogBuffer(_maximum_data_output_width)
    key_buff = _to_string(None, key, print_options)
    value_buff = _to_string(None, value, print_options)
    buff.append_buffer(None, key_buff).append_buffer(_key_value_separator, value_buff)
    return buff

def _get_type_name(value: object, count: int = -1) -> str:
    '''
    Returns the type name of the value.

    Args:
        value (object): The value
        count (int): Number of elements of the value if it is a collection

    Returns:
        str: The type name
    '''
# 1.1.0
#   type_name = '('
#   type_name += _get_simple_type_name(type(value), 0)
#
#   if count >= _minimum_output_count:
#       type_name += ' ' + _count_format.format(count)
#   type_name += ')'
#   return type_name
    value_type = type(value)
    type_name = _get_simple_type_name(type(value), 0)
    if (type_name == 'tuple' or type_name == 'list' or type_name == 'set' or type_name == 'dict'):
        type_name = ''

    if count >= _minimum_output_count:
        if len(type_name) > 0:
            type_name += ' '
        type_name += _count_format.format(count)
    if len(type_name) > 0:
        type_name = '(' + type_name + ')'
    return type_name
####

def _get_simple_type_name(value_type: type, nest: int) -> str:
    '''
    Returns the simple type name.

    Args:
        value_type (type): The type
        nest (int): Nesting level of this method call

    Returns:
        str: The simple type name
    '''
    type_name = str(value_type) if nest == 0 else value_type.__name__
    if type_name.startswith("<class '"):
        type_name = type_name[8:]
    elif type_name.startswith("<enum '"):
        type_name = 'enum ' + type_name[7:]
    if type_name.endswith("'>"):
        type_name = type_name[:-2]

    base_names = list(
        map(lambda base: _get_simple_type_name(base, nest + 1),
        filter(lambda base: base != object,
            value_type.__bases__)))

    if len(base_names) > 0:
        type_name += '('
        type_name += ', '.join(base_names)
        type_name += ')'

    return type_name

def _has_str_repr_method(value: object) -> Tuple[bool, bool]:
    '''
    Returns true if the class of the value has __str__ or __repr__ method.

    Args:
        value: The value

    Returns:
        bool: True if the class of the value has __str__ or __repr__ method
    '''
    try:
        members = inspect.getmembers(value, lambda v: inspect.ismethod(v))
        return (
            len([member for member in members if member[0] == '__str__']) != 0,
            len([member for member in members if member[0] == '__repr__']) != 0)
    except:
        return False, False

def _get_frame_summary(limit: int) -> traceback.FrameSummary:
    try:
        raise RuntimeError
    except RuntimeError:
        return traceback.extract_stack(limit=limit)[0]
    return None

_DO_NOT_OUTPUT = 'Do not output'

def print(name: str, value: object = _DO_NOT_OUTPUT, *,
        force_reflection: bool = False,
        output_private: bool = False,
        output_method: bool = False,
        collection_limit: int = None,
        string_limit: int = None,
        bytes_limit: int = None,
        reflection_nest_limit: int = None
        ) -> None:
    '''
    Outputs the name and value.

    Args:
        name (str): The name of the value (simply output message if the value is omitted).
        value (object, optional): The value to output if not omitted.
        force_reflection (bool, optional): If true, outputs using reflection even if it has a __str__ or __repr__ method. Defaults to None
        output_private (bool, optional): If true, also outputs private members when using reflection. Defaults to None
        output_method (bool, optional): If true, also outputs method members when using reflection. Defaults to None
        collection_limit (int, optional): Output limit of collection elements (overrides debugtarace.ini value). Defaults to None
        string_limit (int, optional): Output limit of string characters (overrides debugtarace.ini value). Defaults to None
        bytes_limit (int, optional): Output limit of byte array elements (overrides debugtarace.ini value). Defaults to None
        reflection_nest_limit (int, optional): Nest limits when using reflection (overrides debugtarace.ini value). Defaults to None

    The following is in Japanese.
    
    名前と値を出力します。

    引数:
        name (str): 出力する名前 (valueが省略されている場合は、単に出力するメッセージ)
        value (object, optional): 出力する値 (省略されていなければ)
        force_reflection (bool, optional): Trueなら __str__ または __repr__ メソッドが定義されていてもリフレクションを使用する。デフォルトは指定なし
        output_private (bool, optional): Trueならプライベートメンバーも出力する。デフォルトは指定なし
        output_method (bool, optional): Trueならメソッドも出力する。デフォルトは指定なし
        collection_limit (int, optional): コレクションの要素の出力数の制限 (debugtarace.iniの値より優先)。デフォルトは指定なし
        string_limit (int, optional): 文字列値の出力文字数の制限 (debugtarace.iniの値より優先)。デフォルトは指定なし
        bytes_limit (int, optional): バイト配列bytesの内容の出力数の制限 (debugtarace.iniの値より優先)。デフォルトは指定なし
        reflection_nest_limit (int, optional): リフレクションのネスト数の制限 (debugtarace.iniの値より優先)。デフォルトは指定なし
    '''
    global _last_print_buff
    global _reflected_objects

    if not _is_enabled: return

    _reflected_objects.clear()

    last_is_multi_lines = _last_print_buff.is_multi_lines

    if value is _DO_NOT_OUTPUT:
        # without value
        _last_print_buff = LogBuffer(_maximum_data_output_width)
        _last_print_buff.no_break_append(name)

    else:
        # with value
        print_options = _PrintOptions(
            force_reflection, output_private, output_method,
            collection_limit, string_limit, bytes_limit, reflection_nest_limit)

        _last_print_buff = _to_string(name, value, print_options)

    # append print suffix
    frame_summary = _get_frame_summary(3)
    _last_print_buff.no_break_append(
        _print_suffix_format.format(
            frame_summary.name,
            os.path.basename(frame_summary.filename),
            frame_summary.lineno))

    _last_print_buff.line_feed()

    if last_is_multi_lines or _last_print_buff.is_multi_lines:
        _logger.print(_get_indent_string()) # Empty Line

    lines = _last_print_buff.lines
    for line in lines:
        _logger.print(_get_indent_string(line[0]) + line[1])

class _DebugTrace(object):
    '''
    Outputs a entering log when initializing and outputs an leaving log when deleting.
    '''
    __slots__ = [
        'name',
        'filename',
        'lineno',
        'enter_time',
    ]
    
    def __init__(self, invoker: object) -> None:
        '''
        Initializes this object.

        Args:
            invoker (object): The object or class that invoked this method.
        '''
        global _nest_level
        global _previous_nest_level
        global _last_print_buff

        if not _is_enabled: return

        if invoker is None:
            self.name = ''
        else:
            self.name = type(invoker).__name__
            if self.name == 'type':
                self.name = invoker.__name__
            self.name += '.'

        frame_summary = _get_frame_summary(4)
        self.name += frame_summary.name
        self.filename = os.path.basename(frame_summary.filename)
        self.lineno = frame_summary.lineno

        indent_string = _get_indent_string()
        if _nest_level < _previous_nest_level or _last_print_buff.is_multi_lines:
            _logger.print(indent_string) # Empty Line

        _last_print_buff = LogBuffer(_maximum_data_output_width)
        _last_print_buff.no_break_append(_enter_format.format(self.name, self.filename, self.lineno))
        _last_print_buff.line_feed()
        _logger.print(indent_string + _last_print_buff.lines[0][1])

        _up_nest()

        self.enter_time = datetime.datetime.now()

    def __del__(self):
        '''
        Called when the instance is about to be destroyed.
        '''
        global _last_print_buff

        if not _is_enabled: return

        time = datetime.datetime.now() - self.enter_time

        if _last_print_buff.is_multi_lines:
            _logger.print(_get_indent_string()) # Empty Line

        _down_nest()

        _last_print_buff = LogBuffer(_maximum_data_output_width)
        _last_print_buff.no_break_append(_leave_format.format(self.name, self.filename, self.lineno, time))
        _last_print_buff.line_feed()
        _logger.print(_get_indent_string() + _last_print_buff.lines[0][1])

def enter(invoker: object=None) -> _DebugTrace:
    '''
    By calling this method when entering an execution block such as a function or method,
    outputs an entering log.
    Store the return value in some variable (such as _).
    Outputs a leaving log when leaving the scope of this variable.

    Args
        invoker (object, optional): The object or class that invoked this method. Defaults to None
    
    Returns:
        _DebugTrace: An inner class object.

    The following is in Japanese.

    関数やメソッドなどの実行ブロックに入る際にこのメソッドを呼び出す事で、開始のログを出力します。
    戻り値は何かの変数(例えば _)に格納してください。この変数のスコープを出る際に終了のログを出力します。

    引数:
        invoker　(object, optional): このメソッドを呼び出したオブジェクトまたはクラス。デフォルトは指定なし
    
    戻り値:
        内部クラスのオブジェクト。
    '''
    return _DebugTrace(invoker)

def last_print_string() -> str:
    '''
    Returns a last output string.

    Returns:
        str: a last output string
    '''
    lines = _last_print_buff.lines
    buff_string = '\n'.join(
        list(map(lambda line: _data_indent_string * line[0] + line[1], lines))
    )
    return _get_indent_string() + buff_string

init()

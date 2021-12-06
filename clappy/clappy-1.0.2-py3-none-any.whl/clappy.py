from sys import argv
import logging
import argparse
from argparse import *
import functools
import inspect
from gettext import gettext as _
from typing import Optional
import pathlib
from collections import namedtuple

import __main__

PREFIX_CHAR_OF_OPTION = "-"

logger = logging.getLogger(__name__)

VERSION_OPTIONS = ["-V", "--version"]
HELP_MESSAGE_FOR_V = "Show version and exit."

generates_help_of_version = True


def _normalize_bound_of_args(func):
    """Same hash by same values.
    This converts each keyword arg to positional arg if possible.
    If argument with default value doesn't get actual argument, explicitly give the default value.
    """
    signature = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        return func(*bound.args, **bound.kwargs)

    return wrapper


# TODO version optionのデフォルト機能つける
# groupの順番

# def raise_SystemExit():
#     try:
#         1/0
#     except:
#         import sys
#         sys.exit()

class _HelpMaker:
    unique_instance = None
    _help_chars = ("-h", "--help")
    MESSAGE_ON_DUPLICATE = "Another instance is already in use as context manager. " \
                           "Use only once to print help."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_in_with_block = False

    class _AlreadyInWithBlock(Exception):
        pass

    def __enter__(self):
        if self.active_in_with_block:
            raise self._AlreadyInWithBlock(f"Already an instance to create help is used in with block. "
                                           f"You can use only one in the block.")
        self.active_in_with_block = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is exc_val is exc_tb is None:
            _finish_parsing()
        else:
            raise exc_val

    @classmethod
    @functools.lru_cache
    def runs_for_help(cls):
        if not cls.unique_instance:
            cls.unique_instance = cls()
        for help_char in cls._help_chars:
            if help_char in argv:
                return True
        return False

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if not cls.unique_instance:
            cls.unique_instance = cls(*args, **kwargs)
        return cls.unique_instance


exits_after_help_message = True


def _finish_parsing():
    parser = _Parser.unique_instance
    if _HelpMaker.runs_for_help():
        if generates_help_of_version:
            if hasattr(__main__, "__version__"):
                parse(*VERSION_OPTIONS, help=HELP_MESSAGE_FOR_V)
        for subparser in parser.subparsers_list:
            if subparser.invoked:
                subparser.print_help()
                break
        else:
            parser.print_help()
        if exits_after_help_message:
            exit()
    else:
        parsed, unrecognized = parser.parse_known_args()
        if unrecognized:
            logger.error(_Parser.unique_instance.UNRECOGNIZED_ERROR_MESSAGE % unrecognized)


def end_parse_for_help():
    """Create help and exit program. Run this method only if you want help message on running with -h or --help."""
    _finish_parsing()


def help_maker():
    return get_parser()


class ErrorInArgumentParser(Exception):
    """Raised when ArgumentParser().error runs. The method is replaced"""
    pass


# noinspection PyUnresolvedReferences,PyProtectedMember
class _Parser(argparse.ArgumentParser, _HelpMaker):
    unique_instance: Optional["_Parser"] = None
    SUBCOMMAND_DEST = "_subcommand_dest_for_clappy"
    dest_name = SUBCOMMAND_DEST  # for detecting which subcommand is invoked
    VERBOSE_VALUE_CHANGE_MESSAGE = '''
    While parsing {parsing_dest}, the value of "{name_of_changed_arg}" changed from {last_val} to {current_val}.
This usually happens because of similar names of arguments or confusing order of arguments.
Consider to change them if you actually got invalid result.'''
    VALUE_CHANGE_MESSAGE = '''"{name_of_changed_arg}" changed from {last_val} to {current_val} in the middle of parse.'''
    UNRECOGNIZED_ERROR_MESSAGE = "unrecognized args: %s"

    def __init__(self, *args, **kwargs):
        self.args_for_parse: list = argv[1::] or None
        self.last_namespace = None
        self.parsed_result = dict()
        self.subparsers_list = []
        self.subparsers_action = None
        if kwargs.get("add_help") is True:
            self.add_help_argument = True
            kwargs["add_help"] = False
        else:
            self.add_help_argument = False
        self.printed_verbose_log = False
        super().__init__(*args, **kwargs)

    # def error(self, message: str) -> None:
    #     return super().error(message)
    #     raise ErrorInArgumentParser(message)

    def add_argument(self, *args, is_flag=False, **kwargs):
        if is_flag:
            if kwargs.get("action", None) is None:
                kwargs["action"] = "store_true"
            else:
                raise TypeError(f"{self.add_argument.__name__} got multiple values for action, "
                                f"since is_flag=True is alias of action='store_true'.")

        try:
            action = self._add_argument(*args, **kwargs)
        except argparse.ArgumentError as e:
            if e.message.startswith("conflicting"):
                msg = \
                    "Tried to register same argument." \
                    "Usually, the cache is returned in such case. However, cache is not returned this time " \
                    "since some of given arguments are different from last time." \
                    f"Use same arguments for {self.parse.__name__}() to get cache."
                raise ValueError(msg) from e
            else:
                raise e

        @functools.lru_cache()  # so that parse can be called multiple times to get result in multiple places.
        def _parse_from_action():
            if _HelpMaker.runs_for_help():
                return
            latest_namespace, unrecognized_args = self.parse_known_args()
            logger.debug(f"Unrecognized args while parsing {action.dest}: {unrecognized_args}")
            if self.last_namespace:
                for attr in self.last_namespace.__dict__:
                    last_time = getattr(self.last_namespace, attr)
                    this_time = getattr(latest_namespace, attr)
                    if last_time != this_time:
                        if self.printed_verbose_log:
                            message = self.VALUE_CHANGE_MESSAGE.format(
                                name_of_changed_arg=attr, last_val=last_time, current_val=this_time)
                        else:
                            self.printed_verbose_log = True
                            message = self.VERBOSE_VALUE_CHANGE_MESSAGE.format(
                                parsing_dest=action.dest, name_of_changed_arg=attr,
                                last_val=last_time, current_val=this_time)
                        logger.error(message)
            self.last_namespace = latest_namespace
            return getattr(latest_namespace, action.dest)

        action.parse = _parse_from_action
        return action

    def _add_argument(self, *args, **kwargs):
        active_groups = _GroupForWith.instances
        if active_groups:
            # noinspection PyUnresolvedReferences
            action = active_groups[-1].add_argument(*args, **kwargs)
        elif args == ('-h', '--help'):
            action = super().add_argument(*args, **kwargs)
        else:  # not within with block
            group = get_group()
            obj = group if group is not None else super()
            action = obj.add_argument(*args, **kwargs)
        return action

    @_normalize_bound_of_args
    @functools.lru_cache()  # so that parse can be called multiple times just to get result in multiple places.
    def parse(self, *args, is_flag=False, **kwargs):
        action = self.add_argument(*args, is_flag=is_flag, **kwargs)
        return action.parse()

    @staticmethod
    def _print_version():
        print(f"version {__main__.__version__} {__main__.__file__.split('/')[-1]}")

    def add_argument_group(self, *args, **kwargs):
        group = _GroupForWith(self, *args, **kwargs)
        self._action_groups.append(group)
        return group

    def parse_known_args(self, args=None, namespace=None):
        args = args or self.args_for_parse
        result = super().parse_known_args(args, namespace)
        for act in self._actions:
            if hasattr(act, "parsed_currently"):
                act.parsed_currently = False
        return result

    @staticmethod
    def _get_action_name(argument):
        if argument is None:
            return None
        elif argument.option_strings:
            return '/'.join(argument.option_strings)
        elif argument.metavar not in (None, SUPPRESS):
            return argument.metavar
        elif argument.dest not in (None, SUPPRESS):
            return argument.dest
        else:
            return None

    # noinspection PyProtectedMember,PyUnusedLocal,PyAssignmentToLoopOrWithParameter
    def _parse_known_args(self, arg_strings, namespace):
        """Almost same copy as super()._parse_known_args.
        This differs by lines 105-107 rows below, 140 rows below and 158 rows below"""

        # replace arg strings that are file references
        if self.fromfile_prefix_chars is not None:
            arg_strings = self._read_args_from_files(arg_strings)

        # map all mutually exclusive arguments to the other arguments
        # they can't occur with
        action_conflicts = {}
        for mutex_group in self._mutually_exclusive_groups:
            group_actions = mutex_group._group_actions
            for i, mutex_action in enumerate(mutex_group._group_actions):
                conflicts = action_conflicts.setdefault(mutex_action, [])
                conflicts.extend(group_actions[:i])
                conflicts.extend(group_actions[i + 1:])

        # find all option indices, and determine the arg_string_pattern
        # which has an 'O' if there is an option at an index,
        # an 'A' if there is an argument, or a '-' if there is a '--'
        option_string_indices = {}
        arg_string_pattern_parts = []
        arg_strings_iter = iter(arg_strings)
        for i, arg_string in enumerate(arg_strings_iter):

            # all args after -- are non-options
            if arg_string == '--':
                arg_string_pattern_parts.append('-')
                for arg_string in arg_strings_iter:
                    arg_string_pattern_parts.append('A')

            # otherwise, add the arg to the arg strings
            # and note the index if it was an option
            else:
                option_tuple = self._parse_optional(arg_string)
                if option_tuple is None:
                    pattern = 'A'
                else:
                    option_string_indices[i] = option_tuple
                    pattern = 'O'
                arg_string_pattern_parts.append(pattern)

        # join the pieces together to form the pattern
        arg_strings_pattern = ''.join(arg_string_pattern_parts)

        # converts arg strings to the appropriate and then takes the action
        seen_actions = set()
        seen_non_default_actions = set()

        def take_action(action, argument_strings, option_string=None):
            seen_actions.add(action)
            argument_values = self._get_values(action, argument_strings)

            # error if this argument is not allowed with other previously
            # seen arguments, assuming that actions that use the default
            # value don't really count as "present"
            if argument_values is not action.default:
                seen_non_default_actions.add(action)
                for conflict_action in action_conflicts.get(action, []):
                    if conflict_action in seen_non_default_actions:
                        msg = _('not allowed with argument %s')
                        action_name = self._get_action_name(conflict_action)
                        raise ArgumentError(action, msg % action_name)

            # take the action if we didn't receive a SUPPRESS value
            # (e.g. from a default)
            if argument_values is not SUPPRESS:
                action(self, namespace, argument_values, option_string)

        # function to convert arg_strings into an optional action
        def consume_optional(start_index):

            # get the optional identified at this index
            option_tuple = option_string_indices[start_index]
            action, option_string, explicit_arg = option_tuple

            # identify additional optionals in the same arg string
            # (e.g. -xyz is the same as -x -y -z if no args are required)
            match_argument = self._match_argument
            action_tuples = []
            while True:

                # if we found no optional action, skip it
                if action is None:
                    extras.append(arg_strings[start_index])
                    return start_index + 1

                # if there is an explicit argument, try to match the
                # option's string arguments to only this
                if explicit_arg is not None:
                    arg_count = match_argument(action, 'A')

                    # if the action is a single-dash option and takes no
                    # arguments, try to parse more single-dash options out
                    # of the tail of the option string
                    chars = self.prefix_chars
                    if arg_count == 0 and option_string[1] not in chars:
                        action_tuples.append((action, [], option_string))
                        char = option_string[0]
                        option_string = char + explicit_arg[0]
                        new_explicit_arg = explicit_arg[1:] or None
                        optionals_map = self._option_string_actions
                        if option_string in optionals_map:
                            action = optionals_map[option_string]
                            explicit_arg = new_explicit_arg
                        else:
                            if self._check_if_jointed_short_option(action, option_string):
                                explicit_arg = None
                            else:
                                msg = _('ignored explicit argument %r')
                                raise ArgumentError(action, msg % explicit_arg)

                    # if the action expect exactly one argument, we've
                    # successfully matched the option; exit the loop
                    elif arg_count == 1:
                        stop = start_index + 1
                        args = [explicit_arg]
                        action_tuples.append((action, args, option_string))
                        break

                    # error if a double-dash option did not use the
                    # explicit argument
                    else:
                        msg = _('ignored explicit argument %r')
                        raise ArgumentError(action, msg % explicit_arg)

                # if there is no explicit argument, try to match the
                # option's string arguments with the following strings
                # if successful, exit the loop
                else:
                    start = start_index + 1
                    selected_patterns = arg_strings_pattern[start:]
                    arg_count = match_argument(action, selected_patterns)
                    stop = start + arg_count
                    args = arg_strings[start:stop]
                    action_tuples.append((action, args, option_string))
                    break

            # add the Optional to the list and return the index at which
            # the Option's string args stopped
            assert action_tuples
            self._run_if_not_parsed(namespace, take_action, explicit_arg, arg_strings, action_tuples)
            return stop

        # the list of Positionals left to be parsed; this is modified
        # by consume_positionals()
        positionals = self._get_positional_actions()

        # function to convert arg_strings into positional actions
        def consume_positionals(start_index):
            # match as many Positionals as possible
            match_partial = self._match_arguments_partial
            selected_pattern = arg_strings_pattern[start_index:]
            arg_counts = match_partial(positionals, selected_pattern)

            # slice off the appropriate arg strings for each Positional
            # and add the Positional and its args to the list
            for action, arg_count in zip(positionals, arg_counts):
                args = arg_strings[start_index: start_index + arg_count]
                start_index += arg_count
                take_action(action, args)

            # slice off the Positionals that we just parsed and return the
            # index at which the Positionals' string args stopped
            positionals[:] = positionals[len(arg_counts):]
            return start_index

        # consume Positionals and Optionals alternately, until we have
        # passed the last option string
        extras = []
        start_index = 0
        if option_string_indices:
            max_option_string_index = max(option_string_indices)
        else:
            max_option_string_index = -1
        while start_index <= max_option_string_index:

            # consume any Positionals preceding the next option
            next_option_string_index = min([
                index
                for index in option_string_indices
                if index >= start_index])
            if start_index != next_option_string_index:
                positionals_end_index = consume_positionals(start_index)

                # only try to parse the next optional if we didn't consume
                # the option string during the positionals parsing
                if positionals_end_index > start_index:
                    start_index = positionals_end_index
                    continue
                else:
                    start_index = positionals_end_index

            # if we consumed all the positionals we could and we're not
            # at the index of an option string, there were extra arguments
            if start_index not in option_string_indices:
                strings = arg_strings[start_index:next_option_string_index]
                extras.extend(strings)
                start_index = next_option_string_index

            # consume the next optional and any arguments for it
            start_index = consume_optional(start_index)

        # consume any positionals following the last Optional
        stop_index = consume_positionals(start_index)

        # if we didn't consume all the argument strings, there were extras
        extras.extend(arg_strings[stop_index:])

        # make sure all required actions were present and also convert
        # action defaults which were not given as arguments
        required_actions = []
        for action in self._actions:
            if action not in seen_actions:
                if action.required:
                    required_actions.append(self._get_action_name(action))
                else:
                    # Convert action default now instead of doing it before
                    # parsing arguments to avoid calling convert functions
                    # twice (which may fail) if the argument was given, but
                    # only if it was defined already in the namespace
                    if (action.default is not None and
                            isinstance(action.default, str) and
                            hasattr(namespace, action.dest) and
                            action.default is getattr(namespace, action.dest)):
                        setattr(namespace, action.dest,
                                self._get_value(action, action.default))

        if required_actions:
            self.error(_('the following arguments are required: %s') %
                       ', '.join(required_actions))

        # make sure all required groups had one option present
        for group in self._mutually_exclusive_groups:
            if group.required:
                # noinspection PyProtectedMember
                for action in group._group_actions:
                    if action in seen_non_default_actions:
                        break

                # if no actions were used, report the error
                else:
                    # noinspection PyProtectedMember
                    names = [self._get_action_name(action)
                             for action in group._group_actions
                             if action.help is not SUPPRESS]
                    msg = _('one of the arguments %s is required')
                    self.error(msg % ' '.join(names))

        # return the updated namespace and the extra arguments
        return namespace, extras

    @staticmethod
    def _check_if_jointed_short_option(action, option_string):
        if "Store" in action.__class__.__name__:
            if option_string[0] == PREFIX_CHAR_OF_OPTION:
                if option_string[1] != PREFIX_CHAR_OF_OPTION:
                    return True
        else:
            return False

    def _run_if_not_parsed(self, namespace, take_action, explicit_arg, arg_strings, action_tuples):
        for action, args, option_string in action_tuples:
            if isinstance(action, argparse._HelpAction):
                continue
            if hasattr(action, "parsed_currently") and action.parsed_currently is True:
                continue
            take_action(action, args, option_string)
            option_name = option_string.lstrip("-")
            if explicit_arg is None or f"{option_string}+{explicit_arg}" in arg_strings:
                if hasattr(namespace, option_name) and getattr(namespace, option_name) is not None:
                    registered_actions = self._registries["action"]
                    if not isinstance(action, (registered_actions["append"], registered_actions["extend"])):
                        action.parsed_currently = True

    def _get_values(self, action, arg_strings):
        """Almost same as super()._get_values.
        This differs only at line 43 rows below that runs '_get_value_for_subcommand'."""
        if action.nargs not in [PARSER, REMAINDER]:
            try:
                arg_strings.remove('--')
            except ValueError:
                pass

        if not arg_strings and action.nargs == OPTIONAL:
            if action.option_strings:
                value = action.const
            else:
                value = action.default
            if isinstance(value, str):
                value = self._get_value(action, value)
                self._check_value(action, value)

        elif (not arg_strings and action.nargs == ZERO_OR_MORE and
              not action.option_strings):
            if action.default is not None:
                value = action.default
            else:
                value = arg_strings
            self._check_value(action, value)

        elif len(arg_strings) == 1 and action.nargs in [None, OPTIONAL]:
            arg_string, = arg_strings
            value = self._get_value(action, arg_string)
            self._check_value(action, value)

        elif action.nargs == REMAINDER:
            value = [self._get_value(action, v) for v in arg_strings]

        elif action.nargs == PARSER:
            value = [self._get_value(action, v) for v in arg_strings]
            self._check_if_subcommand_included(action, value)  # modified from argparse

            # original is following.
            # self._check_value(action, value[0])

        elif action.nargs == SUPPRESS:
            value = SUPPRESS

        else:
            value = [self._get_value(action, v) for v in arg_strings]
            for v in value:
                self._check_value(action, v)

        return value

    def _check_if_subcommand_included(self, action, given_args: list):
        """Checks all given_args if subcommand is included or not.
        If not, raise SubCommandNotFound."""
        for arg in given_args:
            try:
                self._check_value(action, arg)
            except ArgumentError:
                continue
            else:
                return
        if action.choices:

            if isinstance(action.choices, dict):
                action_names = list(action.choices.keys())
            else:
                action_names = list(action.choices)
            msg = f"Failed to find subcommand {action_names} in args: {given_args}"
        else:
            msg = f"Valid value for {str(action)} is not found in value: {given_args}"
        raise _SubCommandNotFound(msg)

    def add_subparsers(self, *, title="subcommand", dest=None, parser_class=None, **kwargs):
        dest = dest or self.dest_name
        parser_class = parser_class or _SubCommand
        self.subparsers_action = super().add_subparsers(title=title, dest=dest, parser_class=parser_class, **kwargs)
        return self.subparsers_action


def initialize_parser(*args, add_help_argument=True, **kwargs):
    active_parser = _Parser.unique_instance
    if active_parser is not None:
        if isinstance(active_parser, _Parser):
            raise ValueError("Tried to initialize parser although it is already initialized."
                             "If you want to remake it, set_parser(None) first, then initialize again.")
        else:
            raise ValueError(f"Tried to initialize parser, but parser is already not None."
                             f"Something wrong happened. The type of parser is {type(active_parser)}.")
    else:
        if add_help_argument or kwargs.get("add_help") is True:
            add_help_argument = True
        else:
            add_help_argument = False
        _Parser.unique_instance = _Parser(*args, add_help=add_help_argument, **kwargs)
    return active_parser


def _auto_construct_parser(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if _Parser.unique_instance is None:
            initialize_parser()
        return func(*args, **kwargs)

    return wrapper


def clear_parser():
    _Parser.unique_instance = None


@functools.lru_cache()
def get_parser(*args, **kwargs):
    if _Parser.unique_instance is None:
        _Parser.unique_instance = _Parser.get_instance(*args, **kwargs)
    else:
        if args or kwargs:
            logger.warning(f"Instanced parser already exists, but you ran {get_parser.__name__} with {args, kwargs}."
                           f"This func returned the existing parser, and your {args} and {kwargs} were ignored.")
    return _Parser.unique_instance


@_auto_construct_parser
def parse(*args, is_flag=False, **kwargs):
    """alias of parser.parse"""
    return _Parser.unique_instance.parse(*args, is_flag=is_flag, **kwargs)


_Nargs = namedtuple("Nargs", "OPTIONAL ZERO_OR_MORE ONE_OR_MORE")
nargs = _Nargs(OPTIONAL=argparse.OPTIONAL, ZERO_OR_MORE=argparse.ZERO_OR_MORE, ONE_OR_MORE=argparse.ONE_OR_MORE)

_actions = (
   'STORE',
   'STORE_CONST',
   'STORE_TRUE',
   'STORE_FALSE',
   'APPEND',
   'APPEND_CONST',
   'COUNT',
   'HELP',
   'VERSION',
   'PARSERS',
   'EXTEND')
_Action = namedtuple("_Action", _actions)
action = _Action(**{name:name.lower() for name in _actions})


# noinspection PyUnresolvedReferences,PyProtectedMember
class _GroupForWith(argparse._ArgumentGroup):
    instances: list["_GroupForWith"] = []
    title_group_dict: dict[str:"_GroupForWith"] = {}

    def __enter__(self):
        _GroupForWith.instances.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _GroupForWith.instances.remove(self)


path_of_main: str = pathlib.Path(__main__.__file__).stem  # .py not included


def set_path_of_main(path_str:str):
    """path_str should not include .py usually."""
    global path_of_main
    path_of_main = path_str


@_auto_construct_parser
def get_group(title=None, description=None, is_mutual_exclusive=False, generates_auto_title=True):
    """
    title: Name of group to get or create newly.
    description: Sentence of instruction about the group.
    generates_auto_title: Boolean if title of this group should be named after the module name when title is None.
    """
    if title is None and generates_auto_title:
        current_frame = inspect.currentframe()
        current_file_name = current_frame.f_code.co_filename
        frame_of_caller = current_frame.f_back
        while frame_of_caller and current_file_name == frame_of_caller.f_code.co_filename:
            frame_of_caller = frame_of_caller.f_back
        else:
            if frame_of_caller is None:
                frame_of_caller = current_frame
        path_of_caller = pathlib.Path(frame_of_caller.f_code.co_filename)
        title = path_of_caller.stem
        name_of_main = path_of_main.stem if isinstance(path_of_main, pathlib.Path) else path_of_main
        if name_of_main == title:
            title = None

    if title is None:
        return None

    chosen_group = _GroupForWith.title_group_dict.get(title, None)

    if chosen_group is not None:
        return chosen_group

    group = _Parser.unique_instance.add_argument_group(title, description)
    _GroupForWith.title_group_dict[title] = group
    return group


# noinspection PyUnresolvedReferences,PyProtectedMember
class _SubCommand(_Parser, argparse._ActionsContainer):
    name_of_subcommand_group = "commands"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invoked = False

    def parse(self, *args, is_flag=False, **kwargs):
        main_parser = _Parser.unique_instance
        action = _Parser.add_argument(self, *args, is_flag=is_flag, **kwargs)
        namespace, _ = main_parser.parse_known_args()
        return getattr(namespace, action.dest)

    def _add_argument(self, *args, **kwargs):
        return ArgumentParser.add_argument(self, *args, **kwargs)

    def __bool__(self):
        return self.invoked

    def __enter__(self):
        raise AttributeError

    @classmethod
    def set_name_of_subcommand_group(cls, name: str):
        cls.name_of_subcommand_group = name

    @classmethod
    @_auto_construct_parser
    def create(cls, name, *, help=None, **kwargs):
        """Same arguments as ArgumentParser.subparsers.add_parser() are available for **kwargs."""
        active_parser = _Parser.unique_instance
        if not active_parser.subparsers_list:
            active_parser.add_subparsers(title=cls.name_of_subcommand_group)
        subcommand = active_parser.subparsers_action.add_parser(name, help=help, **kwargs)

        active_parser.subparsers_list.append(subcommand)
        try:
            namespace, _ = active_parser.parse_known_args()
        except _SubCommandNotFound:
            pass
        else:
            if hasattr(namespace, _Parser.SUBCOMMAND_DEST):
                given_subcommand = getattr(namespace, _Parser.SUBCOMMAND_DEST)
                if given_subcommand == name or given_subcommand is kwargs.get("dest", 0):
                    subcommand.invoked = True

        return subcommand


class _SubCommandNotFound(Exception):
    def __init__(self, message):
        self.message = message


def subcommand(name, *, help=None, **kwargs):
    return _SubCommand.create(name, help=help, **kwargs)


if __name__ == "__main__":
    # import __main__ as clappy

    def example():

        if not argv[1::]:
            args = "--foo --bar aiueo sub2 --sub2opt sample"
            argv[1::] = args.split(" ")

        with get_parser():
            bar = parse("--bar")
            print("--bar:", bar)
            sc1 = subcommand("sub1")
            sc2 = subcommand("sub2")
            opt = sc1.argument("--sub1opt")
            opt = sc2.argument("--sub2opt")
            print("opt:", opt)
            sc3 = subcommand("sub3")
            opt2 = sc3.argument("--sub3opt")
            print("opt2:", opt2)
            foo = parse("--foo", is_flag=True, help="heaaalp")
            print("--foo:", foo)

            # bar = parse("--bar")
            # print("--bar:", bar)
            print("withおわり\n")
        print("with後")

    example()

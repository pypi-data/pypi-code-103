from kntgen.constants import *
from kntgen.file_helpers import *
from kntgen.model.exception import *
from kntgen.pasteboard import *


def handle_base_parser(parser, args, supported_sources=SUPPORTED_SOURCES):
    """
    :param parser: parsers from [subcmd] package
    :param args: arguments from [subcmd] package, must include argument [--source] and [--path]
    :param supported_sources: Supported resources to handle
    :return: A tuple of (current args, content of the file which extracted from args, format of content)
    """
    extracted_args = parser.parse_args(args)
    source_type = None
    if extracted_args.source:
        source_type = extracted_args.source[0]
        if source_type not in supported_sources:
            parser.error(DefinedErrorMessage.ERROR_SUPPORT_SOURCE_INPUT)

    content_file = ''
    file_extension = ''
    if not source_type or source_type == SUPPORTED_SOURCES[0]:
        # Use [pasteboard] when [-s] is not defined
        content_file = pasteboard_read()
        if validate_json_content(content_file):
            file_extension = SUPPORTED_SOURCE_FORMAT[0]
        elif validate_yaml_content(content_file):
            file_extension = SUPPORTED_SOURCE_FORMAT[1]
    else:
        # Required file path when [-s] is [file]
        if not extracted_args.path:
            parser.error(DefinedCmd.Required.INPUT_FILE)
        file_path = extracted_args.path[0]
        if not os.path.exists(file_path):
            parser.error(DefinedErrorMessage.FILE_NOT_FOUND)
        file_extension = os.path.splitext(file_path)[1].removeprefix('.')
        if file_extension not in SUPPORTED_SOURCE_FORMAT:
            parser.error(DefinedErrorMessage.ERROR_SUPPORT_FORMAT)
        try:
            with open(file_path, 'r') as file:
                content_file = file.read()
        except (IOError, OSError) as e:
            DefinedErrorMessage.print_error(e)
            exit(1)

    if not file_extension or file_extension.isspace():
        parser.error(DefinedErrorMessage.ERROR_SUPPORT_FORMAT)
    return extracted_args, content_file, file_extension


def create_base_argument(parser,
                         description: str,
                         target: str,
                         supported_sources: list = None):
    parser.description = description
    parser.add_argument(
        '-s', '--source',
        nargs=1,
        choices=supported_sources or SUPPORTED_SOURCES,
        required=False,
        help=DefinedCmd.Argument.help_source(target)
    )
    parser.add_argument(
        '-p', '--path',
        nargs=1,
        required=False,
        help=DefinedCmd.Argument.help_path(target)
    )


def is_set(arg_name):
    if arg_name in sys.argv:
        return True
    return False

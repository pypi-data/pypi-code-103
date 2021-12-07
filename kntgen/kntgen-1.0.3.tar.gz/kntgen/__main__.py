# PYTHON_ARGCOMPLETE_OK
# -*- coding: UTF-8 -*-

from arghandler import subcmd, ArgumentHandler

from kntgen import __version__
from kntgen.bloc.bloc_cmd import BlocCommand
from kntgen.json_to_dart.json_cmd import JsonCommand
from kntgen.model.ui_config import UiConfig
from kntgen.network.network_cmd import NetworkCommand
from kntgen.parser_helpers import *
from kntgen.printer import *
from kntgen.ui.figma_ui_generator import FigmaUIGenerator


@subcmd('sample', help=DefinedCmd.HELP_CMD_SAMPLE)
def cmd_sample(parser, _, args):
    parser.description = DefinedCmd.HELP_CMD_SAMPLE
    parser.add_argument(
        'template',
        nargs=1,
        choices=SUPPORTED_TEMPLATES
    )
    parser.add_argument(
        '-e', '--extension',
        choices=SUPPORTED_SOURCE_FORMAT,
        nargs=1,
        required=False,
        help=DefinedCmd.Argument.HELP_EXTENSION
    )

    # Fetch arguments
    args = parser.parse_args(args)
    template = args.template[0]
    if template not in SUPPORTED_TEMPLATES:
        parser.error(DefinedErrorMessage.ERROR_SUPPORT_TEMPLATE)

    extension = SUPPORTED_SOURCE_FORMAT[0]
    if args.extension:
        extension = args.extension[0]
    if extension not in SUPPORTED_SOURCE_FORMAT:
        parser.error(DefinedErrorMessage.ERROR_SUPPORT_FORMAT)

    # Print the sample
    root = 'kntgen_templates'
    file_path = ''
    if template == SUPPORTED_TEMPLATES[0]:
        file_path = '/bloc/sample_input/sample_bloc'
    elif template == SUPPORTED_TEMPLATES[1]:
        file_path = '/json_to_dart/sample_input/sample'
    elif template == SUPPORTED_TEMPLATES[2]:
        file_path = '/network/sample_input/sample_network'
    elif template == SUPPORTED_TEMPLATES[3]:
        file_path = '/ui/sample_input/kntgen_config'
    file_path = root + file_path + '.' + extension
    try:
        # Open file depends on extension
        with open(file_path, 'r') as file:
            content_file = file.read()
        beauty_printer(title=f'Sample [{template}.{extension}] file',
                       content=[content_file],
                       content_has_block=False)
    except (IOError, OSError):
        print(DefinedErrorMessage.FILE_NOT_FOUND)
        exit(1)


@subcmd(SUPPORTED_TEMPLATES[0], help=DefinedCmd.HELP_CMD_BLOC)
def cmd_bloc(parser, _, args):
    create_base_argument(parser,
                         description=DefinedCmd.HELP_CMD_BLOC,
                         target='BLoC configuration')
    _, content_file, file_extension = handle_base_parser(parser, args)
    BlocCommand({}).create_files(content_file, file_extension)


@subcmd(SUPPORTED_TEMPLATES[1], help=DefinedCmd.HELP_CMD_MODEL)
def cmd_model(parser, _, args):
    parser.add_argument(
        'name',
        nargs=1,
        help=DefinedCmd.Argument.HELP_NAME_MODEL
    )
    create_base_argument(parser,
                         description=DefinedCmd.HELP_CMD_MODEL,
                         target='JSON')
    args, content_file, _ = handle_base_parser(parser, args)
    model_name = args.name[0]
    JsonCommand(model_name=model_name, options={}).create_files(content_file)


@subcmd(SUPPORTED_TEMPLATES[2], help=DefinedCmd.HELP_CMD_NETWORK)
def cmd_network(parser, _, args):
    parser.add_argument(
        '-a', '--append',
        required=False,
        action='store_true',
        help=DefinedCmd.Argument.HELP_APPEND_FILE
    )
    supported_sources = SUPPORTED_SOURCES.copy()
    supported_sources.append(POSTMAN_SOURCE)
    create_base_argument(parser,
                         description=DefinedCmd.HELP_CMD_NETWORK,
                         target='Restful API configuration',
                         supported_sources=supported_sources)
    extracted_args, content_file, file_extension = handle_base_parser(
        parser, args, supported_sources=supported_sources)
    has_append_option = is_set('-a') or is_set('--append')
    # Handle input Postman source
    source_type = extracted_args.source[0]
    if source_type == POSTMAN_SOURCE:
        file_extension = SUPPORTED_SOURCE_FORMAT[0]
        convert_folder = './kntgen'
        convert_file = 'network_config'
        convert_file_path = f'{convert_folder}/{convert_file}.{file_extension}'
        # Convert postman content into worked network form
        restful_service = NetworkCommand.convert_postman_to_generate_form(
            json.loads(content_file))
        generated_file_path, additional_info = create_json_file(
            restful_service.to_dict(),
            convert_file_path)
        generated_content = make_content_output_file(generated_file_path,
                                                     additional_info)
        beauty_printer(title='Successfully create network config file!',
                       content=[generated_content])
        # Save into a file and ask user to fill in
        info_printer(
            f'Please open file [{convert_file_path}] and fill required fields!')
        user_opt = input('Have you completed? (y/n)')
        if user_opt == 'y' or user_opt == 'Y':
            # Read network information from user edited file
            with open(convert_file_path, 'r', encoding='utf8') as edited_file:
                content_file = edited_file.read()
    # Start generating all related network files
    NetworkCommand({}).create_files(content_file,
                                    file_extension,
                                    has_append_option)


@subcmd(SUPPORTED_TEMPLATES[3], help=DefinedCmd.HELP_CMD_UI)
def cmd_ui(parser, _, args):
    parser.add_argument(
        '-c', '--component',
        nargs=1,
        choices=SUPPORTED_UI_COMPONENT,
        required=False,
        help=DefinedCmd.Argument.HELP_UI_COMPONENT
    )
    args = parser.parse_args(args)
    component = args.component[0] if args.component \
        else SUPPORTED_UI_COMPONENT[0]
    if component not in SUPPORTED_UI_COMPONENT:
        parser.error(DefinedErrorMessage.ERROR_SUPPORT_COMPONENT)

    # Firstly we check kntgen_config.yaml file to get configurations
    with open('./kntgen_config.yaml', 'r', encoding='utf8') as config_file:
        ui_config = UiConfig.from_yaml(config_file.read())

    # Then start parsing
    if component == SUPPORTED_UI_COMPONENT[6]:
        FigmaUIGenerator.translate_locale(
            folder=ui_config.assets.translations,
            pivot_locale=ui_config.google.translate.main_locale,
            placeholder=ui_config.google.translate.placeholder)
        return

    generator = FigmaUIGenerator(ui_config)
    if component == SUPPORTED_UI_COMPONENT[0]:
        generator.export_strings()
    elif component == SUPPORTED_UI_COMPONENT[1]:
        generator.export_colors()
    elif component == SUPPORTED_UI_COMPONENT[2]:
        generator.export_images()
    elif component == SUPPORTED_UI_COMPONENT[3]:
        generator.export_fonts()
    elif component == SUPPORTED_UI_COMPONENT[4]:
        generator.export_widgets()
    elif component == SUPPORTED_UI_COMPONENT[5]:
        generator.export_enum()


def main():
    handler = ArgumentHandler(
        use_subcommand_help=True,
        enable_autocompletion=True,
        epilog='Get help on a subcommand: kntgen subcommand -h'
    )

    handler.add_argument(
        '-v', '--version',
        action='version',
        version=__version__,
        help='show the version number'
    )

    # if no parameters are provided, show help
    if len(sys.argv) == 1:
        handler.run(['-h'])
    else:
        handler.run()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

"""
Latex suite entry script. Includes all argument definitions and the branching class to respective functions.
"""

import logging
import os
import sys
import time
from pathlib import Path

import yaml

import argparse as ap
import argcomplete

import latex_suite.bibliography as bibliography
from latex_suite.git import GitInteraction
from latex_suite import search_language_errors
from latex_suite import latex
from latex_suite import bash_print as bash
import latex_suite.util as util
from latex_suite.util import Configuration, filename_stem

CONF_FILE = "latex_suite.yaml"
LOG_FILE = "latex_suite.log"
NO_TEX_FOUND_WARNING = "No_compatible_tex_files_found"


# logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.INFO)
logging.basicConfig(filename=LOG_FILE, filemode="w",
                    format=f"[%(levelname)s][%(name)s]"
                           + f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] %(message)s")


class ArgumentParserExtensions:
    """
    Functions for use with the argument parser to parse arguments.
    """

    @staticmethod
    def is_valid_file(file_path, parser):
        """
        An ArgumentParser argument type to check if a file exists.

        Checks if the file with the given path exists. If the file does not exists or if the argument is
        the special value of :py:const:`~NO_TEX_FOUND_WARNING` calls a parser error.

        :param file_path: str
            A path to a file or :py:const:`~NO_TEX_FOUND_WARNING`.
        :param parser:
            The calling sub-parser for an error call if necessary.
        :return:
        str
            The value of file_path if it is an existing file.
        """
        if file_path == NO_TEX_FOUND_WARNING:
            parser.error("No compatible tex file found.")
        elif not os.path.isfile(file_path):
            parser.error(f"The file {file_path} does not exist!")
        else:
            return file_path

    @staticmethod
    def is_valid_directory(path, parser):
        """
        An ArgumentParser argument type to check if a directory exists.

        Checks if the directory with the given path exists. If the directory does not exists calls a parser error.

        :param path: str
            A directory path.
        :param parser:
            The calling sub-parser for an error call if necessary.
        :return:
        str
            The value of path if it is an existing file.
        """
        path = os.path.expanduser(path)
        if not os.path.isdir(path):
            parser.error(f"The folder {path} does not exist!")
        else:
            return path


def make_pdf_with_substitute_defaults(file_to_translate, num_compile_attempts,
                                      verbose=False, do_bib=False, do_single_run=False):
    """
    Translate a pdf using the default pdf engine and bib engine.

    :param file_to_translate:
        the tex file to translate.
    :param num_compile_attempts: int
        The maximal number of attempts to try to pass past a latex translation error.
    :param verbose: bool
        If True print processing.
    :param do_bib: bool
        If True processes the citations with the citation engine.
    :param do_single_run: bool
        If True and do_bib is False one translation of the tex file.
        If True and do_bib is True: tex translation, citation processing, tex translation.
    :return: LatexBashCompileResult
        The compile result of the last compile with the outcome, output and number of errors and warnings.
        If the bibliography was processed the bib processing information is included.
    """
    engine = Configuration.get_config().engine
    bib_engine = Configuration.get_config().bib_engine
    result = latex.make_pdf(file_to_translate, engine, bib_engine,
                            max_end_attempts=num_compile_attempts,
                            verbose=verbose, do_bib=do_bib, do_single_run=do_single_run)
    return result


def load_settings():
    """
    Load the configuration or applies defaults.

    If a yaml configuration is found the file is loaded and used to initiate the configuration. If
    no file is found all default values are used.
    :return: Configuration
        The configuration.
    """
    loaded_config = None
    if os.path.isfile(CONF_FILE):
        with open(CONF_FILE, "r") as conf_file:
            yaml.SafeLoader.add_multi_constructor("ErrorList", search_language_errors.ErrorList.from_yaml)
            loaded_config = yaml.safe_load(conf_file)
    return Configuration(loaded_config)


def compile_one_tex(tex_file, do_bib, is_verbose, num_compile_attempts):
    """
    Compile on tex file.

    If the tex file could not be found or not compiled the program will exit.

    :param tex_file:
        The path of the tex file.
    :param do_bib: bool
        If True processes the citations with the citation engine.
    :param is_verbose: bool
        If True print processing.
    :param num_compile_attempts: int
        The maximal number of attempts to try to pass past a latex translation error.
    """
    compile_result = make_pdf_with_substitute_defaults(tex_file,
                                                       num_compile_attempts=num_compile_attempts,
                                                       verbose=is_verbose, do_bib=do_bib)
    if compile_result.outcome == latex.Outcome.ABORTED:
        bash.print_error("Failed to compile tex file '" + str(tex_file) + "'.")
        sys.exit(1)
    elif compile_result.outcome == latex.Outcome.FILE_NOT_FOUND:
        bash.print_error("Tex file to compile '" + str(tex_file) + "' not found.")
        sys.exit(2)


def task_write_conf(parsed_args):
    """
    Creates a config file with the default configuration in the current directory.

    :param parsed_args:
        Arguments from the command line.
    """

    force_creation = parsed_args["f"]
    if not force_creation and os.path.isfile(CONF_FILE):
        bash.print_error(f"Config file '{CONF_FILE}' already exists. If you want to override it please specify the"
                         + f" force action flag '-f'.")
    else:
        Configuration.write_default(CONF_FILE)


def task_clean_up(parsed_args):
    """
    Removes all files with file extensions in the clean up list.

    :param parsed_args: dict
        The parameter from the arg parser.
    """
    file_extensions = Configuration.get_config().clean_extensions
    depth = parsed_args["d"]
    list_only = parsed_args["l"]
    force_remove = parsed_args["f"]
    num_files, num_files_removed = util.remove_files(file_extensions, directory=".", depth=depth,
                                                     only_list=list_only, force_remove=force_remove)
    if list_only:
        print(f"Found {num_files} file(s).")
    else:
        print(f"Removed {num_files_removed} of {num_files} file(s).")


def task_git(parsed_args):
    """
    Initiates a git related action as specified by the args.

    :param parsed_args:dict
        The parameter from the arg parser.
    """
    action = parsed_args["action"]
    if action == "ignore":
        if not os.path.isfile(".gitignore"):
            gitignore_file = Path(".gitignore")
            gitignore_file.touch()
        extensions_with_wildcard = ["*" + extension for extension in Configuration.get_config().clean_extensions]
        util.add_files_and_extensions_to_file(extensions_with_wildcard, ".gitignore")
    elif action == "credentialUsername":
        username = parsed_args["username"]
        set_username_parameter = GitInteraction.get_git_config_credential_set_username_parameter_string(username)
        errors = GitInteraction.execute_bash_git_cmd(GitInteraction.CONFIG, set_username_parameter)
        if errors is not None:
            sys.exit(errors)


def task_make_bib_file(parsed_args):
    """
    Creates a bib file under the specifications of the cmd args.

    :param parsed_args: dict
        The parameter from the arg parser.
    """
    aux_file_path = parsed_args["auxFile"]
    bib_folder_path = parsed_args["bibsFolder"]
    out_file_path = parsed_args["output"]
    bib_fields_to_remove = Configuration.get_config().bibliography_fields_to_remove
    errors = bibliography.create_bib_file(aux_file_path, bib_folder_path, out_file_path, bib_fields_to_remove)
    for one_error in errors:
        bash.print_error(str(one_error))


def task_lang_command(parsed_args):
    """
    Searches for textual language error in a file as specified by the cmd args.

    :param parsed_args:dict
        The parameter from the arg parser.
    """
    file_to_check = parsed_args["file"]
    exclude = None
    if any(identifier in parsed_args for identifier in Configuration.get_config().language_errors.identifiers):
        exclude = []
        for identifier in Configuration.get_config().language_errors.identifiers:
            if identifier in parsed_args and parsed_args[identifier]:
                exclude.append(identifier)
    all_errors = Configuration.get_config().language_errors
    errors = search_language_errors.filter_errors_list(all_errors, exclude)
    found_errors = search_language_errors.check_for_error_and_print(file_to_check, errors)
    for i in found_errors.keys():
        errors_in_line = found_errors[i]
        print("Errors in line " + str(i))
        for one_error in errors_in_line:
            print(one_error)


def task_make(parsed_args, compilable_tex_files):
    """
    Compile one or more tex files under the specifications of the cmd args.

    Exists with exit code 1 if one or more tex files could not be translated.

    :param parsed_args: dict
        The parameter from the arg parser.
    :param compilable_tex_files:
        List of tex files that can be compiled.
    """
    is_verbose = parsed_args["verbose"]
    do_bib = parsed_args["bib"]
    do_produce_status_list = parsed_args["listStatus"]
    num_compile_attempts = parsed_args["number"]
    if parsed_args["all"]:
        if parsed_args["texfile"] != filename_stem(Configuration.get_config().main_tex):
            bash.print_warning("Tex file (" + str(parsed_args["texfile"]) + ")"
                               + " and --all specified. Tex file will be ignored.")
        all_compile_results = []
        for one_tex_file in compilable_tex_files:
            one_compile_result = make_pdf_with_substitute_defaults(one_tex_file,
                                                                   num_compile_attempts=num_compile_attempts,
                                                                   verbose=is_verbose,
                                                                   do_bib=do_bib)
            all_compile_results.append(one_compile_result)
            if do_produce_status_list:
                status = bash.Status.UNKNOWN
                status_message = None
                if one_compile_result.outcome == latex.Outcome.SUCCESS:
                    status = bash.Status.SUCCESS
                elif one_compile_result.outcome == latex.Outcome.ABORTED:
                    status = bash.Status.ERROR
                    status_message = "ABORTED"
                elif one_compile_result.outcome == latex.Outcome.FAILURE:
                    status = bash.Status.ERROR
                bash.print_status(one_tex_file, status, status_message)

        failed_compiles = [one_compile_result.filename for one_compile_result in all_compile_results
                           if one_compile_result.outcome != latex.Outcome.SUCCESS]
        num_fail_compile = len(failed_compiles)
        if num_fail_compile > 0:
            failed_compiles_list = ""
            for one_failed_compile in failed_compiles:
                failed_compiles_list += "\t- " + one_failed_compile + "\n"
            distance_to_previous_print = ""
            if is_verbose or do_produce_status_list:
                distance_to_previous_print += "\n"
            bash.print_error(distance_to_previous_print
                             + "Failed to compile all files. "
                             + str(num_fail_compile) + "/" + str(len(compilable_tex_files))
                             + " could not be compiled.\n" + failed_compiles_list[:-1])
            sys.exit(1)
    else:
        tex_file = parsed_args["texfile"] + ".tex"
        compile_one_tex(tex_file, do_bib=do_bib, is_verbose=is_verbose, num_compile_attempts=num_compile_attempts)


def task_free_compile_cmake(parsed_args):
    """
    Compile a tex files under the specifications of the cmd args.

    :param parsed_args:dict
        The parameter from the arg parser.
    """
    is_verbose = parsed_args["verbose"]
    do_bib = parsed_args["bib"]
    tex_file = parsed_args["maintex"]
    num_compile_attempts = parsed_args["number"]
    compile_one_tex(tex_file, do_bib=do_bib, is_verbose=is_verbose, num_compile_attempts=num_compile_attempts)


def select_task(parsed_args, compilable_tex_files):
    """
    Calls the respective function for the task as specified by the cmd args.

    :param parsed_args:dict
        The parameter from the arg parser.
    :param compilable_tex_files: list
         Individually compilable tex files in the current directory.
    """
    task = parsed_args["task"]
    if task == "make":
        task_make(parsed_args, compilable_tex_files)
    if task == "cmake":
        task_free_compile_cmake(parsed_args)
    elif task == "lang":
        task_lang_command(parsed_args)
    elif task == "conf":
        task_write_conf(parsed_args)
    elif task == "bibfile":
        task_make_bib_file(parsed_args)
    elif task == "clean":
        task_clean_up(parsed_args)
    elif task == "git":
        task_git(parsed_args)


def main():
    """
    Main entry of program. Set arguments for argument parser, loads the settings and
    searches current directory for compilable tex files. At the end prints help or calls
    the task selector function to perform one of the tasks.
    """
    parser = ap.ArgumentParser()
    root_logger = logging.getLogger()
    root_logger.handlers.append(logging.StreamHandler(sys.stdout))
    config = load_settings()
    if not config.log_to_console:
        logging.getLogger().removeHandler(logging.getLogger().handlers[1])
    compilable_tex_files = util.find_compilable_tex(".")
    if config.main_tex not in compilable_tex_files:
        compilable_tex_files.append(config.main_tex)
    compilable_tex_files_names = [os.path.splitext(f)[0] for f in compilable_tex_files]
    if len(compilable_tex_files_names) == 0:
        compilable_tex_files_names.append(NO_TEX_FOUND_WARNING)
    # Reusable arguments
    parent_with_tex_file = ap.ArgumentParser(add_help=False)
    parent_with_tex_file.add_argument("--maintex",
                                      type=lambda x: ArgumentParserExtensions.is_valid_file(x, parent_with_tex_file),
                                      default=config.main_tex,
                                      help="Specify main tex file")
    parent_with_bib = ap.ArgumentParser(add_help=False)
    parent_with_bib.add_argument("-b", "--bib", action="store_const", const=True, default=False,
                                 help="Compile bibliography.")
    parent_force_action = ap.ArgumentParser(add_help=False)
    parent_force_action.add_argument("-f",
                                     action="store_true",
                                     help="Force action "
                                          + "(do not ask for confirmation when overwriting or deleting files).")
    verbose_print = ap.ArgumentParser(add_help=False)
    verbose_print.add_argument('-v', '--verbose', action="store_const", const=True, default=False,
                               help="Activate verbose mode.")
    parent_number_ignore_latex_error = ap.ArgumentParser(add_help=False)
    parent_number_ignore_latex_error.add_argument('-n', '--number', type=int,
                                                  default=config.number_ignore_latex_compile_errors,
                                                  help="The number of attempts to ignore latex errors.")
    # Parsers for tasks
    task_parsers = parser.add_subparsers(dest='task')
    # Make config file
    # write_conf_parser =
    task_parsers.add_parser('conf',
                            parents=[parent_force_action],
                            help=f"Create configuration file ({CONF_FILE}).")
    # Language check
    lang_check_parser = task_parsers.add_parser('lang', help='Search for language errors.')
    lang_check_parser.add_argument("file",
                                   type=lambda x: ArgumentParserExtensions.is_valid_file(x, lang_check_parser),
                                   help="File to check for language errors.")
    error_identifiers = config.language_errors.identifiers
    if len(error_identifiers) > 0 and len(error_identifiers) != len(set(error_identifiers)):
        logging.warning("Multiple text errors with the same identifier.")
    for one_error_identifier in set(error_identifiers):
        associated_error_message = config.language_errors.get_error_for_identifier(one_error_identifier).error_message
        help_message = f"Exclude error: {associated_error_message}."
        lang_check_parser.add_argument(f"--{one_error_identifier.strip()}",
                                       action="store_const", const=True, default=False,
                                       help=help_message)
    # Free make pdf
    # make_parser =
    task_parsers.add_parser('cmake',
                            parents=[parent_with_tex_file, parent_with_bib, verbose_print,
                                     parent_number_ignore_latex_error],
                            help='Translate document.')
    # Make pdf
    make_compile_parser = task_parsers.add_parser('make',
                                                  parents=[parent_with_bib, verbose_print,
                                                           parent_number_ignore_latex_error],
                                                  help='Translate document.')
    make_compile_parser.add_argument("texfile",
                                     nargs="?",
                                     default=filename_stem(config.main_tex),
                                     choices=compilable_tex_files_names,
                                     help="File to compile.")
    make_compile_parser.add_argument("--all", action="store_const", const=True, default=False,
                                     help="Translate all independent tex files in the directory.")
    make_compile_parser.add_argument("-l", "--listStatus", action="store_const", const=True, default=False,
                                     help="Produce a list of all compile outcomes.")
    # Clean
    clean_parser = task_parsers.add_parser('clean',
                                           parents=[parent_force_action],
                                           help='Cleans the directory.')
    clean_parser.add_argument("-d", type=int, default=config.clean_depth,
                              help="Set the maximal depth into sub-folders for looking for files to delete.")
    clean_parser.add_argument("-l", action="store_const", const=True, default=False,
                              help="Only list files and do not delete.")
    # Make bibliography file
    make_bib_file = task_parsers.add_parser('bibfile',
                                            parents=[parent_force_action],
                                            help='Create bib file from citations in aux file.')
    make_bib_file.add_argument("-a", "--auxFile",
                               type=lambda x: ArgumentParserExtensions.is_valid_file(x, make_bib_file),
                               default=config.main_aux,
                               help="The aux file.")
    make_bib_file.add_argument("-b", "--bibsFolder",
                               type=lambda x: ArgumentParserExtensions.is_valid_directory(x, make_bib_file),
                               default=config.bibs_folder,
                               help="The path to the folder containing the bib files to search for entries.")
    make_bib_file.add_argument("-o", "--output", type=str,
                               default=config.main_bibliography_file,
                               help="The file to write the bibliography entries into.")
    # Git help
    git_parser = task_parsers.add_parser("git",
                                         help="Help with git related operations.")
    git_action_parsers = git_parser.add_subparsers(dest='action')
    git_action_parsers.add_parser("ignore",
                                  help="Add default clean extensions to gitignore.")
    credentials_parser = git_action_parsers.add_parser("credentialUsername",
                                                       help="Add credential username to local git.")
    credentials_parser.add_argument("username",
                                    type=str,
                                    help="The username to use.")
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    args = vars(args)
    if args["task"] is not None:
        select_task(args, compilable_tex_files)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

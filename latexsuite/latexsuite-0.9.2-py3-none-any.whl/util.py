"""
Some utility functions for the configuration of the suite and file operations.
"""

import os
import re

import yaml

from latex_suite.search_language_errors import TextErrorType, ErrorList


FILE_EXTENSION_PATTERN = re.compile(r"\*\.[a-zA-Z0-9]+")
DOCUMENT_CLASS_NOT_IN_COMMENT_PATTER = re.compile(r"[ a-zA-Z0-9_]*%[ a-zA-Z0-9_]*\\documentclass[ a-zA-Z0-9_]*")

not_working_errors = [
    TextErrorType("No text between sections.",
                  r"(section|chapter|paragraph){[\w\" \",:]+}[\n\" \"\t]+"
                  + r"(\\label{[\w\" \",:]*})*[\n\" \"\t]+\\(sub)*(section|paragraph)")
    ]

verbose_errors = [
    TextErrorType("Capital in sentence.", r"[a-zA-z0-9_\(\)\[\]\{\}:]\ [A-Z]")
    ]


class Configuration:
    """
    Configuration for standard options.
    """

    engine: str
    bib_engine: str
    main_tex: str
    clean_extensions: list[str]
    clean_depth: int
    bibs_folder: str
    main_bibliography_file: str
    bibliography_fields_to_remove: list[str]
    number_ignore_latex_compile_errors: int
    language_errors: ErrorList
    log_to_console: bool

    DEFAULT_CONF = {
        "engine": ("engine", "pdflatex"),
        "bib_engine": ("bib_engine", "biber"),
        "main_tex": ("main_tex", "main.tex"),
        "clean_extensions": ("clean_file_extensions", [".log", ".aux", ".bbl", ".blg"]),
        "clean_depth": ("clean_depth", 0),
        "bibs_folder": ("bib_files_folder", "."),
        "main_bibliography_file": ("main_bibliography_file", "bibliography.bib"),
        "bibliography_fields_to_remove": ("bibliography_fields_to_remove", ["abstract", "file", "keywords", "url"]),
        "number_ignore_latex_compile_errors": ("number_ignore_latex_compile_errors", 1),
        "log_to_console": ("log_to_console", False),
        "language_errors": ("language_errors",
                            ErrorList([
                                TextErrorType("'An' not in front of vowel.", r"[\.\ ][aA]n\ [^aeiouAEIOU]"),
                                TextErrorType("'A' in front of vowel.", r"[\.\ ][aA]\ [aeiouAEIOU]"),
                                TextErrorType("Extra space.", r"[^\ \n%][\ ]{2,}[^\ \n]"),
                                TextErrorType("Named reference with lower case",
                                              r"\b[a-z]\w*\b[\ ~]\\ref\{", ["and", "to"], " |~"),
                                TextErrorType("Doubled word.", r"\b(\w+)\s+\1\b"),
                                TextErrorType("Citation with name and not shortcite",
                                              r"(\b)( et al.){1}~\\cite\{ref:\1", identifier="sc"),
                                TextErrorType("Every sentence in a line",
                                              r"[^iegst0-9\"al\"]\.[^\n]*\.", identifier="spl")]))
    }
    IDX_TAG = 0
    IDX_VALUE = 1

    _instance = None

    def __init__(self, loaded_yaml=None):
        """
        Constructor that uses the yaml config file contents to set the configuration and sets anything that is
        not specified to a default value.
        :param loaded_yaml:
        """
        if loaded_yaml is None:
            loaded_yaml = {}
        self._set_default()
        for one_key in self.DEFAULT_CONF.keys():
            one_tag = self.DEFAULT_CONF[one_key][self.IDX_TAG]
            if one_tag in loaded_yaml:
                internal_key = "_" + one_key
                self.__setattr__(internal_key, loaded_yaml[one_tag])

    def __new__(cls, *args, **kwargs):
        """
        Ensures that there is only one resource class.
        """

        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
        return cls._instance

    def _set_default(self):
        """
        Set all known settings to default.
        """
        for one_key in self.DEFAULT_CONF.keys():
            internal_key = "_" + one_key
            self.__setattr__(internal_key, self.DEFAULT_CONF[one_key][self.IDX_VALUE])

    def __getattribute__(self, item):
        """
        If the key is a default setting retrieve that entry otherwise call super.
        :param item:
        :return:
        """
        if item != "DEFAULT_CONF" and item in self.DEFAULT_CONF.keys():
            value = self._get_conf_value(item)
        else:
            value = super().__getattribute__(item)
        return value

    def __setattr__(self, key, value):
        """
        If the key is a default setting raise AttributeError since these cannot be changed; otherwise call super.
        :param key:
        :param value:
        :return:
        """
        if key != "DEFAULT_CONF" and key in self.DEFAULT_CONF.keys():
            raise AttributeError("can't set attribute")
        else:
            super().__setattr__(key, value)

    @classmethod
    def get_config(cls):
        """
        :return: Configuration
        The configuration if it has been initialised before and None otherwise.
        """
        return cls._instance

    def _get_conf_value(self, key):
        """
        Property step in for configuration settings.
        :param key:
        :return:
        """
        value = self.__getattribute__("_" + key)
        return value

    @property
    def main_aux(self):
        """
        The aux file associated with the main tex file.
        :return:
        str
            '<main tex file name without extension>.aux'
        """
        return filename_stem(self.main_tex) + ".aux"

    @staticmethod
    def write_default(file):
        """
        Write the default configuration to a yaml file.
        :param file:
        The path of the file to write to.
        """
        default_config = {}
        for one_key in Configuration.DEFAULT_CONF:
            tag = Configuration.DEFAULT_CONF[one_key][Configuration.IDX_TAG]
            value = Configuration.DEFAULT_CONF[one_key][Configuration.IDX_VALUE]
            default_config[tag] = value
        yaml.Dumper.add_multi_representer(ErrorList, ErrorList.to_yaml)
        with open(file, "w") as config_file:
            yaml.dump(default_config, config_file)


def remove_files(file_extensions, directory=None, depth=0, only_list=False, force_remove=False):
    """
    Removes all files with matching file extensions.

    :param file_extensions: [str]
        The list of file extensions (including dot (.)), e.g. [".log"]
    :param directory:
        The root directory to start the delete process.
    :param depth: int
        The recursion depth to go to for deleting files. 0 means only the directory, 1 includes the subdirectories,
        2 includes the subdirectories of the subdirectories and so on.
    :param only_list:
        Does not delete the files. Only list them.
    :param force_remove:
        Just removes the files without prompting for input.
    """

    num_files = 0
    num_files_removed = 0
    if directory is None:
        directory = "."
    for dir_entry in os.listdir(directory):
        dir_entry_path = os.path.join(directory, dir_entry)
        if os.path.isfile(dir_entry_path):
            if filename_extension(dir_entry) in file_extensions:
                num_files += 1
                if only_list:
                    print(dir_entry_path)
                else:
                    response = None
                    if force_remove:
                        response = "y"
                    while response is None or (response != "y" and response != "n"):
                        text = f"Please enter 'y' or 'n' to remove or not remove '{dir_entry_path}', respectively:"
                        if response is None:
                            text = f"Do you want to remove '{dir_entry_path}? y/n:"
                        response = input(text)
                    if response == "y":
                        print("Removing '" + str(str(dir_entry_path)) + "'.")
                        os.remove(dir_entry_path)
                        num_files_removed += 1
        elif os.path.isdir(dir_entry_path) and depth > 0:
            num_files_sub_dirs, num_files_removed_sub_dirs = remove_files(file_extensions, dir_entry_path,
                                                                          depth=depth-1, only_list=only_list,
                                                                          force_remove=force_remove)
            num_files += num_files_sub_dirs
            num_files_removed += num_files_removed_sub_dirs
    return num_files, num_files_removed


def find_compilable_tex(directory_path):
    """
    Find tex files that can be compiled on their own.

    A text file is considered compilable on its own if the file extension is tex and if the first
    non comment line contains a \\documentclass command.
    :param directory_path:
        The directory to look for compilable tex files.
    :return:
    [str]
        List of relative paths of files which are compilable.
    """
    tex_files = [f for f in os.listdir(directory_path)
                 if os.path.isfile(os.path.join(directory_path, f))
                 and os.path.splitext(f)[1] == ".tex"]
    compilable_tex_files = []
    for one_tex_file in tex_files:
        with open(one_tex_file, "r") as tex_file:
            continue_searching = True
            while continue_searching:
                try:
                    line = next(tex_file)
                except StopIteration:
                    continue_searching = False
                    line = "EOF"
                if "\\documentclass" in line and not DOCUMENT_CLASS_NOT_IN_COMMENT_PATTER.search(line):
                    compilable_tex_files.append(one_tex_file)
                if (not ("\\documentclass" in line and not DOCUMENT_CLASS_NOT_IN_COMMENT_PATTER.search(line)
                         or "".join(line.split()).startswith("%")
                         or len("".join(line.split())) == 0)):
                    continue_searching = False
    return compilable_tex_files


def add_files_and_extensions_to_file(all_patters_to_add, path):
    """
    Adds all file patterns to the file in path.

    File extension patterns are appended to the longest list of file extension
    patterns or the end of the file. All other patterns are added to the end of the
    file. The list of patterns does not need newlines these are added in. The patterns
    can be files or file extension, e.g. ['*.jpg', 'some.pdf'].

    :param all_patters_to_add: [str]
        The list of patterns.
    :param path: str
        The path to the file.
    """

    with open(path, "r") as file:
        lines = file.readlines()
    all_contents = "".join(lines)
    extension_insert_location = find_file_extension_insert_location(lines)
    file_extension_matcher = re.compile(FILE_EXTENSION_PATTERN)
    for one_pattern_to_add in all_patters_to_add:
        if one_pattern_to_add not in all_contents:
            if file_extension_matcher.match(one_pattern_to_add):
                lines.insert(extension_insert_location, one_pattern_to_add + "\n")
                extension_insert_location += 1
            else:
                lines.insert(len(lines), one_pattern_to_add + "\n")
                if extension_insert_location == len(lines):
                    extension_insert_location += 1
    with open(path, "w") as f:
        contents = "".join(lines)
        f.write(contents)


def find_file_extension_insert_location(lines):
    """
    Find the longest sequence of lines containing file extension entries and choose the end
    of this as the insertion location. If there are no file extension lines returns end of file
    as index.
    :param lines: [str]
        The file as a list of lines.
    :return: int
        The index after the longest sequence or the end of file (len of lines list).
    """

    insert_location = len(lines)
    current_sequence_length = -1
    longest_sequence_length = 0
    file_extension_matcher = re.compile(FILE_EXTENSION_PATTERN)
    for i in range(len(lines)):
        one_line = lines[i]
        if file_extension_matcher.match(one_line):
            if current_sequence_length > 0:
                current_sequence_length += 1
            else:
                current_sequence_length = 1
        elif current_sequence_length > 0:
            if current_sequence_length > longest_sequence_length:
                insert_location = i
                longest_sequence_length = current_sequence_length
            current_sequence_length = -1
    return insert_location


def filename_stem(filename):
    """
    Returns the name of the file without the file extension.
    :param filename: The full name of the file with file extension.
    :return: str
        The name of the file.
    """

    return os.path.splitext(filename)[0]


def filename_extension(filename):
    """
    Returns the file extension of the file.
    :param filename: The full name of the file with file extension.
    :return: str
        The file extension.
    """

    return os.path.splitext(filename)[1]

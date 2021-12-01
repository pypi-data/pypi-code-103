"""
Search for common language errors in a file that can be determined via regex.
"""

import logging
import re


logger = logging.getLogger(__name__)


class ErrorList:
    """
    Class that represent a list of text errors.
    """

    def __init__(self, list_of_errors=None):
        if list_of_errors is None:
            self._errors = []
        else:
            self._errors = list_of_errors

    def __len__(self):
        return len(self._errors)

    def __getitem__(self, i):
        return self._errors[i]

    def __delitem__(self, i):
        del self._errors[i]

    def __setitem__(self, i, val):
        self._errors[i] = val

    def __str__(self):
        return str(self._errors)

    def __repr__(self):
        str_repr = [(e.error_message, e.regex, e.exclude_beginning_words, e.split_characters, e.identifier)
                    for e in self._errors]
        return str_repr

    @property
    def errors(self):
        """
        :return: list
        A list of the errors.
        """
        return self._errors

    @property
    def identifiers(self):
        """
        :return: [str]
        List of all non None error identifiers.
        """
        identifier_list = [e.identifier for e in self._errors if e.identifier is not None]
        return identifier_list

    def get_error_for_identifier(self, identifier):
        """
        Returns the text errors with the specified identifier
        :param identifier: str
        The identifier to search for.
        :return: TextErrorType
        The error if an error with the identifier exists. Otherwise None.
        """
        found_error = next((e for e in self._errors if e.identifier == identifier), None)
        return found_error

    @classmethod
    def to_yaml(cls, dumper, data):
        """
        Transform an object of ErrorList into a MappingNode from a list containing all the TextErrorTypes
        transformed into dicts.

        :param dumper:
        :param data: ErrorList
        The ErrorList object.
        :return: MappingNode
        The mapping node from the dict of the object.
        """
        error_list = []
        for one_error in data.errors:
            one_error_as_dict = {"message": one_error.error_message,
                                 "regex": one_error.regex.pattern}
            if len(one_error.exclude_beginning_words) > 0:
                one_error_as_dict["exclude_words"] = one_error.exclude_beginning_words
            if one_error.split_characters != " ":
                one_error_as_dict["split_character"] = one_error.split_characters
            if one_error.identifier is not None:
                one_error_as_dict["identifier"] = one_error.identifier
            error_list.append(one_error_as_dict)
        return dumper.represent_mapping("ErrorList", {"errors": error_list})

    @classmethod
    def from_yaml(cls, loader, _, data):
        """
        A MappingNode representing a ErrorList to an ErrorList.

        :param loader:
        :param _:
        :param data: MappingNode
        The MappingNode.
        :return:
        An instance of ErrorList.
        """
        error_list = []
        try:
            list_of_errors_as_nodes = data.value[0][1].value
        except TypeError:
            logger.error("Structural error in language_errors. No errors loaded.")
            list_of_errors_as_nodes = []
        for one_error_node in list_of_errors_as_nodes:
            error_as_dict = loader.construct_mapping(one_error_node)
            if "message" in error_as_dict and "regex" in error_as_dict:
                error_constructor_args = {"error_message": error_as_dict["message"], "regex": error_as_dict["regex"]}
                keys_to_include_if_possible = [("exclude_words", "exclude_beginning_words"),
                                               ("split_character", "split_characters"),
                                               ("identifier", "identifier")]
                for yaml_dict_key, param_name in keys_to_include_if_possible:
                    if yaml_dict_key in error_as_dict:
                        error_constructor_args[param_name] = error_as_dict[yaml_dict_key]
                error_list.append(TextErrorType(**error_constructor_args))
            else:
                warn_message = "A text error could not be loaded."
                if "message" in error_as_dict:
                    warn_message += f" Message '{error_as_dict['message']}'."
                else:
                    warn_message += " Message missing."
                if "regex" in error_as_dict:
                    warn_message += f" Regex '{error_as_dict['regex']}'."
                else:
                    warn_message += " Regex missing."
                logger.error(warn_message)
        return cls(error_list)

    def insert(self, i, val):
        self._errors.insert(i, val)

    def append(self, val):
        self.insert(len(self._errors), val)


class TextErrorType:
    """
    A type of textual error that can be found with a regex.
    """

    def __init__(self, error_message, regex, exclude_beginning_words=None, split_characters=" ", identifier=None):
        """
        Constructor.

        :param error_message: str
        The message for this error.
        :param regex: raw str
        The regex for this error.
        :param exclude_beginning_words: [str]
        List of match's first words for which to ignore match.
        :param split_characters: str
        The character to spit a match to determine the first word.
        :param identifier: str
        A string to identify the error with.
        """
        self.regex = re.compile(regex)
        self.error_message = error_message
        if exclude_beginning_words is None:
            self.exclude_beginning_words = []
        else:
            self.exclude_beginning_words = exclude_beginning_words
        self.split_characters = split_characters
        self.identifier = identifier

    def check_for_error(self, text):
        """
        Search for an occurrence of the error (regex) in the text.

        :param text: str
            The text to search in.
        :return:
        TextErrorOccurrence or None
            None if no error found or the (first) occurrence of the error.
        """
        check_result = self.regex.search(text)
        error = None
        if check_result:
            occurrence_start_idx = check_result.start()
            occurrence_end_idx = check_result.end()
            error = TextErrorOccurrence(text, self, occurrence_start_idx, occurrence_end_idx)
            text_split_at_space = re.split(self.split_characters, error.get_matched_text())
            first_word = text_split_at_space.pop(0)
            if first_word in self.exclude_beginning_words:
                error = None
        return error


class TextErrorOccurrence:
    """
    Information on an error occurrence in a text.
    """

    def __init__(self, text, error_type, start_idx_in_text, end_idx_in_text):
        self.error_type = error_type
        self.text = text
        self.start_idx_in_text = start_idx_in_text
        self.end_idx_in_text = end_idx_in_text

    def get_matched_text(self):
        """
        The substring that was found to contain the error.
        :return:
        str
            The substring.
        """
        last_space_before_occurrence = self.last_space_before_occurrence()
        if last_space_before_occurrence == -1:
            last_space_before_occurrence = 0
        else:
            last_space_before_occurrence += 1
        first_space_after_occurrence = self.first_space_after_occurrence()
        if first_space_after_occurrence == -1:
            first_space_after_occurrence = len(self.text) - 1
        matched_text = self.text[last_space_before_occurrence:first_space_after_occurrence]
        return matched_text

    def last_space_before_occurrence(self):
        """
        The index of the last space before the substring where the error occurred.
        :return:
        int
            The index.
        """
        return self.text.rfind(" ", 0, self.start_idx_in_text)

    def first_space_after_occurrence(self):
        """
        The index of the first space after the substring where the error occurred.
        :return:
        int
            The index.
        """
        return self.text.find(" ", self.end_idx_in_text)

    def __repr__(self):
        """
        A textual representation of the error (error message).

        Structure: ~TextErrorType.error_message ' - Character location: from ' <start index of substring>
                   ' to ' <end index of substring>'.\n\t -->' <'...'|'(beginning of line)'> <matched text>
                   <'...'|'(end of line)'>

        :return:
        str
            The error message
        """
        last_space_before_occurrence = self.last_space_before_occurrence()
        before_string = "..."
        if last_space_before_occurrence == -1:
            before_string = "(beginning of line)"
        first_space_after_occurrence = self.first_space_after_occurrence
        after_string = "..."
        if first_space_after_occurrence == -1:
            after_string = "(end of line)"
        message = (self.error_type.error_message
                   + " - Character location: from " + str(self.start_idx_in_text)
                   + " to " + str(self.end_idx_in_text) + "."
                   + "\n\t --> "
                   + before_string
                   + self.get_matched_text()
                   + after_string)
        return message


def filter_errors_list(errors, deactivate=None):
    """
    Excludes the errors identified by the identifier in the deactivate list from the list of all errors.

    :param errors: [TextErrorType]
        List of all errors.
    :param deactivate: [str]
        List of identifiers or errors to not check for.
    """
    errors_to_check_for = errors
    if deactivate is not None:
        errors_to_check_for = [e for e in errors if e.identifier is None or e.identifier not in deactivate]
    return errors_to_check_for


def check_for_error_and_print(file_to_check, errors):
    """
    Checks a file for all known textual errors except those excluded.

    :param file_to_check:
        The path of the file to check for errors.
    :param errors: {int: [TextErrorType]}
        Dict of lists of all errors indexed by the line number.
    """
    i = 0
    all_errors = {}
    with open(file_to_check, "r") as file_to_check:
        for line in file_to_check:
            i += 1
            errors_in_line = []
            for one_error_type in errors:
                error_from_error_type = one_error_type.check_for_error(line)
                if error_from_error_type is not None:
                    errors_in_line.append(error_from_error_type)
            if len(errors_in_line) > 0:
                all_errors[i] = errors_in_line
    return all_errors

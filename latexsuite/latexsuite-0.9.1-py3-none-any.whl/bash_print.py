"""
Bash printing with font.
"""

import sys


class Status:
    """
    Status indicators.
    """

    UNKNOWN = -1
    SUCCESS = 0
    ERROR = 1
    WARNING = 2


class BackgroundColours:
    """
    Colour codes to highlight text in bash output.
    """

    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BACK_TO_DEFAULT = '\033[0m'


def message_with_colour(message, colour, bold=False, underline=False):
    """
    Annotated a message with colour code and highlight codes for bash printing.

    Colour, bold and underline code are added to the front of the message. The back
    to default code is added to the end of the message to not affect printing that
    follows the message.

    :param message: str
        The message.
    :param colour: BackgroundColours constant
        The colour code.
    :param bold: bool.
        If True adds bold code.
    :param underline: bool.
        If True adds underline code.
    :return: str
        The message with added codes.
    """
    font = colour
    if bold:
        font += BackgroundColours.BOLD
    if underline:
        font += BackgroundColours.UNDERLINE
    coloured_message = font + str(message) + BackgroundColours.BACK_TO_DEFAULT
    return coloured_message


def print_to_error(message):
    """
    Send message to stderr.

    :param message: str
        The message
    """
    print(message, file=sys.stderr)


def print_warning(message):
    """
    Prints a message in yellow warning colour.

    :param message: str
        The message.
    """
    print(message_with_colour(message, BackgroundColours.WARNING))


def print_error(message):
    """
    Prints a message in red error colour.

    :param message: str
        The message.
    """
    print_to_error(message_with_colour(message, BackgroundColours.ERROR))


def print_success(message):
    """
    Prints a message in green success colour.

    :param message: str
        The message
    """
    print(message_with_colour(message, BackgroundColours.SUCCESS))


def print_status(message, status, status_text=None):
    """
    Prints a status message in the form: <message>\t[<status>].

    The first part of the status message is any message passed as a parameter.
    Following this with a tab distance and in boxed brackets is a status message
    text in a colour based on the specified status:
        - Status.SUCCESS:
            - text: "SUCCESS"
            - colour: BackgroundColours.SUCCESS (green)
        - Status.ERROR:
            - text: "FAILURE"
            - colour: BackgroundColours.ERROR (red)
        - Status.WARNING:
            - text: "WARNING"
            - colour: BackgroundColours.WARNING (yellow)
        - Unknown/else
            - text: "UNKNOWN"
            - colour: BackgroundColours.BLUE (blue)
    The default message can be overridden by specifying the additional parameter.

    :param message: str
        The message.
    :param status: Status constant
        The status.
    :param status_text: str
        If the value is not None this text overrides the default status message in the
        boxed brackets.
    """
    if status == Status.SUCCESS:
        if status_text is None:
            status_text = "SUCCESS"
        status_colour = BackgroundColours.SUCCESS
    elif status == Status.ERROR:
        if status_text is None:
            status_text = "FAILURE"
        status_colour = BackgroundColours.ERROR
    elif status == Status.WARNING:
        if status_text is None:
            status_text = "WARNING"
        status_colour = BackgroundColours.WARNING
    else:
        if status_text is None:
            status_text = "UNKNOWN"
        status_colour = BackgroundColours.BLUE
    status_indicator = message_with_colour(status_text, status_colour)
    print(message, "\t", f"[{status_indicator}]")

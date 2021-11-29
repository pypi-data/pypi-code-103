from pdx import Session
from pdx import Config
from pdx.db import ConnectionHolder
import os
import math
import logging
import getpass


class Console:
    suppressConsoleOutput = False
    indent = 0
    level_indicators = True
    numWarnings = 0
    numErrors = 0

    def clear(self):
        """Clear the screen, unless there are errors or warnings"""
        # If there are no errors, clear the screen
        if self.numErrors + self.numWarnings == 0:
            os.system('clear')

        # If there are errors or warnings, just print a few blank lines
        else:
            self.put("\n\n\n")

    def put_heading(self, heading, color='white', chars='-'):
        """Print a heading that stands out in the console"""

        # Log heading in log file
        self.log_info(heading+"\n-------------------------------------------------------------")

        # If output is suppressed, return now
        if self.suppressConsoleOutput:
            return

        # Determine width of terminal window
        term_w = self.console_width()
        head_w = term_w

        # Get a full line of given characters
        char_line = ""
        for ii in range(head_w):
            char_line += chars[:1]

        # Limit heading to window width
        heading_line = "  {0}  ".format(heading[:head_w])

        # Pad heading with chars
        while len(heading_line) < head_w:
            heading_line = "{0}{1}{0}".format(chars[:1], heading_line)

        # print heading
        self.put()
        self.put_color(char_line, color)
        self.put_color(heading_line.strip()[:head_w], color)
        self.put_color(char_line, color)

        # Cleanup
        del head_w
        del term_w
        del char_line
        del heading_line

    def put(self, text='', end="\n"):
        """
        Simply prints a line to the terminal.
        Use this rather than calling print() directly for any application where:
            - output may be suppressed by a parameter
            - script may be scheduled to run and email output to a mailing list
        """
        # Allow output suppression
        if self.suppressConsoleOutput:
            return

        # ToDo: Allow emailing of all output

        # Print text to the terminal (with or without indent)
        print(f"{''.ljust(self.indent)}{text}", end=end)

    def unexpected_error(self, system_error, friendly_error=None):
        """Print an error message to the screen, and log it as an error"""
        # Log error message(s)
        self.log_error("{0}\n{1}".format(friendly_error if friendly_error else 'Unexpected Error', system_error))

        # Always count as an error
        self.numErrors += 1

        # Since error already logged and incremented, just print color
        self.put_color("[UNEXPECTED]", 'error', ' ')
        self.put_color(friendly_error if friendly_error else system_error, 'error')

        # Since this package will only ever be used by developers, go ahead and print the ugly message too
        if friendly_error:
            self.put_color(system_error, 'error')

    def put_error(self, text, increment_error_count=True):
        """Print an error message to the screen, and log it as an error"""
        # Log error message
        self.log_error("{0}".format(text))

        # Add an indicator (in addition to color, which may be suppressed) that this is an error
        if self.level_indicators:
            self.put_color("[ERROR]", 'error', ' ')

        # Print error to screen
        self.put_color(text, 'error')

        # Increment error counter
        if increment_error_count:
            self.numErrors += 1

    def put_warning(self, text, increment_warning_count=True):
        """Print a warning message to the screen, and log it as a warning"""
        # Log warning message
        self.log_warning("{0}".format(text))

        # Add an indicator (in addition to color, which may be suppressed) that this is a warning
        if self.level_indicators:
            self.put_color("[WARN]", 'warning', ' ')

        self.put_color(text, 'warning')

        # Increment error counter
        if increment_warning_count and not self.suppressConsoleOutput:
            self.numWarnings += 1

    def put_info(self, text):
        """Print an info message to the screen, and log it too"""
        # Log info message
        self.log_info("{0}".format(text))

        self.put_color(text, 'blue')

    def put_success(self, text):
        """Print a success message to the screen, and log it too"""
        # Log info message
        self.log_info("{0}".format(text))

        self.put_color(text, 'green')

    def put_debug(self, text):
        """Log a debug message.  If in debug mode, also print it to the screen"""
        self.log_debug("{0}".format(text))

        if Session.debug_mode:
            # Add an indicator (in addition to color, which may be suppressed) that this is a debug message
            self.put_color("[DEBUG]", 'debug', ' ')

            self.put_color(text, 'debug')

    def put_color(self, message, color, end_char="\n"):
        """
        Print a message to the screen in the given color.
        Does not log the message
            message: The message/text to display to the user
            color: The color to print in (must exist in color dict)
            end_char: character to print at the end of the message
                  - default is a newline character
                  - to continue printing on the same line (i.e. in a different color), pass in an empty string
        """
        # Make sure color is lowercase, and use default if None is given
        color_key = color.lower().strip() if color is not None else 'default'

        try:
            # Only print color to the terminal (do not record)
            if not self.suppressConsoleOutput:
                if not Config.disable_color:
                    print("{0}".format(Config.color_dict[color_key]), end="")

            # Print the message to the screen, and record (if recording)
            self.put("{0}".format(message), end="")

            # Only reset the color if color was set (on terminal only)
            if not self.suppressConsoleOutput:
                if not Config.disable_color:
                    print("{0}".format(Config.color_dict["reset"]), end="")

            # Print the specified end character to terminal and record (if recording)
            self.put("", end=end_char)

        except KeyError:
            self.put(message)
            self.put_warning("{0} is not a configured color.".format(color))

    def format_list(self, p_list, empty_message=None, numbering=True, padding=4, indent=0):
        """Return a formatted list of values as a string"""
        if type(p_list) is not list:
            p_list = list(p_list)
        list_length = len(p_list) if p_list is not None else 0
        formatted_list = ""

        # If no list values to print, print the empty message
        if type(p_list) is not list or list_length == 0:
            return "{0}\n".format(empty_message) if empty_message else ''

        # Try to determine longest value (for determining column widths)
        max_length = 0

        # Only print columns when not numbering the items
        if not numbering:
            for item in p_list:
                # Track longest item length
                item_length = len(str(item))
                max_length = item_length if item_length > max_length else max_length

        # Determine number of columns
        col_width = (max_length + padding)
        if max_length == 0:
            num_cols = 1
        else:
            # last column's padding will be stripped
            num_cols = max([int(math.floor((self.console_width() - indent + padding) / col_width)), 1])

        ii = 0
        number_width = len(str(list_length))
        col_pointer = 1

        # Write the values to the variable
        for item in p_list:
            item_string = str(item).ljust(col_width)
            end_char = ""
            ii += 1
            nn = "{0}. ".format(str(ii).rjust(number_width))

            if col_pointer == num_cols:
                item_string = item_string.strip()
                end_char = "\n"

            formatted_list += "{0}{1}{2}{3}".format(
                " ".ljust(indent) if indent > 0 else "",
                nn if numbering else "",
                item_string,
                end_char
            )

            col_pointer = (col_pointer + 1) if col_pointer < num_cols else 1

        # End the last line
        if col_pointer > 1:
            formatted_list += "\n"

        # append a blank line
        formatted_list += "\n"

        # Cleanup
        del list_length
        del max_length
        del col_width
        del num_cols
        del number_width
        del col_pointer

        return formatted_list

    def put_list(self, p_list, empty_message=None, numbering=True, padding=4, indent=0):
        """Print a list of values to the terminal"""

        # Clean any output indent since list will be multi-line
        indent_before = self.indent
        self.indent = 0

        # Output indentation (if any) is added to the specified list indentation
        if indent_before > 0:
            indent = indent + indent_before

        # Print the list with no additional "output" indentation
        self.put(self.format_list(p_list, empty_message=empty_message, numbering=numbering, padding=padding, indent=indent))

        # Restore any output indentation
        self.indent = indent_before

        return True

    def prompt(self, message, response_list=None, automated_answer=None, make_uppercase=None):
        """Prompt the user for input"""
        self.trace("prompt", [message, response_list, automated_answer, make_uppercase])
        self.log_info("Prompt: {0}".format(message))

        # Use default answer when run in automated mode, or when output is suppressed
        if Session.auto_mode or self.suppressConsoleOutput:
            self.log_info("Automated response: {0}".format(automated_answer))
            return automated_answer

        # If make uppercase was not specified, determine T/F based on response_list
        if make_uppercase is None and response_list:
            # If a list of allowed responses was provided, are they all uppercase?
            if any(str(xx) != str(xx).upper() for xx in response_list):
                make_uppercase = False
            else:
                make_uppercase = True

        answer = None
        err = False

        try:
            while answer is None and not Session.auto_mode:
                answer = input("{0}:  ".format(message.strip(': ')))

                if make_uppercase:
                    answer = answer.upper()

                if response_list is not None and type(response_list) is list:
                    if answer not in response_list:
                        self.put_warning("{0} is not a valid response.".format(answer), False)
                        # Formatted list
                        fl = self.format_list(response_list, numbering=False, indent=2)
                        self.put(f"Valid responses are: \n{fl}")
                        self.put()
                        answer = None

        except KeyboardInterrupt:  # ctrl-c
            self.put()
            self.put_color("User canceled request for input", 'red')
            err = True
        except EOFError:  # ctrl-d
            self.put()
            self.put_color("User canceled request for input", 'red')
            err = True

        if err:
            return automated_answer
        else:
            self.log_info("User response: {0}".format(answer))
            return answer

    def prompt_secret(self, message, automated_answer=None):
        """Prompt the user for secret input"""
        self.trace("prompt", [message, automated_answer])
        self.log_info("PromptSecret: {0}".format(message))

        # Use default answer when run in automated mode, or when output is suppressed
        if Session.auto_mode or self.suppressConsoleOutput:
            self.log_info("Automated response: {0}".format(automated_answer))
            return automated_answer

        answer = None
        err = False

        try:
            while answer is None and not Session.auto_mode:
                answer = getpass.getpass("{0}:  ".format(message.strip(': ')))
                if answer == '':
                    answer = None
                    self.put_color("\nNo input was detected. Press ctrl-c to abort\n", 'gray')

        except KeyboardInterrupt:
            self.put()
            self.put_error("User canceled request for input")
            err = True

        if err:
            return automated_answer
        else:
            return answer

    def goodbye(self, exit_code=None, print_status=None, print_log_path=None):
        """Clean up and say goodbye"""
        self.trace("goodbye", [exit_code, print_status, print_log_path], 'info')

        # Color to use for goodbye text
        goodbye_color = 'cyan'

        # Short aliases for numbers of errors and warnings
        ee = self.numErrors
        ww = self.numWarnings

        # Should status line be printed? (determine default)
        if print_status is None:
            # Only print status as default if something happened
            print_status = (self.numErrors + self.numWarnings) > 0

        # Should log path be printed? (determine default)
        if print_log_path is None:
            # Print log_path as default if something happened or in debug mode
            print_log_path = (Session.debug_mode or (self.numErrors + self.numWarnings) > 0)

        # Determine default exit code
        if exit_code is None:
            exit_code = self.numErrors

        # Close any open DB connections
        ConnectionHolder.closeout()

        # Print status and/or log path if desired
        if not self.suppressConsoleOutput:

            # Blank line
            self.put()

            # Print number of errors and warnings
            if print_status:
                script = Session.script_name

                # Do not pluralize single error/warning
                ees = 's' if ee != 1 else ''
                wws = 's' if ww != 1 else ''

                if ee == 0 and ww == 0:
                    self.put_color("{0} completed successfully.".format(script), goodbye_color)
                elif ee > 0 and ww == 0:
                    self.put_color(
                        "{0} completed with {1} error{2}.".format(script, ee, ees),
                        goodbye_color
                    )
                elif ee == 0 and ww > 0:
                    self.put_color(
                        "{0} completed with {1} warning{2}.".format(script, ww, wws),
                        goodbye_color
                    )
                else:
                    self.put_color(
                        "{0} completed with {1} error{2} and {3} warning{4}.".format(script, ee, ees, ww, wws),
                        goodbye_color
                    )

            # Print log path, if desired
            if print_log_path:
                self.put_color("Log file: {0}".format(Session.logInstance.logFilePath), 'cyan')

        # Exit the script
        exit(exit_code)

    def trace(self, function_name, parameters=None, level='debug'):
        """Print a trace message. Debug level is default."""
        if type(parameters) is list:
            parameter_string = "{0}".format(parameters).strip('[]')
        elif parameters is None:
            parameter_string = ""
        else:
            parameter_string = "{0}".format(parameters)

        self.log("TRACE: {0}({1})".format(function_name, parameter_string), level)

    # Shortcuts for the static log method below
    def log_info(self, content):
        self.log(content, 'info')

    def log_warning(self, content):
        self.log(content, 'warning')

    def log_error(self, content):
        self.log(content, 'error')

    def log_debug(self, content):
        self.log(content, 'debug')

    def console_width(self):
        """Determine the current width of the console/terminal window"""
        # ToDo: If user has defined a width preference, use it, regardless of actual window size
        # if io_config.has_width_preference:
        #     return io_config.assumed_width

        # Get the actual terminal size
        try:
            rows, columns = os.popen('stty size', 'r').read().split()
            return int(columns)
        except Exception as ee:
            self.log_debug("Unable to determine console width")
            return 80

    @staticmethod
    def log(content, level='info'):
        if level == 'debug':
            logging.debug("{0}".format(content))
        elif level == 'info':
            logging.info("{0}".format(content))
        elif level == 'warn' or level == 'warning':
            logging.warning("{0}".format(content))
        elif level == 'error':
            logging.error("{0}".format(content))
        else:
            logging.info("{0}".format(content))

    def __init__(self):
        if Session.consoleInstance:
            self.put_warning("Opening a new console instance, which will not be tracked in the Session.")
        else:
            Session.consoleInstance = self


def get():
    """Get a Console from the Session, or start a new one if needed"""
    if Session.consoleInstance:
        return Session.consoleInstance
    else:
        return Console()


def goodbye(exit_code=None, print_status=None, print_log_path=None):
    """Get a console and use it to say goodbye"""
    get().goodbye(exit_code, print_status, print_log_path)

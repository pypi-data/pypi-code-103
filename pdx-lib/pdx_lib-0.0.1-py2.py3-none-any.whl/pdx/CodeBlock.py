import re


class CodeBlock:
    content = None
    language = None

    _noComments = None

    # Count number of lines of code.
    def get_number_of_lines(self, ignore_blank_lines=True):

        # Do not count leading or trailing empty lines
        src = self.content.strip() if self.content else None

        # If there is no content, return 0
        if src is None or len(src) == 0:
            return 0

        # Do not count empty lines
        if ignore_blank_lines:
            src = src.replaceAll("\n+", "\n")

        # Otherwise, return number of \n plus one (to count the final line)
        return src.count("\n") + 1

    # Get the code contents with all comments removed
    def get_without_comments(self):

        # If comments were already removed, return the revised content
        if self._noComments:
            return self._noComments

        # Otherwise, remove comments from content
        self._noComments = self.content

        # Define comment characters
        single_line = '//'
        multi_line_start = "/*"
        multi_line_end = '*/'
        mle_length = len(multi_line_end)
        if self.language and self.language.lower() == 'sql':
            single_line = '--'
        elif self.language and self.language.lower() in ['python', 'sh', 'bash', 'bsh', 'shell']:
            single_line = '#'
            multi_line_start = None

        # Remove multi-line comments, if applicable
        if multi_line_start:
            # Determine some maximum number of iterations (prevent infinite loop)
            num_chars = len(self._noComments)
            max_iterations = num_chars / 2
            ii = 0
            # For as long as multiline comment characters exist in the content...
            while multi_line_start in self._noComments and ii < max_iterations:
                # Get positions of start and end of the next comment
                offset1 = self._noComments.index(multi_line_start)
                offset2 = self._noComments.index(multi_line_end)

                # If the end of the comment was located, remove the comment
                if offset2 and offset1 < offset2:
                    self._noComments = self._noComments[:offset1] + self._noComments[offset2 + mle_length:]

                # if comment never ends, remove remainder of content
                else:
                    self._noComments = self._noComments[:offset1]

                # Track number of iterations
                ii += 1

        # Temporarily replace any quoted single-line comment characters
        # Ex: "http://www..."
        placeholder = '@@@CC@@@'
        self._noComments = re.sub(
            r'(\'[^\'\n]*)' + single_line + r'([^\'\n]*\')',
            r'\1' + placeholder + r'\2',
            self._noComments
        )

        # Look at individual lines
        while single_line in self._noComments:

            comment_start = self._noComments.find(single_line)
            comment_end = self._noComments.find("\n", comment_start)

            # If comment never ends
            if comment_end == -1:
                # Use portion prior to comment start
                self._noComments = self._noComments[:comment_start]
            else:
                # Use portion prior to comment start + portion after comment end
                self._noComments = self._noComments[:comment_start] + self._noComments[comment_end:]

        # Restore any quoted instances of -- that were replaced
        self._noComments = self._noComments.replace(placeholder, single_line)

        return self._noComments

    def __init__(self, content, language=None):
        self.content = content
        self.language = language
        self._noComments = None

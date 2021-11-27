import re

from markdown import markdown
from typing import Union, Callable, Any

from .namedlist import NamedList
from .link import link
from .lists import DropdownMenu, RadioButtons
from .inlines import Label, Textarea, InputText, Checkbox, Button



class Parser:
    def __init__(self, document: str):
        self.document = document

        # Remove comments to avoid incorrectly parsing elements within them
        self.document = self.remove_comments(self.document)

        # TODO: Implement extensible lists!
        self.elements = self.create_lists(self.document, prefixes='-*')

        # Parse all types of inline elements
        for inline_element_type in [Label, Textarea, InputText, Checkbox, Button]:
            self.elements = self.construct_elements(
                self.elements, inline_element_type.pattern, inline_element_type)

        # Replace all line breaks at the beginning or end of strings with `<br>`
        for i, element in enumerate(self.elements):
            if isinstance(element, str):
                self.elements[i] = re.sub(r'[ \t]*\n', '<br>', element)

        # Only the form elements
        self.form_elements = [
            e for e in self.elements
            if isinstance(e, (
                DropdownMenu,
                RadioButtons,
                Textarea,
                InputText,
                Checkbox
            ))
        ]

    def remove_comments(self, document: str):
        """Remove comments from document."""
        
        return re.sub(
            r'\<\!\-\-((?:.|\n)*?)\-\-\>',
            # Leave a line break if any are found in match
            lambda m: ("", '\n')['\n' in m.group(1)],
            document
        )

    def create_lists(self, document: str, prefixes: str = '-*+', flatten: bool = False) \
            -> list[Union[str, NamedList[Union[str, NamedList[str]]]]]:
        """Parse dropdown menus, radio buttons
        and extensible lists in the documents.

        # Item suffixes:
        `-`  Dropdown menu
        `*`  Radio buttons
        `+`  Extensible list
        """

        elements = []

        for i, line in enumerate(document.splitlines()):
            # Skip empty lines
            if not line:
                if elements:
                    if not isinstance(elements[-1], str):
                        elements.append("\n\n")
                    else:
                        elements[-1] += '\n'
                else:
                    elements.append("\n")
                continue

            # Create a new named list
            if m := re.match(fr'\#{{1,6}} (.+)\:', line.lstrip()):
                elements.append(NamedList(m.group(1)))
                continue

            # Add item to latest named list
            if elements and isinstance(elements[-1], NamedList):
                pattern = r'([{prefixes}]) ([^\n]+(?:\n(?!\1)[^\n]+)*)' \
                                .format(prefixes=prefixes)

                if m := re.match(pattern, line.lstrip()):
                    elements[-1].append(m)

                elif elements[-1]:
                    elements[-1][-1] += f'\n{line}'
                else:
                    elements.append(f'{line}\n')

                continue

            # Attach line to previous line
            if elements and isinstance(elements[-1], str):
                elements[-1] += f'{line}\n'
                continue

            # Add any other line as is
            elements.append(f'{line}\n')


        # Convert into the correct list objects;
        # `DropdownMenu`, `RadioButtons`, `ExtensibleList`
        # Also parse inline elements.

        for i, element in enumerate(elements):
            if not isinstance(element, NamedList):
                continue

            # TODO: Parse inline elements in lists
            # Make sure there is only 1 element per entry
            # and that it is a link object or string

            if element.prefix == '+':
                # Parse lists within extensible list
                for j, subelem in enumerate(element):
                    if isinstance(subelem, str):
                        element[j] = self.create_lists(subelem, flatten=True)
            else:
                # Dropdown menus and radio button
                links = [*map(link, element)]

                if element.prefix == '-':
                    elements[i] = DropdownMenu(element.name, links)
                if element.prefix == '*':
                    elements[i] = RadioButtons(element.name, links)

        # If the only element is a string,
        # no elements have been parsed
        if len(elements) == 1 and flatten:
            return elements[0]

        return elements

    def segment_by_pattern(self, document: str, pattern: Union[str, re.Pattern]) \
            -> list[Union[str, re.Match]]:
        """Find all occurrences of a pattern by recursively matching once
        and returning the left-hand side, the match and the right-hand side.

        Returns a list of the unmatched sections mixed with the matches at the places they occur.
        Example:
            Pattern: '\d+'
            In: 'hello 123 world 456 !'
            Out: ['hello ', Match('123'), ' world ', Match('456'), ' !']
        """

        if match := re.search(pattern, document):
            # The surrounding left and right hand sides of the match
            left = document[:match.start()]
            right = document[match.end():]

            # Attempt to find further matches on the right hand side.
            right = self.segment_by_pattern(right, pattern)
            
            # The left hand side will not need to be parsed,
            # as `re.search` should already have found the first occurrence in the document.

            return [left, match, *right]
        
        return [document]
        
    def construct_elements(self, elements: list[Any], pattern: Union[str, re.Pattern],
                                    constructor: Callable) -> list[Any]:
        """Parse all instances of the specified pattern in all strings
        of the elements and instantiate objects from the matches.
        """

        for i, element in enumerate(elements):
            if not isinstance(element, str):
                continue
            
            # Find all matches for the element pattern
            new_elements = self.segment_by_pattern(element, pattern)

            # Construct objects from matches
            new_elements = [constructor(e) if isinstance(e, re.Match) else e
                                for e in new_elements]

            # Replace index and insert new elements
            elements[i:i + 1] = new_elements

        return elements
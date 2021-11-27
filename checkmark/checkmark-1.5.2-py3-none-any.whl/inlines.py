from re import Match

from .link import get_pattern as get_link_pattern



class Label:
    pattern = get_link_pattern(r'\:')
    
    def __init__(self, match: Match):
        self.text = match.group(2)
        self._for = match.group(3)
        self.hint = match.group(4) or ""

    def __str__(self):
        """Render as HTML"""
        return (
            f'<label for="{self._for}" '
            f'title="{self.hint}">'
            f'{self.text}</label>'
        )


class Textarea:
    pattern = get_link_pattern(r'\>\>')
    
    def __init__(self, match: Match):
        self.name = match.group(3)
        self.placeholder = match.group(2)
        self.hint = match.group(4) or ""
        self.value = ""

    def __str__(self):
        """Render as HTML"""
        return (
            f'<textarea id="{self.name}" '
            f'name="{self.name}" '
            f'title="{self.hint}" '
            f'placeholder="{self.placeholder}" '
            f'rows=3>'
            f'{self.value}</textarea>'
        )


class InputText:
    pattern = get_link_pattern(r'\>')
    
    def __init__(self, match: Match):
        self.name = match.group(3)
        self.placeholder = match.group(2)
        self.hint = match.group(4) or ""
        self.value = ""

    def __str__(self):
        """Render as HTML"""
        return (
            f'<input type="text" '
            f'id="{self.name}" '
            f'name="{self.name}" '
            f'title="{self.hint}" '
            f'placeholder="{self.placeholder}" '
            f'value="{self.value}">'
        )


class Checkbox:
    pattern = get_link_pattern(r'\[([ x])\] ')
    
    def __init__(self, match: Match):
        self.name = match.group(4)
        self.text = match.group(3)
        self.hint = match.group(5) or ""
        self.value = match.group(2) == 'x'

    def __str__(self):
        """Render as HTML"""
        return (
            f'<div class="checkbox" title={self.hint!r}>'
            f'<input type="checkbox" id="{self.name}" name="{self.name}" '
            f'{"checked" if self.value else ""}>'
            # f'<label for="{self.name}">{self.text}</label>'
            f'<label>{self.text}</label>'
            f'</div>'
        )


class Button:
    pattern = get_link_pattern(r'\@')
    
    def __init__(self, match: Match):
        self.text = match.group(2)
        self.name = match.group(3)
        self.hint = match.group(4) or ""

    def __str__(self):
        """Render as HTML"""
        return (
            f'<button type="button" title="{self.hint}" '
            f'onclick="submitData({self.name!r})">{self.text}</button>'
        )
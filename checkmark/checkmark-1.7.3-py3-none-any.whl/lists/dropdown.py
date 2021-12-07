from ..link import Link



class DropdownMenu:
    def __init__(self, name: str, options: list[Link]):
        self.name = name
        self.options = options
        self.value = None if not options else options[0].url

    def __str__(self):
        """Render as HTML"""
        options = "".join([
            f'<option value="{option.url}" '
            f'title="{option.hint}" '
            f'{"selected" if self.value == option.url else ""}>'
            f'{option.text}</option>'
                for option in self.options
        ])
        return f'<select name="{self.name}" id="{self.name}">{options}</select>'
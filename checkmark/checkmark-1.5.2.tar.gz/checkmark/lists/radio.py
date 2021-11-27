from ..link import Link



class RadioButtons:
    def __init__(self, name: str, options: list[Link]):
        self.name = name
        self.options = options
        self.value = None if not options else options[0].url

    def __str__(self):
        """Render as HTML"""
        radio_buttons = "".join([
            f'<div class="radio" id="{self.name}">'
            f'<input type="radio" id="{self.name}.{option.url}" '
            f'name="{self.name}" value="{option.url}" title="{option.hint}" '
            f'{"checked" if self.value == option.url else ""}>'
            f'<label for="{self.name}.{option.url}">{option.text}</label>'
            f'</div>'
                for option in self.options
        ])
        return f'<div class="radio-buttons">{radio_buttons}</div>'
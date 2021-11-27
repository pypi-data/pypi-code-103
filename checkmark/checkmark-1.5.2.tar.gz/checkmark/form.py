import webview
import re

from markdown import markdown
from typing import Callable
from contextlib import suppress

from .parser import Parser
from . import templates



class MarkdownForm:
    """An HTML form window generated from Markdown"""

    def __init__(self, 
        title: str,
        document: str,
        style: str = templates.style,
        api_methods: dict[str, Callable] = None,
    ):
        self.title = title
        self.style = style

        self.api_methods = api_methods or {}
        
        parser = Parser(document)
        self.elements = parser.elements
        self.form_elements = parser.form_elements

    def html(self) -> str:
        """Render into HTML"""

        body = "".join(
            # Parse Markdown in strings and remove added surrounding paragraph tags
            re.sub(
                r'(^<p>|</p>$)', "",
                markdown(element),
                flags=re.IGNORECASE

            ) if isinstance(element, str) else str(element)
            for element in self.elements
        )
        
        return templates.html \
            .replace('(( body ))', body) \
            .replace('(( style ))', self.style)

    def on_open(self, window: webview.Window):
        """What to do before starting the form window"""

    def on_close(self):
        """What to do after shutting down the form window"""

    def submit_data(self, method_name: str, data: dict):
        # Remove integer indices
        data = {key: value for key, value in data.items() if not key.isdigit()}

        # Call the specified method with received data
        self.api_methods[method_name](data)

    def update(self, keys: list[str], data: dict, reload_page: bool = False):
        """Update specific keys from submitted data.

        This can be used in an API method to save the values
        of only certain elements in the form.
        """

        for e in self.form_elements:
            if e.name in keys and e.name in data:
                e.value = data[e.name]

        if reload_page:
            self.window.load_html(self.html())

    def start(self, *args, **kwargs):
        """Launch form window"""

        try:
            width = kwargs.pop('width', 480)
            height = kwargs.pop('height', 640)

            self.window = webview.create_window(
                title=self.title,
                html=self.html(),
                js_api=self,
                width=width,
                height=height,
                *args, **kwargs
            )
            self.on_open(self.window)
            
            with suppress(KeyboardInterrupt):
                webview.start()
        finally:
            self.on_close()

    def stop(self):
        """Close form window"""
        self.window.destroy()

    def api_method(self, f: Callable):
        """Decorator for defining function as API method to form"""
        self.api_methods[f.__name__] = f
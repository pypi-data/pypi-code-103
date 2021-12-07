from typing import Callable, Any

import webview
import re

from markdown import markdown
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

    def __getitem__(self, key: str) -> Any:
        for element in self.form_elements:
            if element.name == key:
                return element.value
        raise KeyError(key)

    def items(self) -> dict[str, Any]:
        """Get form keys and values as a dictionary."""
        return {e.name: e.value for e in self.form_elements}

    def get(self, key: str, default: Any = None) -> Any:
        """Return value for key if key is in form elements, else default."""
        try:
            return self[key]
        except KeyError:
            return default

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

    def update(self, data: dict, keys: list[str] = None, reload_page: bool = False):
        """Update specific keys from submitted data.

        This can be used in an API method to save the values
        of only certain elements in the form.
        """

        for e in self.form_elements:
            if keys and e.name not in keys:
                continue
            if e.name not in data:
                continue

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
                width=width,
                height=height,
                *args, **kwargs
            )
            self.window.expose(self.submit_data)
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
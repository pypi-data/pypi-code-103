"""A text reader for the Understory framework."""

from understory import web

app = web.application(__name__, prefix="readers/text")


@app.control(r"")
class TextReader:
    """A text reader for notes and articles."""

    def get(self):
        """Render the editor."""
        return app.view.text()

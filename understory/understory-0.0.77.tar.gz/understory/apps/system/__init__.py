""""""

from understory import web
from understory.web import tx

app = web.application(__name__, prefix="system")


@app.control(r"")
class System:
    """Render information about the application structure."""

    def get(self):
        applications = web.get_apps()
        return app.view.index(tx.app, applications)

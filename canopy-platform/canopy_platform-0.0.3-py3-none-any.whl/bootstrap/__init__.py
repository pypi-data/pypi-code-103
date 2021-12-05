from understory import web

__all__ = ["app"]

app = web.application(__name__)


@app.control("")
class Bootsrap:
    """"""

    def get(self):
        return app.view.index()

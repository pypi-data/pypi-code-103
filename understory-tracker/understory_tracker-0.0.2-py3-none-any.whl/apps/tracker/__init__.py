"""
Personal tracker for your personal website.

Track your physical movement: GPS locations and trip circuits (eg. Overland)

Track your web movement: webpage visits (eg. Liana)

"""

from understory import sql, web
from understory.web import tx

model = sql.model(
    __name__,
    locations={"location": "JSON"},
    trips={"start": "DATETIME", "distance": "TEXT", "location": "JSON"},
    web={"location": "JSON"},
)
app = web.application(
    __name__, prefix="tracker", args={"start": r".*"}, model=model.schemas
)


@app.wrap
def connect_model(handler, main_app):
    """Connect the model to this transaction's database."""
    tx.tracker = model(tx.db)
    yield


@app.control(r"")
class Tracker:
    """"""

    def get(self):
        """"""
        if not tx.user.session:
            raise web.NotFound("nothing to see here.")
        return app.view.physical(
            tx.tracker.get_locations(), tx.tracker.get_trip_locations()
        )


@app.control(r"physical")
class Physical:
    """"""

    # @app.scope("fitness")
    # @web.scope("mj.com", "ace.com")
    def get(self):
        """"""
        return app.view.physical(tx.tracker.get_locations(), tx.tracker.get_trips())

    def post(self):
        """"""
        for location in tx.request.body["locations"]:
            tx.tracker.add_location(location)
        if trip := tx.request.body.get("trip"):
            tx.tracker.add_trip_location(trip)
        return {"result": "ok"}


@app.control(r"physical/trips/{start}")
class Trip:
    """"""

    def get(self):
        """"""
        if not tx.user.session:
            raise NotFound("nothing to see here.")
        return app.view.trip(tx.tracker.get_trip(self.start))


@app.control(r"web")
class Web:
    """"""

    def get(self):
        """"""
        if not tx.user.session:
            raise NotFound("nothing to see here.")
        return app.view.web(tx.tracker.get_web_locations())

    def post(self):
        """"""
        tx.tracker.add_web_location(tx.request.body["location"])
        print("hello")
        return {"result": "ok"}


@model.control
def add_location(db, location):
    db.insert("locations", location=location)


@model.control
def get_locations(db):
    return db.select("locations")


@model.control
def add_trip_location(db, location):
    db.insert(
        "trips",
        start=location["start"],
        distance=location["distance"],
        location=location,
    )


@model.control
def get_trips(db):
    return db.select("trips", group="start")


@model.control
def get_trip(db, start):
    return db.select(
        "trips",
        where="start = ?",
        vals=[str(start).replace("+00:00", "Z")],
        order="distance ASC",
    )


@model.control
def add_web_location(db, location):
    db.insert("web", location=location)


@model.control
def get_web_locations(db):
    return db.select("web")

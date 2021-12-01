"""An IndieAuth client for the Understory framework."""

from indieauth import client
from understory import web
from understory.web import tx

__all__ = ["app"]

app = web.application(
    __name__,
    prefix="guests",
    model=client.model.schemas,
)


@app.wrap
def connect_model(handler, main_app):
    """Connect the model to this transaction's database."""
    # TODO store User Agent and IP address with `sessions`
    # TODO attach session to this user
    tx.auth_client = client.model(tx.db)
    yield


@app.control(r"")
class Guests:
    """Site guests."""

    def get(self):
        """Return a list of guests to owner, the current user or a sign-in page."""
        if tx.user.session:
            if tx.user.is_owner:
                return app.view.guests(tx.auth_client.get_guests())
            else:
                return tx.user.session
        else:
            return app.view.signin(tx.host.name)


@app.control(r"sign-in")
class SignIn:
    """IndieAuth client sign in."""

    def get(self):
        """Initiate a sign-in."""
        form = web.form("me", return_to="/")
        tx.user.session["return_to"] = form.return_to
        raise web.SeeOther(
            client.initiate_sign_in(
                tx.origin, "guests/authorize", form.me, scopes=("profile", "email")
            )
        )


@app.control(r"authorize")
class Authorize:
    """IndieAuth client authorization redirect URL."""

    def get(self):
        """Complete a sign-in by requesting a token."""
        form = web.form("state", "code")
        response = client.authorize_sign_in(form.state, form.code, "profile")
        tx.user.session["uid"] = [response["me"]]
        tx.user.session["name"] = [response["profile"]["name"]]
        raise web.SeeOther(tx.user.session["return_to"])


@app.control(r"sign-out")
class SignOut:
    """IndieAuth client sign out."""

    def get(self):
        """Return a sign-out form."""
        return app.view.signout()

    def post(self):
        """Sign the guest out."""
        form = web.form(return_to="")
        client.sign_out(tx.user.session["uid"])
        tx.user.session = None
        raise web.SeeOther(f"/{form.return_to}")

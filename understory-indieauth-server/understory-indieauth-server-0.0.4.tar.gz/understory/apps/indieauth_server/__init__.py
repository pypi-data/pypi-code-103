"""An IndieAuth server for the Understory framework."""

from indieauth import server
from understory import web
from understory.web import tx

__all__ = ["app"]

app = web.application(
    __name__,
    prefix="auth",
    args={"client_id": r"[\w/.]+"},
    model=server.model.schemas,
)


@app.wrap
def connect_model(handler, main_app):
    """Connect the model to this transaction's database."""
    tx.auth_server = server.model(tx.db)
    yield


@app.wrap
def linkify_head(handler, main_app):
    """Ensure server links are in head of root document."""
    yield
    if tx.request.uri.path == "":
        web.add_rel_links(
            authorization_endpoint="/auth",
            token_endpoint="/auth/tokens",
            ticket_endpoint="/auth/tickets",
        )


def _redeem_authorization_code(flow):
    return server.redeem_authorization_code(
        flow,
        tx.origin,
        tx.host.owner["name"][0],
        tx.host.owner.get("email", [None])[0],
        tx.host.owner.get("photo", [None])[0],
    )


@app.control(r"")
class AuthorizationEndpoint:
    """Identity and resource authorization."""

    def get(self):
        """Return a consent screen for a third-party site sign-in."""
        if not tx.user.is_owner:  # TODO FIXME
            raise web.OK(app.view.root(tx.host.owner, tx.auth_server.get_clients()))
        try:
            client, developer, scopes = server.initiate_auth()
        except web.BadRequest:
            return app.view.authorizations(
                tx.auth_server.get_clients(),
                tx.auth_server.get_active(),
                tx.auth_server.get_revoked(),
            )
        return app.view.consent(client, developer, scopes, server.supported_scopes)

    def post(self):
        """Handle "Profile URL" flow response."""
        return _redeem_authorization_code("profile")


@app.control(r"consent")
class AuthorizationConsent:
    """The authorization consent screen."""

    def post(self):
        """Handle consent screen action."""
        form = web.form("action", scopes=[])
        if form.action == "cancel":
            raise web.SeeOther(tx.user.session["redirect_uri"])
        server.consent(form.scopes)


@app.control(r"tokens")
class TokenEndpoint:
    """Your token endpoint."""

    def get(self):
        """Return a list of tokens to owner otherwise a form to submit a code."""
        # TODO move to library?
        try:
            auth = tx.auth_server.get_auth_from_token(
                str(tx.request.headers["authorization"])
            )
        except IndexError:
            raise web.Forbidden("token could not be found")
        web.header("Content-Type", "application/json")
        return {
            "me": auth["response"]["me"],
            "client_id": auth["client_id"],
            "scope": " ".join(auth["response"]["scope"]),
        }

    def post(self):
        """Handle "Access Token" flow response or revoke an existing access token."""
        # TODO token introspection
        # TODO token verification
        try:
            form = web.form("action", "token")
        except web.BadRequest:
            return _redeem_authorization_code("token")
        if form.action == "revoke":
            server.revoke_auth(form.token)


@app.control(r"tickets")
class TicketEndpoint:
    """Your ticket endpoint."""

    def get(self):
        """Return a list of tickets to owner otherwise a form to submit a ticket."""


@app.control(r"clients")
class Clients:
    """Third-party clients you've used."""

    def get(self):
        """Return a list of clients."""
        return app.view.clients(tx.auth_server.get_clients())


@app.control(r"clients/{client_id}")
class Client:
    """A third-party client."""

    def get(self, client_id):
        """Return given client's authorizations."""
        return app.view.client(tx.auth_server.get_client_auths(client_id))

import dotenv
dotenv.load_dotenv()

import flask as f
import authlib.integrations.flask_client
import werkzeug.middleware.proxy_fix
import os
import datetime
from .validator import signer


app = f.Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')

oauth = authlib.integrations.flask_client.OAuth(app=app)
ryg_login = oauth.register(
    name="ryg_login",
    api_base_url=os.getenv("API_BASE_URL"),  # https://ryg.eu.auth0.com
    authorize_url=os.getenv("AUTHORIZE_URL"),  # https://ryg.eu.auth0.com/authorize
    access_token_url=os.getenv("ACCESS_TOKEN_URL"),  # https://ryg.eu.auth0.com/oauth/token
    server_metadata_url=os.getenv("SERVER_METADATA_URL"),  # https://ryg.eu.auth0.com/.well-known/openid-configuration
    client_kwargs={
        "scope": "profile email openid",
    },
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET")
)

reverse_proxy_app = werkzeug.middleware.proxy_fix.ProxyFix(app=app, x_for=1, x_proto=0, x_host=1, x_port=0, x_prefix=0)



@app.errorhandler(404)
def page_404(_):
    return f.render_template('error.htm', e=404, text="La risorsa che stai cercando è in un altro castello."), 404


@app.route("/typeform/<string:form_user>/<string:form_id>")
def page_typeform(form_user: str, form_id: str):
    f.session["type"] = "typeform"
    f.session["form_user"] = form_user
    f.session["form_id"] = form_id
    return ryg_login.authorize_redirect(redirect_uri=f.url_for("page_auth", _external=True), audience="")


@app.route("/tripetto/<string:form_id>")
def page_tripetto(form_id: str):
    f.session["type"] = "tripetto"
    f.session["form_id"] = form_id
    return ryg_login.authorize_redirect(redirect_uri=f.url_for("page_auth", _external=True), audience="")


@app.route("/authorize")
def page_auth():
    ryg_login.authorize_access_token()
    userdata = ryg_login.get("userinfo").json()

    name, verify_name = str(signer.sign(userdata["name"]), encoding="ascii").split(".")
    sub, verify_sub = str(signer.sign(userdata["sub"]), encoding="ascii").split(".")
    *time, verify_time = str(signer.sign(datetime.datetime.now().isoformat()), encoding="ascii").split(".")
    time = ".".join(time)

    querystring = f"?n={name}&s={sub}&t={time}&vn={verify_name}&vs={verify_sub}&vt={verify_time}"

    if f.session["type"] == "typeform":
        return f.redirect(f"https://{f.session['form_user']}.typeform.com/to/{f.session['form_id']}{querystring}")
    elif f.session["type"] == "tripetto":
        return f.redirect(f"https://tripetto.app/run/{f.session['form_id']}{querystring}")
    else:
        return "No type found", 500


@app.route("/")
def page_root():
    return f.render_template("main.html")


@app.before_request
def add_year_to_global_scope():
    f.g.year = datetime.datetime.now().year
    return None


if __name__ == "__main__":
    # noinspection PyUnreachableCode
    if __debug__:
        app.run(debug=True, host="127.0.0.1", port=30012)
    else:
        raise Exception("This app shouldn't be run standalone in production mode.")

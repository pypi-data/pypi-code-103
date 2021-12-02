from dnastack.constants import *
import click
import webbrowser
import requests
import requests.utils
from time import sleep, time
from urllib.parse import urlparse, parse_qs


def login_with_personal_access_token(
    audience,
    email,
    personal_access_token,
    auth_params=default_auth,
):
    try:
        session = requests.Session()
        # login at /login/token
        login_res = session.get(
            auth_params["url"] + "login/token",
            params={"token": personal_access_token, "email": email},
            allow_redirects=False,
        )

        if not login_res.ok:
            session.close()
            raise Exception(
                "The personal access token and/or email provided is invalid"
            )

        auth_code_res = session.get(
            auth_params["url"] + "oauth/authorize",
            params={
                "response_type": "code",
                "scope": auth_scopes,
                "client_id": auth_params["client"]["id"],
                "redirect_uri": auth_params["client"]["redirect_url"],
                "resource": ",".join(audience),
            },
            allow_redirects=False,
        )

        if "Location" in auth_code_res.headers:
            auth_code_redirect_url = urlparse(auth_code_res.headers["Location"])
        else:
            session.close()
            raise Exception("The authorization failed")

        if "code" in parse_qs(auth_code_redirect_url.query):
            auth_code = parse_qs(auth_code_redirect_url.query)["code"][0]
        else:
            session.close()
            raise Exception("The authorization failed")

        auth_token_res = session.post(
            auth_params["url"] + "oauth/token",
            data={
                "grant_type": "authorization_code",
                "code": auth_code,
                "scope": auth_scopes,
                "resource": ",".join(audience),
                "client_id": auth_params["client"]["id"],
                "client_secret": auth_params["client"]["secret"],
            },
        )

        session.close()

        if auth_token_res.ok:
            return auth_token_res.json()

        raise Exception("Failed to get a token from Wallet")
    except Exception as e:
        raise Exception(f"Could not login with personal access token: {e}")


def login_device_code(audience=None, auth_params=default_auth, open_browser=True):
    try:
        session = requests.Session()

        device_code_res = session.post(
            auth_params["url"] + "oauth/device/code",
            params={
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "client_id": auth_params["client"]["id"],
                "resource": ",".join(audience),
            },
            allow_redirects=False,
        )

        if device_code_res.ok:
            device_code_json = device_code_res.json()

            device_code = device_code_json["device_code"]
            device_verify_uri = device_code_json["verification_uri_complete"]
            poll_interval = int(device_code_json["interval"])
            expiry = time() + int(device_code_json["expires_in"])
            click.echo(f"{device_verify_uri}")

            if open_browser:
                webbrowser.open(device_verify_uri, new=2)
        else:
            try:
                raise Exception(device_code_res.json()["error"])
            except Exception as e:
                raise Exception("Could not receive device code from Wallet")

        while time() < expiry:
            auth_token_res = session.post(
                auth_params["url"] + "oauth/token",
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": device_code,
                    "client_id": auth_params["client"]["id"],
                },
            )

            if auth_token_res.ok:
                session.close()
                click.secho("Login successful!", fg="green")
                return auth_token_res.json()
            elif "error" in auth_token_res.json():
                if auth_token_res.json()["error"] == "access_denied":
                    raise Exception(auth_token_res.json()["error_description"])

            sleep(poll_interval)
        raise Exception("The authorize step timed out.")

    except Exception as e:
        raise Exception(f"Login failed: {e}")


def login_refresh_token(token=None, auth_params=default_auth):
    refresh_token_res = requests.post(
        auth_params["url"] + "oauth/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": token["refresh_token"],
            "scope": token["scope"] if "scope" in token.keys() else auth_scopes,
        },
        auth=(auth_params["client"]["id"], auth_params["client"]["secret"]),
    )
    if refresh_token_res.ok:
        fresh_token = refresh_token_res.json()
        token["access_token"] = fresh_token["access_token"]
        token["expires_in"] = fresh_token["expires_in"]
        return token
    else:
        raise Exception(f"Unable to refresh token: {refresh_token_res.text}")

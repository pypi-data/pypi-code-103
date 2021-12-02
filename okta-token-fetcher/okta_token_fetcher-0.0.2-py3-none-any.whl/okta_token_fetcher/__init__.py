#!/usr/bin/env python3
from argparse import ArgumentParser
import http.server
from urllib.parse import urlparse, parse_qs, urlencode
from time import sleep, time
from os.path import expanduser, isfile
from os import chmod
from requests import get
from requests.exceptions import ConnectionError
from webbrowser import open_new_tab
from threading import Thread
from jwt import decode
from typing import List
from logging import getLogger


LOGGER = getLogger()
LOGGER.setLevel("INFO")


class Handler(http.server.SimpleHTTPRequestHandler):
    """
    Handles requests to the local web server.
    * The first request to the server will be to /ready, which signals that we are ready to browse to the auth server endpoint and the redirect will work
    * The second request is to localhost:8888/, which will get the has from the window.location and redirect back to the server with the correct parameters
    * The third request is to /gettoken, which will parse the id_token from the GET parameters and return it
    """
    id_token: str = None
    token_url: str = None

    # We don't really need any http logging for this
    def log_message(self, format, *args) -> None:
      pass

    def do_GET(s):
      """
      Our request handler
      """
      def get_msg(msg, jwt: str = "") -> str:
        msgs = {
          "redirect": """
          <script>
              hash = window.location.hash.replace(/^#/, "?")
              console.log(hash)
              url = "http://localhost:8888/gettoken" + hash
              console.log(url)
              window.location.href = url
          </script>
          <div style="text-align:center">
              <h1>Redirecting</h1>
          </div>
          """.encode(),
          "auth_failed_msg": """
          <div style="text-align:center">
              <h1>401 NOT AUTHORIZED</h1>
              <h2>____________________________________</h2>
              <h2>Could not log into OKTA</h2>
          </div>
          """.encode(),
          "auth_succeed_msg": f"""
          <script>
              url = new URLSearchParams(window.location.search)
              params = Object.fromEntries(url.entries())
              console.log(params)

              setTimeout(function(){{window.location.href = "https://www.mathewmoon.net/nyancat.gif"}}, 3000)
          </script>
          <div style="text-align:center">
              <h1>Holy crap it worked!</h1>
              <h2>____________________________________</h2>
              <h2>I mean, I knew it would......</h2>
              <div style="background-color:grey"> TOKEN: {jwt} </div>
          </div>
          """.encode()
        }
        return msgs[msg]

      def send_headers(code, res) -> None:
        """
        Sets response headers
        """
        s.send_response(code, res)
        s.send_header('Content-type', 'html')
        s.end_headers()

      req = urlparse(s.path)
      qry = req.query
      req_path = req.path

      if req_path == "/ready":
        send_headers(200, "OK")
        s.wfile.write("ready".encode())

      elif req_path == "/gettoken":
        id_token = parse_qs(qry).get("id_token", [None])[0]
        if id_token is None:
            send_headers(401, "NOT AUTHORIZED")
            s.wfile.write(get_msg("auth_failed_msg"))
            exit(1)
        else:
          send_headers(200, "OK")
          Handler.id_token = id_token
          s.wfile.write(get_msg("auth_succeed_msg", jwt=id_token))

      # This handles any 'other' requests, such as /favicon.ico
      elif req_path == "/":
        send_headers(200, "Redirecting")
        s.wfile.write(get_msg("redirect"))
      else:
        send_headers(404, "NOT FOUND")


def open_link():
  """
  Handles the browser iteraction.
    * Make requests to /ready until we get a 200 and "ready" in the body
    * Open a browser to the auth server url and follow the redirects
    * The server will get the JWT from the dance it does with redirects
  """

  LOGGER.info("You will need to log into OKTA.")
  LOGGER.info("Redirecting you to login.........")
  while True:
      try:
          res = get("http://localhost:8888/ready")
      except ConnectionError:
          sleep(1)
          continue
      if res.content.decode() == "ready":
          open_new_tab(Handler.token_url)
          break
      sleep(1)


class OktaToken:
  """
  Starts an http server that opens a browser window for logging into OKTA (if not already) and retrieves an
  id_token by using a local server as the redirect URI in the OKTA auth url parameters.
  """
  def __init__(
    self,
    url: str,
    client_id: str,
    scopes: List[str] = ["openid"],
    token_type: str = "id_token",
    cache: bool = True
  ) -> None:
    self.url = url
    self.client_id = client_id
    self.scopes = scopes
    self.__token = None

    if "openid" not in scopes:
      scopes.append("openid")

    self.token_type = token_type
    self.cache = cache
    self.cache_path = f"{expanduser('~')}/.okta_token"
    self.token_url = self.make_tokenurl()

    # Kinda hacky, but hey, this whole thing kinda is.....
    Handler.token_url = self.token_url

    self.get_token()

  @property
  def token(self) -> str:
    """
    Returns the stored OKTA token. A new token will be generated if:
      * self.cache == False
      * A token has not been previously cached
      * There is a cached token, but it has expired
    """
    if self.__token is None or not self.is_valid:
      self.get_new_token()
    return self.__token

  def make_tokenurl(self):
    """
    Builds the url sent to the browser for logging in. Taken from:
    https://developer.okta.com/docs/guides/implement-oauth-for-okta/main/#get-an-access-token-and-make-a-request
    """
    uri = "/oauth2/v1/authorize"
    params = {
      "client_id": self.client_id,
      "response_type": self.token_type,
      "nonce": 1234,
      "scope": " ".join(self.scopes),
      "state": "test",
      "redirect_uri": "http://localhost:8888"
    }

    # The replace method is there because urllib does not correctly encode spaces when passing a dict.
    # The other option is building a string from the dict and passing it to urlencode which, IMO, is just as ugly.
    # We know what the parameters are what they will contain, so this shouldn't be an issue.
    param_str = urlencode(params).replace("+", "%20")
    url = f"{self.url}/{uri}?{param_str}"
    return url

  def is_valid(self) -> bool:
    """
    Tests if we can decode the JWT and if it has not expired.
    We DO NOT validate the signature on the token.
    """
    try:
      data = decode(
          self.token,
          algorithms="RS256",
          options={
              "verify_signature": False
          }
      )
    except Exception:
      LOGGER.error("Could not get token expiration")
      return False

    return not data.get("exp", 0) < time()


  def get_token(self) -> str:
    """
    Update self.token and return it. We will generate a new token if:
      * The token is expired
      * self.token is None and self.cache == False
      * There is an error decoding the token
    """
    if (
      not self.cache
      or (not isfile(self.cache_path) and self.cache)
    ):
      return self.get_new_token()

    with open(self.cache_path, "r") as f:
      self.__token = f.read()

    if not self.is_valid():
      LOGGER.info("Auth token is expired. Getting fresh token.")
      self.get_new_token()

    return self.__token

  def get_new_token(self) -> str:
    """
    The big show. This is what we are here for.
      * Start a server to listen for the browser to be redirected to it
      * Make requests to /ready until we get a 200
      * Open a browser to the auth server url and follow the redirects
      * return the JWT from the server class
    """
    s = http.server.HTTPServer(('', 8888), Handler)
    link = Thread(target=open_link, daemon=True)
    link.start()

    while Handler.id_token is None:
        s.handle_request()

    jwt = Handler.id_token

    if self.cache == True:
      with open(self.cache_path, "w+") as f:
        f.write(jwt)

      chmod(self.cache_path, 0o600)

    self.__token = jwt
    return jwt


def run_from_shell() -> str:
  """
  Used as an entrypoint for terminal script. Creates the arguments from OktaToken from cmdline args,
  fetches a token, and logs it to stdout before returning it.
  """
  from sys import stdout
  from logging import basicConfig
  basicConfig(
    stream=stdout,
    format="%(message)s"
  )

  epilog = """
    This script builds off of the dirty quick way to get a token from your browser stated here:
    https://developer.okta.com/docs/guides/implement-oauth-for-okta/main/#get-an-access-token-and-make-a-request .

    This is done by opening a browser window that navigates to the auth server with localhost as the redirect_uri. There
    is an http server that is spun up for just long enough to handle the redirect request and get the id_token from the
    query parameters that are sent via window.hash (I suppose OKTA does this so that it can't be sent to the server itself).

    Note that when using this tool your OKTA JWT will:
      * Be stored in ~/.okta_token (700 file permissions) unless --no-cache is specified
      * Be visible in the url bar of your browser for a few seconds
      * Be visible on the page after all of the redirects for 3 seconds before being redirected to a final page in your browser

    Your OKTA application MUST have "http://localhost:8888" configured as one of the allowed redirect uri's for this tool to work.
  """
  parser = ArgumentParser(epilog=epilog)

  parser.add_argument(
      "-u",
      "--url",
      required=True,
      help="The auth server url. This should be only the domain and protocol. eg: https://mydomain.okta.com"
  )

  parser.add_argument(
      "-c",
      "--client-id",
      required=True,
      help="The client id to get a token for"
  )

  parser.add_argument(
      "-s",
      "--scopes",
      help="Comma delimited list of scopes to request",
      default="openid"
  )

  parser.add_argument(
      "-t",
      "--token-type",
      help="The type of token to request",
      default="id_token"
  )

  parser.add_argument(
      "--no-cache",
      help="Don't cache the token",
      action="store_true"
  )

  args = parser.parse_args()
  args.scopes = args.scopes.split(",")

  fetcher = OktaToken(
      url=args.url,
      client_id=args.client_id,
      scopes=args.scopes,
      token_type=args.token_type,
      cache=not args.no_cache
  )

  LOGGER.info(fetcher.token)
  return fetcher.token

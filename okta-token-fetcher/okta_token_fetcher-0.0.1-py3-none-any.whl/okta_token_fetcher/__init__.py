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
    id_token = None
    token_url = None
    def log_message(self, format, *args):
      pass

    def do_GET(s):
      def get_msg(msg, jwt=""):
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

      def send_headers(code, res):
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
      elif req_path == "/":
        send_headers(200, "Redirecting")
        s.wfile.write(get_msg("redirect"))
      else:
        send_headers(404, "NOT FOUND")


def open_link():
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


#def get_jwt():
#  token = get_token()
#  LOGGER.info(token)
#  return token


class OktaToken:

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
    Handler.token_url = self.token_url
    self.get_token()

  @property
  def token(self) -> str:
    if self.__token is None or not self.is_valid:
      self.get_new_token()
    return self.__token

  def make_tokenurl(self):
    uri = "/oauth2/v1/authorize"
    params = {
      "client_id": self.client_id,
      "response_type": self.token_type,
      "nonce": 1234,
      "scope": " ".join(self.scopes),
      "state": "test",
      "redirect_uri": "http://localhost:8888"
    }
    param_str = urlencode(params).replace("+", "%20")
    url = f"{self.url}/{uri}?{param_str}"
    return url

  def is_valid(self):
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
    if (
      not self.cache
      or (not isfile(self.cache_path) and self.cache)
    ):
      return self.get_new_token()

    with open(self.cache_path, "r") as f:
      self.__token = f.read()

    if not self.is_valid():
      print("NOT VALID")
      LOGGER.info("Auth token is expired. Getting fresh token.")
      self.get_new_token()

    return self.__token

  def get_new_token(self) -> str:
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


def run_from_shell():
  from sys import stdout
  from logging import basicConfig
  basicConfig(
    stream=stdout,
    format="%(message)s"
  )

  parser = ArgumentParser()

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

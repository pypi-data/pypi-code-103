# minecraft_server_updater.py

import logging
import os.path
import re
import sys

import click
import click_log
import click_spinner
import requests
from bs4 import BeautifulSoup

# wire up our logging
log = logging.getLogger()
click_log.basic_config(log)
log.level = logging.INFO

# silence the requests stuff
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class ServerUpdater(object):

    def __init__(self, directory=None, testing=False, suppress_gui=False):

        log.debug("init")
        self.setDirectory(directory)
        self.testing = testing
        self.suppress_gui = suppress_gui
        self.html_url = "https://www.minecraft.net/en-us/download/server"
        self.content = None
        self.soup = None
        self.name = None
        self.jar_url = None

        self.pull_html()
        self.load_soup()
        self.parse_soup()
        self.pull_jar()

    def setDirectory(self, directory):
        if directory is None:
            self.directory = None
            return

        log.debug(f"directory: {input}")

        if os.path.exists(directory):
            self.directory = directory
        else:
            log.critical("directory %s does not exist" % directory)
            sys.exit(2)

    def pull_html(self):
        # pull html file and parse it
        log.debug(f"pull_html {self.html_url}")

        try:
            redirected = requests.head(self.html_url, allow_redirects=True)
            log.debug(redirected.url)
            r = requests.get(redirected.url)
            log.debug(f"status code: {r.status_code}")
            self.content = r.text

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            log.critical(e)
            sys.exit(1)

        # if(not self.testing):
        #     try:
        #         redirected = requests.head(self.html_url, allow_redirects=True)
        #         print(redirected.url)
        #         r = requests.get(redirected.url)
        #         log.debug(f"status code: {r.status_code}")
        #         self.content = r.text
        #     except requests.exceptions.RequestException as e:  # This is the correct syntax
        #         log.critical(e)
        #         sys.exit(1)
        # else:
        #     with open('sample.html', 'r', encoding='utf8') as f:
        #         self.content = f.read()

    def load_soup(self):
        log.debug("load_soup")
        self.soup = BeautifulSoup(self.content, features="html.parser")

    def parse_soup(self):
        log.debug("parse_soup")
        jar_file = self.soup.find('a', href=re.compile(r'launcher'))
        self.name = jar_file.text
        self.jar_url = jar_file.get('href')

    def jar_path(self):
        if(self.directory):
            full_path = os.path.join(self.directory, self.name)
            return full_path
        else:
            return self.name

    def pull_jar(self):
        if(not self.suppress_gui):
            print("downloading : %s" % self.name)

        log.debug(f"pull_jar {self.jar_url}")
        with click_spinner.spinner():
            serverFile = requests.get(self.jar_url)

        open(self.jar_path(), 'wb').write(serverFile.content)


@click.command()
@click.option(
    '-d',
    '--directory',
    'directory',
    default=".",
    help="directory to place file, defaults to pwd"
)
@click.option(
    '-t',
    '--testing',
    is_flag=True,
    default=False
)
@click.option(
    '-no',
    '--nogui',
    is_flag=True,
    default=False,
    help="suppress all output for humans"
)
@click_log.simple_verbosity_option(log)
def main(directory, testing, nogui):
    log.debug("main")
    su = ServerUpdater(directory, testing, nogui)


if __name__ == '__main__':
    main()

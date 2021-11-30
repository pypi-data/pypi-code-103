#!/usr/bin/env python3

# Libervia: an XMPP client
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Run end-to-end tests in appropriate Docker environment"""

import sys, os
from pathlib import Path
import tempfile
from textwrap import dedent
from datetime import datetime
import sh
import io
import sat_templates
import libervia
from sat.core import exceptions
from sat.tools.common import regex
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


OPT_KEEP_CONTAINERS = "--keep-containers"
OPT_KEEP_PROFILES = "--keep-profiles"
OPT_KEEP_VNC = "--keep-vnc"
OPT_KEEP_BROWSER = "--keep-browser"
OPT_VISUAL = "--visual"
OPT_DEV_MODE = "--dev-mode"

dev_mode_inst = dedent("""\
    Here is a short script to start working with a logged account:

    from helium import *
    start_firefox()
    go_to("https://libervia-web.test:8443/login")
    write("account1", "login")
    write("test", "password")
    click("log in")
    """)
report_buffer = io.StringIO()
live_out_buf = []
live_err_buf = []


def live_out(data):
    if live_out_buf:
        # we may get bytes when buffer is reached and we are in the middle of an unicode
        # sequence. In this case we buffer it, and print it when it's complete
        if isinstance(data, str):
            data = b''.join(live_out_buf).decode() + data
            live_out_buf.clear()
        else:
            live_out_buf.append(data)
            return
    try:
        sys.stdout.write(data)
    except TypeError:
        live_out_buf.append(data)
        return
    sys.stdout.flush()
    report_buffer.write(data)


def live_err(data):
    if live_err_buf:
        if isinstance(data, str):
            data = b''.join(live_err_buf).decode() + data
            live_err_buf.clear()
        else:
            live_err_buf.append(data)
            return
    try:
        sys.stderr.write(data)
    except TypeError:
        live_err_buf.append(data)
        return
    sys.stderr.flush()
    report_buffer.write(data)


def get_opt(opt_name):
    """Check is an option flag is set, and remove it for sys.argv

    This allow to have simple flags without interfering with pytest options
    """
    if opt_name in sys.argv:
        sys.argv.remove(opt_name)
        return True
    else:
        return False


def set_env(override, name, value="1"):
    """Set environement variable"""
    environment = override["services"]["backend"].setdefault("environment", {})
    environment[name] = value

def write_report_log(path, log_raw, with_ansi=False):
    log_raw = str(log_raw)
    if with_ansi:
        # we save 2 versions: one with ANSI escape codes
        report_ansi = path.with_suffix(".ansi")
        with report_ansi.open('w') as f:
            f.write(log_raw)
        # and one cleaner, without them
        report_log = path.with_suffix(".log")
        with report_log.open('w') as f:
            f.write(regex.RE_ANSI_REMOVE.sub('', log_raw))
    else:
        report_log = path.with_suffix(".log")
        with report_log.open('w') as f:
            f.write(log_raw)

def use_e2e_env():
    rev = os.getenv("DOCKER_LIBERVIA_REV", "dev")
    print(f"Running tests for Libervia {rev}")
    visual = get_opt(OPT_VISUAL)
    keep_containers = get_opt(OPT_KEEP_CONTAINERS)
    keep_profiles = get_opt(OPT_KEEP_PROFILES)
    keep_vnc = get_opt(OPT_KEEP_VNC)
    keep_browser = get_opt(OPT_KEEP_BROWSER)
    if keep_browser:
        keep_containers = True
        keep_vnc = True
    if keep_vnc:
        visual = True
    dev_mode = get_opt(OPT_DEV_MODE)
    if dev_mode:
        keep_containers = keep_profiles = keep_vnc = visual = True

    for p in Path.cwd().parents:
        package_path = p / "sat"
        docker_path = p / "docker"
        if package_path.is_dir() and docker_path.is_dir():
            backend_root_path = p
            break
    else:
        raise exceptions.NotFound(
            "Can't find root of SàT code, are you sure that you are running the test "
            "from the backend repository?"
        )

    libervia_web_path = Path(libervia.__file__).parent.resolve()
    libervia_web_root_path = libervia_web_path.parent
    if (libervia_web_root_path / ".hg").is_dir():
        libervia_web_source = libervia_web_root_path
        libervia_web_target = "/src/libervia-web"
    else:
        libervia_web_source = libervia_web_path
        libervia_web_target = "/src/libervia-web/libervia"

    sat_templates_path = Path(sat_templates.__file__).parent.resolve()
    sat_templates_root_path = sat_templates_path.parent
    if (sat_templates_root_path / ".hg").is_dir():
        sat_templates_source = sat_templates_root_path
        sat_templates_target = "/src/libervia-templates"
    else:
        sat_templates_source = sat_templates_path
        sat_templates_target = "/src/libervia-templates/sat_templates"

    compose_e2e_path = docker_path / "docker-compose-e2e.yml"
    if not compose_e2e_path.is_file():
        raise exceptions.NotFound('"docker-compose-e2e.yml" file can\'t be found')

    with tempfile.TemporaryDirectory(prefix="libervia_test_e2e_") as temp_dir:
        override_path = Path(temp_dir) / "test_override.yml"
        override = yaml.load(
            dedent(f"""\
                version: "3.6"
                services:
                  backend:
                    volumes:
                      - type: bind
                        source: {backend_root_path}
                        target: /src/libervia-backend
                        read_only: true
                  web:
                    volumes:
                      - type: bind
                        source: {backend_root_path}
                        target: /src/libervia-backend
                        read_only: true
                      - type: bind
                        source: {libervia_web_source}
                        target: {libervia_web_target}
                        read_only: true
                      - type: bind
                        source: {sat_templates_source}
                        target: {sat_templates_target}
                        read_only: true
                """
                   ),
            Loader=Loader
        )

        if keep_profiles:
            set_env(override, "LIBERVIA_TEST_E2E_KEEP_PROFILES")

        if visual:
            set_env(override, "LIBERVIA_TEST_E2E_WEB_NO_HEADLESS")

        if keep_browser:
            set_env(override, "LIBERVIA_TEST_E2E_WEB_KEEP_BROWSER")

        with override_path.open("w") as f:
            yaml.dump(override, f, Dumper=Dumper)

        docker_compose = sh.docker_compose.bake(
            "-f", compose_e2e_path, "-f", override_path)
        docker_compose.up("-d")

        p = docker_compose.exec(
            "--workdir", "/src/libervia-backend/tests", "backend",
            "pytest", "-o", "cache_dir=/tmp", *sys.argv[1:], color="yes",
            _in=sys.stdin, _out=live_out, _out_bufsize=0, _err=live_err, _err_bufsize=0,
            _bg=True
        )
        if visual:
            vnc_port = docker_compose.port("backend", "5900").split(':', 1)[1].strip()
            p_vnc = sh.vncviewer(
                f"localhost:{vnc_port}",
                _bg=True,
                # vncviewer exits with 1 when we send an SIGTERM to it, and it's printed
                # before we can catch it (it's happening in a thread). Thus we set exit
                # code 1 as OK to avoid the backtrace.
                _ok_code=[0, 1]
            )
        else:
            p_vnc = None

        try:
            p.wait()
        except sh.ErrorReturnCode as e:
            libervia_cont_id = docker_compose.ps("-q", "backend").strip()
            report_dest = Path(f"report_{datetime.now().isoformat()}/")
            # we need to make `report_dest` explicitely local with "./", otherwise
            # docker parse takes it as a container path due to the presence of ":"
            # with `isoformat()`.
            sh.docker.cp(f"{libervia_cont_id}:/reports", f"./{report_dest}")
            write_report_log(
                report_dest/"report",
                report_buffer.getvalue(),
                with_ansi=True
            )
            write_report_log(
                report_dest/"backend",
                docker_compose.logs("--no-log-prefix", "backend")
            )
            write_report_log(
                report_dest/"web",
                docker_compose.logs("--no-log-prefix", "web")
            )
            print(f"report saved to {report_dest}")
            sys.exit(e.exit_code)
        finally:
            if p_vnc is not None and p_vnc.is_alive() and not keep_vnc:
                p_vnc.terminate()
            if not keep_containers:
                docker_compose.down(volumes=True)
            if dev_mode:
                print(dev_mode_inst)


if __name__ == "__main__":
    use_e2e_env()

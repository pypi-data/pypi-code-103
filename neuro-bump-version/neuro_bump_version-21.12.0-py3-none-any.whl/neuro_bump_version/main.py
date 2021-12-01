import datetime
import pathlib
import subprocess
import sys

import click
import semver


def find_root() -> pathlib.Path:
    path = pathlib.Path.cwd()
    while path != path.parent:
        if (path / ".git").is_dir():
            return path
        path = path.parent
    raise click.ClickException(
        f"The current path {pathlib.Path.cwd()} is not a part of Git repo"
    )


@click.command()
def main() -> None:
    setup_py = find_root() / "setup.py"
    if not setup_py.exists():
        raise click.ClickException(f"{setup_py} doesn't exist")
    if not setup_py.is_file():
        raise click.ClickException(f"{setup_py} is not a file")
    if "use_scm_version" not in setup_py.read_text():
        raise click.ClickException(f"{setup_py} doesn't contain use_scm_version clause")

    out = subprocess.run(["git", "tag", "-l"], capture_output=True, text=True)
    if out.returncode:
        click.echo(out.stdout, nl=False)
        click.echo(out.stderr, nl=False, err=True)
        sys.exit(out.returncode)
    today = datetime.date.today()
    current = semver.Version(today.year % 100, today.month, 0)
    versions = sorted(
        semver.Version.parse(line.strip()) for line in out.stdout.splitlines()
    )
    versions = [
        v for v in versions if v.major == current.major and v.minor == current.minor
    ]

    if not versions:
        version = current
    else:
        version = versions[-1].next_patch

    click.echo(f"Tag version v{version}:")
    click.secho(f"git tag -a v{version} -m 'Release {version}'", bold=True)
    subprocess.run(
        ["git", "tag", "-a", f"v{version}", "-m", f"Release {version}"],
        check=True,
    )

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


def pyproject_guard(root: pathlib.Path) -> bool:
    fname = root / "pyproject.toml"
    if not fname.exists():
        return False
    if not fname.is_file():
        return False
    if "[tool.setuptools_scm]" not in fname.read_text():
        return False
    return True


def setup_py_guard(root: pathlib.Path) -> bool:
    fname = root / "pyproject.toml"
    if not fname.exists():
        return False
    if not fname.is_file():
        return False
    if "use_scm_version" not in fname.read_text():
        return False
    return True


@click.command()
def main() -> None:
    root = find_root()
    if not pyproject_guard(root) and not setup_py_guard(root):
        raise RuntimeError(
            "There is no pyproject.toml or setup.py that contains "
            "setuptools_scm configuration"
        )

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

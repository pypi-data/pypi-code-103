import datetime
import pathlib
import subprocess
import sys

import click
from packaging.version import Version, parse


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
    current = Version(f"{today.year % 100}.{today.month}.0")
    versions = []
    for line in out.stdout.splitlines():
        try:
            version = parse(line.strip())
            if not isinstance(version, Version):
                # LegacyVersion
                continue
            if version.epoch:
                # Versions with epoch are not semver compliant
                continue
            if version.base_version != str(version):
                # Pre, post, and dev releases are not semver compliant
                continue
            versions.append(version)
        except ValueError:
            pass
    versions = [
        v
        for v in sorted(versions)
        if v.major == current.major and v.minor == current.minor
    ]

    if not versions:
        version = current
    else:
        prev = versions[-1]
        version = Version(f"{prev.major}.{prev.minor}{prev.micro + 1}")

    click.echo(f"Tag version v{version}:")
    click.secho(f"git tag -a v{version} -m 'Release {version}'", bold=True)
    subprocess.run(
        ["git", "tag", "-a", f"v{version}", "-m", f"Release {version}"],
        check=True,
    )

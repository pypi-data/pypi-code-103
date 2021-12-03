from pathlib import Path

import typer

valid_completion_items = [
    ("Camila", "The reader of books."),
    ("Carlos", "The writer of scripts."),
    ("Sebastian", "The type hints guy."),
]


def complete_envfile_names(ctx: typer.Context, incomplete: str):
    for path in Path(
        ctx.params.get("dir")
        or next(param for param in ctx.command.params if param.name == "dir").default
    ).glob(f"{incomplete}*.env"):
        yield path.name


def complete_envfile_dirs(incomplete: str):
    for path in Path(incomplete).glob("*"):
        if path.is_dir():
            yield str(path)


app = typer.Typer()


@app.command()
def main(
    dir: Path = typer.Option(
        Path.cwd() / "envfiles",
        help="Directory with envfiles",
        autocompletion=complete_envfile_dirs,
    ),
    file: Path = typer.Argument(
        ..., help="Envfile to set as .env", autocompletion=complete_envfile_names
    ),
    backup: bool = typer.Option(
        False, help="Backup the current .env file", is_flag=True
    ),
):
    """Switch between envfiles"""
    if backup and Path(".env").exists():
        typer.echo(f"Backing up .env to .env.bak")
        Path(".env.bak").write_text(Path(".env").read_text())
    full_path = Path(dir / file)
    typer.echo(f"Setting {full_path} as .env")
    Path(".env").write_text(
        "\n".join((f"# envswitcher {full_path} #", full_path.read_text()))
    )


if __name__ == "__main__":
    app()

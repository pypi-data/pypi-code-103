import logging
import subprocess
import sys

import typer

app = typer.Typer()

logger = logging.getLogger()


def build_pdf(
    target: str = typer.Argument(
        ...,
        help=(
            "Local folder containing the local LaTeX project."
            "Must contain main.tex file."
        ),
    ),
):
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    typer.echo("Build PDF from LaTeX")
    typer.echo(f"Target folder: {target}")
    typer.echo("Invoking xelatex...")
    try:
        XELATEX_CMD = f'cd {target}; latexmk -f -xelatex -synctex=1 -interaction=nonstopmode -file-line-error -latexoption="-shell-escape" main.tex'
        ret_val = subprocess.run(XELATEX_CMD, shell=True)
        if ret_val.returncode != 0:
            typer.echo(
                f"mklatex returned with a non zero error code, but thePDF was still created"
            )
            typer.Exit(code=1)
    except ValueError as err:
        typer.echo(f"Fatal error while running mklatex")
        typer.Exit(code=1)

    typer.echo(f"mklatex reports success!")
    typer.Exit(code=0)

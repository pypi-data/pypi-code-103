from typing import Optional, List

import pytest
import typer


Models = List[str]

app = typer.Typer()


@app.command()
def test(
    models: Optional[Models] = typer.Option(
        [],
        "--model",
        help="A model to be compiled. This option can be passed multiple times.",
    ),
) -> None:
    """
    Runs tests on data in deployed models. Run this after `amora materialize`
    to ensure that the date state is up-to-date.
    """
    return_code = pytest.main(["-n", "auto"])
    raise typer.Exit(return_code)


if __name__ == "__main__":
    app()

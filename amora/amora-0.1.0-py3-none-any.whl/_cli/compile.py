from typing import Optional, List

import typer

from amora.compilation import amora_model_for_path, compile_statement
from amora.models import (
    list_model_files,
    AmoraModel,
)


Models = List[str]
app = typer.Typer()


@app.command()
def compile(
    models: Optional[Models] = typer.Option(
        [],
        "--model",
        help="A model to be compiled. This option can be passed multiple times.",
    )
) -> None:
    """
    Generates executable SQL from model files. Compiled SQL files are written to the `./target` directory.
    """
    for model_file_path in list_model_files():
        if models and model_file_path.stem not in models:
            continue

        try:
            AmoraModel_class = amora_model_for_path(model_file_path)
        except ValueError:
            continue

        if not issubclass(AmoraModel_class, AmoraModel):  # type: ignore
            continue

        source_sql_statement = AmoraModel_class.source()
        if source_sql_statement is None:
            typer.echo(f"⏭ Skipping compilation of model `{model_file_path}`")
            continue

        target_file_path = AmoraModel_class.target_path(model_file_path)
        typer.echo(
            f"🏗 Compiling model `{model_file_path}` -> `{target_file_path}`"
        )

        content = compile_statement(source_sql_statement)
        target_file_path.write_text(content)


if __name__ == "__main__":
    app()

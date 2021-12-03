import typer
from typing import Optional, List

from amora.models import list_target_files
from amora import materialization


Models = List[str]
app = typer.Typer()


@app.command()
def materialize(
    models: Optional[Models] = typer.Option(
        [],
        "--model",
        help="A model to be compiled. This option can be passed multiple times.",
    ),
    draw_dag: bool = typer.Option(False, "--draw-dag"),
) -> None:
    """
    Executes the compiled SQL againts the current target database.
    """
    model_to_task = {}

    for target_file_path in list_target_files():
        if models and target_file_path.stem not in models:
            continue

        task = materialization.Task.for_target(target_file_path)
        model_to_task[task.model.__name__] = task

    dag = materialization.DependencyDAG.from_tasks(tasks=model_to_task.values())

    if draw_dag:
        dag.draw()

    for model in dag:
        try:
            task = model_to_task[model]
        except KeyError:
            typer.echo(f"⚠️  Skipping `{model}`")
            continue
        else:
            table = materialization.materialize(
                sql=task.sql_stmt, model=task.model
            )
            if table is None:
                continue

            typer.echo(f"✅  Created `{model}` as `{table.full_table_id}`")
            typer.echo(f"    Rows: {table.num_rows}")
            typer.echo(f"    Bytes: {table.num_bytes}")


if __name__ == "__main__":
    app()

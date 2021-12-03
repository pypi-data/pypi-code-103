import json
from dataclasses import dataclass
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table

from amora.compilation import amora_model_for_path
from amora.config import settings
from amora.models import (
    list_model_files,
    AmoraModel,
)
from amora.providers.bigquery import dry_run, DryRunResult


app = typer.Typer()


@dataclass
class ResultItem:
    model: AmoraModel
    dry_run_result: Optional[DryRunResult] = None

    def as_dict(self):
        return {
            "depends_on": self.depends_on,
            "has_source": self.has_source,
            "materialization_type": self.materialization_type,
            "model_name": self.model_name,
            "referenced_tables": self.referenced_tables,
            "total_bytes": self.total_bytes,
        }

    @property
    def model_name(self):
        return self.model.__name__

    @property
    def has_source(self):
        return self.model.source() is not None

    @property
    def depends_on(self) -> List[str]:
        return sorted(
            [dependency.__name__ for dependency in self.model.dependencies()]
        )

    @property
    def total_bytes(self) -> Optional[int]:
        if self.dry_run_result:
            return self.dry_run_result.total_bytes
        return None

    @property
    def referenced_tables(self) -> List[str]:
        if self.dry_run_result:
            return self.dry_run_result.referenced_tables
        return []

    @property
    def materialization_type(self) -> Optional[str]:
        if self.has_source:
            return self.model.__model_config__.materialized.value
        else:
            return None


@app.command(name="list")
def list_models(
    format: str = typer.Option(
        "table",
        help="Output format. Options: json,table",
    ),
    with_total_bytes: bool = typer.Option(
        False,
        help="Uses BigQuery query dry run feature "
        "to gather model total bytes processed information",
    ),
) -> None:
    """
    List the resources in your project

    """
    results = []
    for model_file_path in list_model_files():
        model = amora_model_for_path(model_file_path)
        if with_total_bytes:
            result_item = ResultItem(model=model, dry_run_result=dry_run(model))
        else:
            result_item = ResultItem(model=model, dry_run_result=None)

        results.append(result_item)

    if format == "table":
        table = Table(
            show_header=True,
            header_style="bold",
            show_lines=True,
            width=settings.CLI_CONSOLE_MAX_WIDTH,
            row_styles=["none", "dim"],
        )

        table.add_column("Model name", style="green bold", no_wrap=True)
        table.add_column("Total bytes", no_wrap=True)
        table.add_column("Referenced tables", no_wrap=True)
        table.add_column("Depends on", no_wrap=True)
        table.add_column("Has source?", no_wrap=True, justify="center")
        table.add_column("Materialization", no_wrap=True)

        for result in results:
            table.add_row(
                result.model_name,
                f"{result.total_bytes or '-'}",
                " , ".join(result.referenced_tables) or "-",
                " , ".join(result.depends_on) or "-",
                "🟢" if result.has_source else "🔴",
                result.materialization_type or "-",
            )

        console = Console(width=settings.CLI_CONSOLE_MAX_WIDTH)
        console.print(table)

    elif format == "json":
        output = {"models": [result.as_dict() for result in results]}
        typer.echo(json.dumps(output))


def main():
    return app()

import sys
from pathlib import Path
from typing import Optional

from typer import Argument, Option, Typer

from ldflex import LDFlex
from octadocs.cli.formatters.csv import csv_print
from octadocs.cli.formatters.json import print_json
from octadocs.cli.formatters.pretty import pretty_print
from octadocs.storage import load_graph
from octadocs.types import QueryResultsFormat

app = Typer(name='sparql')


@app.callback(invoke_without_command=True)
def sparql(
    fmt: QueryResultsFormat = Option(
        default=QueryResultsFormat.PRETTY,
        metavar='format',
    ),
    query_text: Optional[str] = Argument(
        None,
        metavar='query',
        help='SPARQL query text. Will be read from stdin if empty.',
    ),
) -> None:
    """Run a SPARQL query against the graph."""
    if query_text is None:
        query_text = sys.stdin.read()

    graph = load_graph(Path.cwd() / '.cache/octadocs')
    ldflex = LDFlex(graph)

    query_result = ldflex.query(query_text)

    {
        QueryResultsFormat.CSV: csv_print,
        QueryResultsFormat.PRETTY: pretty_print,
        QueryResultsFormat.JSON: print_json,
    }[fmt](query_result)   # type: ignore

import typer

from amora.cli import compile, list, materialize, model, test

app = typer.Typer(
    help="Amora Data Build Tool enables engineers to transform data in their warehouses "
    "by defining schemas and writing select statements with SQLAlchemy. Amora handles turning these "
    "select statements into tables and views"
)

app.add_typer(compile.app, name="compile")
app.add_typer(list.app, name="list")
app.add_typer(materialize.app, name="materialize")
# app.add_typer(model.app)
app.add_typer(test.app, name="test")


if __name__ == "__main__":
    app()

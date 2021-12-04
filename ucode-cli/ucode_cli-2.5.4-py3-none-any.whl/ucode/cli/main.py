import typer

from ucode.cli import dsa_command, ucode_command, cf_command

app = typer.Typer()
app.add_typer(dsa_command.app, name="dsa")
app.add_typer(ucode_command.app, name="svr")
app.add_typer(cf_command.app, name="cf")

if __name__ == "__main__":
    app()
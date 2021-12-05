import typer

app_recipe = typer.Typer()


@app_recipe.command("ls")
def list_recipes():
    """
    list recipes
    """
    typer.echo("list all recipes")


@app_recipe.callback()
def recipes():
    """
    manage recipes
    """

import typer

app_ingredient = typer.Typer()


@app_ingredient.command("shop")
def suggest_buy_ingredient():
    typer.echo("suggesting buying ingredient", color=typer.colors.BLUE)


@app_ingredient.callback()
def ingredients():
    """
    manage ingredients
    """

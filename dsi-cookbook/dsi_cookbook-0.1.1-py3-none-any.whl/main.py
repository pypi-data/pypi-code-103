import typer

from dsi_cookbook.commands.ingredient import app_ingredient
from dsi_cookbook.commands.recipe import app_recipe

app = typer.Typer()
app.add_typer(app_recipe, name="recipes")
app.add_typer(app_ingredient, name="ingredients")


@app.callback()
def callback():
    """
    The only cookbook you'll ever need
    """

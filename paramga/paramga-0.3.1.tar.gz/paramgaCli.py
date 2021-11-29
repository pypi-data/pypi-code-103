import click


@click.group()
def cli():
    """Main cli entrypoint."""
    click.echo("Welcome to paramga")


@cli.command()
def run(

):

    click.echo("Complete!")


if __name__ == "__main__":
    ''' Get the config and input data locations from the cli
    Then loads these into the config and runs the model

    '''
    cli()

import click
from functions import parse_file_data, parse_input_string


@click.command()
@click.option('--file', '-f')
def parse_input_data(file=None):
    """
    :param file:
    :param parsestring:
    :param output_file
    :return: Returns Results Table to stdout.
    """
    if file not in [None, " "]:
        result = parse_file_data(file)
        click.echo("League Results Table")
        i = 1
        for k, v in result.iterrows():
            click.echo(f"{i}. {k} : {v[0]} pts", color=True)
            i += 1


if __name__ == '__main__':
    # This is the entry function and will act like a switch
    parse_input_data()

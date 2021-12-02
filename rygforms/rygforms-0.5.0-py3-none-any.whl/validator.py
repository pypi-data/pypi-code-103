import click
import os
import itsdangerous


signer = itsdangerous.Signer(os.getenv('SECRET_KEY'), salt=b"rygforms")


@click.group()
def validator():
    pass


@click.command()
@click.argument("string", type=str, nargs=1)
def sign(string: str):
    value = signer.sign(string)
    click.echo(value)


@click.command()
@click.argument("signature", type=str, nargs=1)
def validate(signature: str):
    try:
        value = signer.validate(signature)
    except itsdangerous.BadData as e:
        click.echo(f"{e!r}", err=True)
        exit(1)
    else:
        click.echo(value)


if __name__ == "__main__":
    validator()

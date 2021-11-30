import click

from hoss.version import __version__, get_server_version, ServerCheckError
from hoss.console import console


@click.command()
@click.option('--endpoint', '-e', type=str, default="http://localhost", show_default=True,
              help="Hoss server endpoint")
def version(endpoint):
    """Print client library and server version info

    /f

    Returns:
        None
    """
    console.print(f"\nHoss client library: v{__version__}")

    try:
        server_version, build = get_server_version(endpoint)
        console.print(f"Hoss server: v{server_version} (build {build})\n")
    except ServerCheckError as err:
        console.print(f"Hoss server: NOT AVAILABLE\n")
        console.print(f"Failed to fetch server version from {endpoint}. If the server is located at a different "
                      f"location, provide the URL via the '--endpoint' option "
                      f"(e.g. '--endpoint https://hos.mydomain.com')")
        console.print(f" - Error: {err}\n\n")


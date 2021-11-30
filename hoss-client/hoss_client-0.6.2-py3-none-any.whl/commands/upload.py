import click
from hoss.tools.upload import upload_directory


@click.command()
@click.argument('dataset_name', metavar='DATASET_NAME', type=str, nargs=1)
@click.argument('directory', type=str, nargs=1)
@click.option('--namespace', '-n', type=str, default="default", show_default=True,
              help="Namespace that contains the dataset")
@click.option('--endpoint', '-e', type=str, default="http://localhost", show_default=True,
              help="Hoss server root endpoint")
@click.option('--skip', '-s', type=str, default="",
              help="Optional regular expression used to filter out files to skip (e.g. myprefix.*\\.txt)")
@click.option('--max_concurrency', '-c', type=int, default=10, show_default=True,
              help="Maximum number of concurrent s3 API transfer operations, defaults to 10.")
@click.option('--multipart_threshold', type=int, default=48, show_default=True,
              help="Threshold in megabytes for which transfers will be split into multiple parts, defaults to 48MB")
@click.option('--metadata', '-m', type=str, multiple=True, default=list(),
              help="Object metadata key-value pair(s) applied to every object uploaded."
                   " You may specify multiple values by repeating the option (e.g. -m foo=bar -m fizz=buzz")
@click.pass_context
def upload(ctx, dataset_name: str, directory: str, namespace: str,
           endpoint: str, skip: str, max_concurrency: int, multipart_threshold: int, metadata: str):
    """Upload files in a directory to an existing dataset"""
    # Convert metadata to dict if it is set, otherwise set to None
    if metadata:
        metadata_pairs = [item.split("=") for item in metadata]
        metadata_dict = dict((k.lower(), v.lower()) for k, v in metadata_pairs)
    else:
        metadata_dict = None

    upload_directory(dataset_name, directory, namespace, endpoint, skip,
                     max_concurrency, multipart_threshold, metadata_dict)

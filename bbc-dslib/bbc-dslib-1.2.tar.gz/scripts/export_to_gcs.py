import argparse
import logging
import os

from dslib import utils
from dslib.google import StorageWrapper
from google.cloud._helpers import _determine_default_project as default_project


# Create argument parser
parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('--source-path', '-s', type=str, required=True,
                    help='Local path (or path pattern) to files and folders to be exported.')
parser.add_argument('--exclude-path', '-e', type=str, required=False, default="''",
                    help='Local path (or path pattern) to files and folders NOT to be exported. Defaults to none.')
parser.add_argument('--archive', '-a', type=str, required=True,
                    help='Path within GCS bucket to upload zipped file to.')
parser.add_argument('--bucket', '-b', type=str, required=True,
                    help='GCS bucket to upload zipped file to.')
parser.add_argument('--project', '-p', type=str, required=False, default=default_project(),
                    help='GCS project to be used. Defaults to default Cloud SDK project.')
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Sets logger to DEBUG level.')

# Parse arguments
args = parser.parse_args()

# Set up logging
utils.configure_logging(level=logging.DEBUG if args.verbose else logging.INFO, detailed=args.verbose)
LOGGER = logging.getLogger(__name__)

# Set needed variables
tmp_filepath = utils.get_tmp_filepath()

# Zip all files and folders except tmp/
with utils.ensure_directory_exists(os.path.dirname(tmp_filepath)):
    utils.zip_files(args.source_path, tmp_filepath, exclude_filepath=args.exclude_path, if_exists='replace')

# Load all this to GCS
storage = StorageWrapper.from_params(args.project, args.bucket)
storage.upload_file(tmp_filepath, args.archive, replace=True)

LOGGER.info('Done')

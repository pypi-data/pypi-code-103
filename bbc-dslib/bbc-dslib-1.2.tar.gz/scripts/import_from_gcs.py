import argparse
import logging
import os

from dslib import utils
from dslib.google import StorageWrapper
from google.cloud._helpers import _determine_default_project as default_project


# Create argument parser
parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('--archive', '-a', type=str, required=True,
                    help='Path within GCS bucket to download zipped file from.')
parser.add_argument('--bucket', '-b', type=str, required=True,
                    help='GCS bucket to download zipped file from.')
parser.add_argument('--project', '-p', type=str, required=False, default=default_project(),
                    help='GCS project to be used. Defaults to default Cloud SDK project.')
parser.add_argument('--target-directory', '-t', type=str, required=False, default='.',
                    help='Local directory to unzip the project file in. Defaults to working directory.')
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Sets logger to DEBUG level.')

# Parse arguments
args = parser.parse_args()

# Set up logging
utils.configure_logging(level=logging.DEBUG if args.verbose else logging.INFO, detailed=args.verbose)
LOGGER = logging.getLogger(__name__)

# Set needed variables
tmp_filepath = utils.get_tmp_filepath()

# Download exported ZIP file from GCS
storage = StorageWrapper.from_params(args.project, args.bucket)
with utils.ensure_directory_exists(os.path.dirname(tmp_filepath)):
    storage.download_file(args.archive, tmp_filepath)

# Zip all files and folders except tmp/
utils.unzip_file(tmp_filepath, args.target_directory)

LOGGER.info('Done')

import argparse
import json
import logging
import os
import sys

from unconcealment import finder
from unconcealment.config import Config, load_file
from unconcealment.result import Result
from unconcealment.secret_pattern import SecretPattern


def collect_sensitive_data(file_path: str, data: str) -> list:
    """ TODO """
    results = []
    for content in data.split('\n'):
        for secret_pattern in SecretPattern:
            secret = finder.extract_secret(content, secret_pattern)
            if secret is not None:
                results.append(Result(file_path, secret_pattern, secret))
    return results


def collect_sensitive_data_from_directory(directory_path: str):
    """ Parse the directory and collect sensitive data """
    sensitive_data = []
    # pylint: disable=W0612:
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            path = os.path.join(root, file)
            sensitive_data.extend(collect_sensitive_data(path, load_file(path)))
    return sensitive_data


def convert_to_json(sensitive_data):
    """ Convert the sensitive data to json """
    return json.dumps(sensitive_data, default=lambda x: x.__dict__).replace("\"file\": null, ", '')


def main():
    """ main """
    parser = argparse.ArgumentParser(description='Detect secrets (AWS, GCP or AZURE keys, NPM tokens etc...)')
    parser.add_argument('-f', '--file', type=str, required=False, help='Input file')
    parser.add_argument('-d', '--directory', type=str, required=False, help='Input directory')
    parser.add_argument('-l', '--log-level', default=logging.INFO, type=lambda x: getattr(logging, x),
                        help="Configure the logging level.")
    parser.add_argument('remainder', nargs=argparse.REMAINDER)
    Config.init(parser)
    logging.debug("Starting the application: %s, %s", Config.log_level(), Config.data())
    sensitive_data = []
    if Config.data() is not None:
        sensitive_data = collect_sensitive_data(Config.file(), Config.data())
    elif Config.directory() is not None:
        sensitive_data = collect_sensitive_data_from_directory(Config.directory())
    if sensitive_data is None or len(sensitive_data) == 0:
        logging.info("No sensitive data found")
        sys.exit(0)
    print(convert_to_json(sensitive_data))
    sys.exit(1)


if __name__ == '__main__':
    main()

import json
import os
import subprocess
from typing import Dict, List, Optional, Tuple

from .util import download_file


class Trombone:

    def __init__(self, jar_path: Optional[str] = None):
        if jar_path is None:
            jar_path = '/tmp/trombone.jar'
            if not os.path.exists(jar_path):
                print(f'Downloading Trombone ({jar_path}). This may take some minutes ...')
                download_file(
                    url='https://github.com/ulaval-rs/pytrombone/raw/main/bin/trombone-5.2.1-jar-with-dependencies.jar',
                    new_file_name=jar_path
                )
                print(f'Trombone ({jar_path}) downloaded.')

        if not os.path.exists(jar_path):
            raise FileNotFoundError(f'pytrombone.jar not found at {jar_path}')

        self.jar_path = jar_path

    def get_version(self):
        output, _ = self.run()
        serialized_output = self.serialize_output(output)

        return serialized_output

    def run(self, key_values: Optional[List[Tuple[str, str]]] = None) -> Tuple[str, str]:
        """Run Trombone with given arguments.

        Args:
            key_values: List of tuples of (key, value) of arguments to give to the Trombone executable.
                        Example: [('tool', 'corpus.DocumentSMOGIndex'), ('storage', 'file')]

        Returns:
            Tuple of (output, error), both in str.
        """
        formatted_args = []
        if key_values:
            formatted_args = [f'{key}={value}' for key, value in key_values]

        process = subprocess.Popen(
            ['java', '-jar', self.jar_path] + formatted_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate()

        return stdout.decode(), stderr.decode()

    def serialize_output(self, output: str) -> Dict:
        index_where_json_start = 0

        for i, c in enumerate(output):
            if c == '{':
                index_where_json_start = i
                break

        return json.loads(output[index_where_json_start:])

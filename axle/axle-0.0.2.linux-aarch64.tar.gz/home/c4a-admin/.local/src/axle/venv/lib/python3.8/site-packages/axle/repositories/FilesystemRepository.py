from flask import abort
from .ABCRepository import ABCRepository, PackageFileListResult, PackageListResult
import requests
import urllib.parse
import pathlib

class FilesystemRepository(ABCRepository):
    def __init__(self, *, path, **kwargs):
        super().__init__(**kwargs)
        self.path = pathlib.Path(path)

    def list_all_packages(self):
        for child in self.path.iterdir():
            if child.is_dir():
                link = f'{child.name}/'
                result.add_result(name = child.name, link=link)

        return result

    def list_all_package_files(self, package_name):
        for child in (self.path / package_name).iterdir():
            if child.is_file():
                link = f'{package_name}/{child.name}'
                result.add_result(name = child.name, link=link)

        return result

    def get_package_file(self, package_name, file_name):
        file_path = self.path / package_name / file_name

        if not file_path.exists():
            abort(404)

        with file_path.open('rb') as fin:
            yield fin


import io
import zipfile
from typing import Any, Dict, Optional, Tuple

from drb import DrbNode
from drb.factory import DrbFactory
from drb.path import ParsedPath
from .execptions import DrbZipNodeException
from .zip_node import DrbZipNode


class DrbFileZipNode(DrbZipNode):

    def __init__(self, base_node: DrbNode):
        super().__init__(parent=base_node.parent, zip_info=None)
        self._file_list = None
        self._zip_file = None
        self._zip_file_source = None
        self.base_node = base_node

    @property
    def parent(self) -> Optional[DrbNode]:
        return self.base_node.parent

    @property
    def path(self) -> ParsedPath:
        return self.base_node.path

    @property
    def name(self) -> str:
        return self.base_node.name

    @property
    def namespace_uri(self) -> Optional[str]:
        return self.base_node.namespace_uri

    @property
    def value(self) -> Optional[Any]:
        return self.base_node.value

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return self.base_node.attributes

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        return self.base_node.get_attribute(name, namespace_uri)

    @property
    def zip_file(self) -> zipfile.ZipFile:
        if self._zip_file is None:
            try:
                if self.base_node.has_impl(io.BufferedIOBase):
                    self._zip_file_source = self.base_node \
                        .get_impl(io.BufferedIOBase)
                elif self.base_node.has_impl(io.BytesIO):
                    self._zip_file_source = self.base_node \
                        .get_impl(io.BytesIO)
                if self._zip_file_source is not None:
                    self._zip_file = zipfile.ZipFile(self._zip_file_source)
                else:
                    raise DrbZipNodeException(f'Unsupported base_node '
                                              f'{type(self.base_node).name} '
                                              f'for DrbFileZipNode')
            except Exception as e:
                raise DrbZipNodeException(f'Unable to read zip file'
                                          f' {self.name} ') from e
        return self._zip_file

    def has_impl(self, impl: type) -> bool:
        return self.base_node.has_impl(impl)

    def get_impl(self, impl: type) -> Any:
        return self.base_node.get_impl(impl)

    def close(self):
        if self._zip_file_source is not None:
            self._zip_file_source.close()
        if self._zip_file is not None:
            self._zip_file.close()
        self.base_node.close()

    def __add_dir_for_path(self, file_info):
        self._file_list.append(file_info)

        if file_info.filename[:-1].find('/') > 0:
            index = file_info.filename[:-1].rindex('/')
            if index > 0:
                path_zip = file_info.filename[:index + 1]
                if path_zip not in self.zip_file.NameToInfo.keys() and \
                        not any(
                            x.filename == path_zip for x in self._file_list):
                    self.__add_dir_for_path(
                        zipfile.ZipInfo(path_zip, file_info.date_time))

    def get_file_list(self):
        if self._file_list is None:
            self._file_list = []
            for fileInfo in self.zip_file.filelist:
                self.__add_dir_for_path(fileInfo)

        return self._file_list

    def _is_a_child(self, filename):
        if '/' not in filename or filename.index('/') == (len(filename) - 1):
            return True
        return False

    def open_entry(self, zip_info: zipfile.ZipInfo):
        # open a entry of the zip en return an BufferedIOBase impl
        return self._zip_file.open(zip_info)


class DrbZipFactory(DrbFactory):

    def _create(self, node: DrbNode) -> DrbNode:
        return DrbFileZipNode(base_node=node)

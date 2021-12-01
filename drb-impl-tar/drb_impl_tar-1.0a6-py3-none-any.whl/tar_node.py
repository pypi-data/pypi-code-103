import datetime
import enum
import io
import tarfile
from typing import Any, List, Dict, Tuple, Optional

import drb

from drb import DrbNode, AbstractNode
from drb.exceptions import DrbNotImplementationException, DrbException
from drb.path import ParsedPath


class DrbTarAttributeNames(enum.Enum):
    SIZE = 'size'
    DIRECTORY = 'directory'
    MODIFIED = 'modified'


class DrbTarNode(AbstractNode):
    supported_impl = {
        io.BufferedIOBase,
        tarfile.ExFileObject
    }

    def __init__(self, parent: DrbNode, tar_info: tarfile.TarInfo):
        self._tar_info = tar_info
        self._attributes: Dict[Tuple[str, str], Any] = None
        self._name = None
        self._parent: DrbNode = parent
        self._children: List[DrbNode] = None
        self._path = None

    @property
    def parent(self) -> Optional[DrbNode]:
        return self._parent

    @property
    def path(self) -> ParsedPath:
        if self._path is None:
            self._path = self.parent.path / self.name
        return self._path

    @property
    def name(self) -> str:
        if self._name is None:
            if self._tar_info.name.endswith('/'):
                self._name = self._tar_info.name[:-1]
            else:
                self._name = self._tar_info.name
            if '/' in self._name:
                self._name = self._name[self._name .rindex('/') + 1:]
        return self._name

    @property
    def namespace_uri(self) -> Optional[str]:
        return None

    @property
    def value(self) -> Optional[Any]:
        return None

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        if self._attributes is None:
            self._attributes = {}
            name_attribute = DrbTarAttributeNames.DIRECTORY.value
            self._attributes[name_attribute, None] = \
                self._tar_info.type == tarfile.DIRTYPE

            name_attribute = DrbTarAttributeNames.SIZE.value
            self._attributes[name_attribute, None] = self._tar_info.size

            date_time = datetime.datetime.fromtimestamp(self._tar_info.mtime)

            name_attribute = DrbTarAttributeNames.MODIFIED.value
            self._attributes[name_attribute, None] = date_time.strftime("%c")

        return self._attributes

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        key = (name, namespace_uri)
        if key in self.attributes.keys():
            return self.attributes[key]
        raise DrbException(f'Attribute not found name: {name}, '
                           f'namespace: {namespace_uri}')

    def get_members(self):
        return self.parent.get_members()

    def _is_a_child(self, filename):
        if not filename.startswith(self._tar_info.name):
            return False

        filename = filename[len(self._tar_info.name):]
        if not filename:
            return False

        if not filename.startswith('/') and \
                not self._tar_info.name.endswith('/'):
            return False

        filename = filename[1:]
        if filename.endswith('/'):
            filename = filename[:-1]

        # Either the name do not contains sep either only one a last position
        return '/' not in filename

    @property
    @drb.resolve_children
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = [DrbTarNode(self, entry) for entry in
                              self.get_members()
                              if self._is_a_child(entry.name)]
            self._children = sorted(self._children,
                                    key=lambda entry_cmp: entry_cmp.name)

        return self._children

    def has_child(self) -> bool:
        return len(self.children) > 0

    def has_impl(self, impl: type) -> bool:
        if impl in self.supported_impl:
            return not self.get_attribute(DrbTarAttributeNames.DIRECTORY.value,
                                          None)

    def get_impl(self, impl: type) -> Any:
        if self.has_impl(impl):
            return self.parent.open_member(self._tar_info)
        raise DrbNotImplementationException(f'no {impl} '
                                            f'implementation found')

    def close(self):
        pass

    def open_member(self, tar_info: tarfile.TarInfo):
        # open a member to retrieve tje implementation
        # back to first parent that is file tar to open it...
        return self.parent.open_member(tar_info)

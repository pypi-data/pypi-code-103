from abc import ABC
from typing import Optional
from heaobject import root


class FileSystem(root.AbstractDesktopObject, ABC):
    """
    Represents a filesystem, which controls how data is stored and retrieved. In HEA, all filesystems are either
    databases or network file storage.
    """
    pass


class MongoDBFileSystem(FileSystem):
    """
    MongoDB-based filesystem.
    """

    def __init__(self):
        super().__init__()
        self.__connection_string: Optional[str] = None
        self.__database_name: Optional[str] = None

    @property  # type: ignore
    def connection_string(self) -> Optional[str]:
        """The MongoDB connection string."""
        return self.__connection_string

    @connection_string.setter
    def connection_string(self, connection_string: Optional[str]):
        self.__connection_string = str(connection_string) if connection_string is not None else None

    @property  # type: ignore
    def database_name(self) -> Optional[str]:
        """The MongoDB database name"""
        return self.__database_name

    @database_name.setter
    def database_name(self, database_name: Optional[str]):
        self.__database_name = str(database_name) if database_name is not None else None


class Volume(root.AbstractDesktopObject):
    """
    A single accessible storage area that stores a single filesystem. Some volumes may require providing credentials in
    order to access them.
    """

    def __init__(self):
        super().__init__()
        self.__file_system_name: FileSystem = DEFAULT_FILE_SYSTEM
        self.__credential_id: Optional[str] = None
        self.__folder_id: Optional[str] = None

    @property  # type: ignore
    def folder_id(self) -> Optional[str]:
        """
        The id of the folder to open when opening this volume.
        """
        return self.__folder_id

    @folder_id.setter
    def folder_id(self, id_) -> None:
        self.__folder_id = str(id_) if id_ is not None else None

    @property  # type: ignore
    def file_system_name(self) -> FileSystem:
        """
        The unique name of this volume's file system (a FileSystem object). Defaults to the 'root' file system.
        """
        return self.__file_system_name

    @file_system_name.setter  # type: ignore
    def file_system_name(self, file_system_name: FileSystem) -> None:
        self.__file_system_name = str(file_system_name) if file_system_name is not None else DEFAULT_FILE_SYSTEM

    @property  # type: ignore
    def credential_id(self) -> Optional[str]:
        """
        The id of the current user's credentials needed to open this volume (a Credentials object), if any.
        """
        return self.__credential_id

    @credential_id.setter  # type: ignore
    def credential_id(self, credentials_id: Optional[str]) -> None:
        self.__credential_id = str(credentials_id) if credentials_id is not None else None


DEFAULT_FILE_SYSTEM = 'DEFAULT_MONGODB'

import locale
import os
import shutil
from tempfile import gettempdir
from typing import (Any, Dict, ItemsView, Iterator, KeysView, List,
                    MutableMapping, MutableSequence, Optional)
from xml.etree.ElementTree import Element, ElementTree

import requests
import win32com.client as win32
from pythoncom import com_error


class ScalaPlayer:

    ERROR_CODES = {
        'software_error': 1010,
        'software_warn': 1000,
        'data_error': 1012,
        'data_warn': 1000
    }

    LANGUAGES = {
        'EN': 0,
        'NL': 1
    }
    _prog_id_scalaplayer = 'ScalaPlayer.ScalaPlayer.1'
    _prog_id_filelock = 'ScalaFileLock.ScalaFileLock.1'
    _prog_id_infoplayer5 = 'Scala.InfoPlayer5'
    _prog_id_netic = 'Scala.InfoNetwork'

    _debug_field = 'Player.debug_python'
    _language_field = 'Player.language'
    _fi_api_field = 'Player.fi_api_key'
    _player_uuid_field = 'Player.uuid'

    _find_me_filename = 'find_me.txt'
    _find_me_path = os.path.join(gettempdir(), _find_me_filename)

    def __init__(self, script: str, main: bool = False) -> None:
        self._script = script
        self.is_main = main
        self.temp_folder = os.path.join(gettempdir(), self._script)

        if not self.is_main:
            self._scalaplayer = win32.Dispatch(self._prog_id_scalaplayer)
            self._netic = win32.Dispatch(self._prog_id_netic)
        else:
            print('This class is run from main. Because of this script will sent messages of whats its doing instead of doing it.')

        self._create_find_me()
        virtual_path = self.install_content(self._find_me_path)

        self.content_folder = os.path.dirname(
            str(self.find_content(virtual_path)))

        self.is_debug = self._get_debug()
        self.language = self._get_language()
        self.fi_api_key = self._get_fi_key()
        self.uuid = self._get_player_uuid()
        self._change_language()

        self.variables = self.Variables(self)

    def log(self, code: str, message: str) -> None:
        if not self.is_main:
            if code in self.ERROR_CODES.keys():
                self._scalaplayer.LogExternalError(
                    self.ERROR_CODES[code], self._script, message)
            else:
                self._scalaplayer.Log(
                    '{} - {} - {}'.format(code, self._script, message))
        else:
            print('{} - {} - {}'.format(code, self._script, message))

    def debug(self, msg: str) -> None:
        if self.is_debug:
            self.log('DEBUG', msg)

    def error(self, msg: str, data: bool = False) -> None:
        if data:
            self.log('data_error', msg)
        else:
            self.log('software_error', msg)

        raise SystemExit

    def warn(self, msg: str, data: bool = False) -> None:
        if data:
            self.log('data_warn', msg)
        else:
            self.log('software_warn', msg)

    def set_debug(self, value: bool):
        self.is_debug = value

    def set_variables(self, variables: Dict[str, Any]) -> None:
        if self.is_main:
            self.variables = variables
        else:
            self.warn(
                'Setting the variables only possible when running python script from main')

    def set_language(self, language: str) -> None:
        self.language = self.LANGUAGES[language]
        self._change_language()

    def quit(self):
        if not self.is_main:
            win32.Dispatch(self._prog_id_infoplayer5).Quit()
        else:
            print('Quiting infoplayer')

    def restart(self):
        if not self.is_main:
            win32.Dispatch(self._prog_id_infoplayer5).RestartPlayback()
        else:
            print('restarting infoplayer')

    def sleep(self, secs: float):
        if not self.is_main:
            self._scalaplayer.Sleep(secs * 1000)
        else:
            print('Sleeping for {} seconds'.format(secs))

    def find_content(self, path: str):
        _path = path.replace('//', '\\')
        content_path = self._lock_content(_path)

        if content_path:
            path = content_path.string
            del content_path
            return path
        else:
            self.error('The path "{}" does not exists'.format(path))

    def install_content(self, abspath: str, subsubfolders: Optional[str] = None):
        if not os.path.isfile(abspath):
            self.error(
                'File "{}" does not exists or is not a file'.format(abspath))

        if not subsubfolders is None:
            subfolder = os.path.join(self._script, subsubfolders)
        else:
            subfolder = self._script

        if not self.is_main:
            try:
                netic: Any = win32.Dispatch(self._prog_id_netic)
                netic.IntegrateContentLocally(abspath, subfolder)
            except com_error as error:
                self.warn('Could not install locally {}'.format(
                    str(error)))

        else:
            print('integrating content from path {} in subfolder {}'.format(
                abspath, subfolder))

        return 'Content:\\{}\\{}'.format(subfolder, os.path.basename(abspath))

    def download_media_temp(self, media_link: str, filename: Optional[str] = None, subsubfolders: Optional[str] = None):
        if filename is None:
            media_filename = media_link.split('/').pop()
        else:
            media_filename = filename

        if subsubfolders is None:
            media_path = os.path.join(self.temp_folder, media_filename)
        else:
            media_path = os.path.join(
                self.temp_folder, subsubfolders, media_filename)

        response = requests.get(media_link, stream=True)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.error('Downloading image {} did not work because requests raised response error {}'.format(
                media_link, str(e)))

        with open(media_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)

        return media_path

    def download_root_temp(self, root: Element, filename: str):
        path = os.path.join(self.temp_folder, filename)
        ElementTree(root).write(path)
        return path

    def _change_language(self):
        if self.language == self.LANGUAGES['EN']:
            language_str = 'en_US'
            try:
                locale.setlocale(locale.LC_TIME, language_str)
            except locale.Error:
                language_str = 'English_America'
                locale.setlocale(locale.LC_TIME, language_str)
        else:
            language_str = 'nl_NL'
            try:
                locale.setlocale(locale.LC_TIME, language_str)
            except locale.Error:
                language_str = 'Dutch_Netherlands'
                locale.setlocale(locale.LC_TIME, language_str)

    def _create_find_me(self):
        with open(self._find_me_path, 'w') as f:
            f.write('find me!')

    def _get_debug(self) -> bool:
        debug_value = self._get_value(self._debug_field)
        return True if debug_value is None else debug_value

    def _get_language(self) -> int:
        language_value = self._get_value(self._language_field)
        return self.LANGUAGES['NL'] if language_value is None else self.LANGUAGES.get(language_value, self.LANGUAGES['NL'])

    def _get_fi_key(self) -> str:
        fi_api_key = self._get_value(self._fi_api_field)
        return '' if fi_api_key is None else fi_api_key

    def _get_player_uuid(self) -> str:
        uuid = self._get_value(self._player_uuid_field)
        return '' if uuid is None else uuid

    def _get_keys(self) -> KeysView[str]:
        if not self.is_main:
            return self._scalaplayer.ListScalaScriptValues()
        else:
            print('Getting keys')
            temp: Dict[str, Any] = {}
            return temp.keys()

    def _get_value(self, key: str) -> Optional[Any]:
        if not self.is_main:
            if key in self._get_keys():
                value: Any = self._scalaplayer.GetScalaScriptValue(key)
                # if isinstance(value, (list, tuple)):
                #     value = self.Array(key, self)
                return value
            else:
                self.warn('variable {} from scala can not be found'.format(key))
                return None
        else:
            print('Getting value')
            return None

    def _set_value(self, key: str, value: Any):
        if not self.is_main:
            if key in self._get_keys():
                self._scalaplayer.SetScalaScriptValue(key, value)
            else:
                self.error(
                    'key {} not found in scalascript values'.format(key))
        else:
            print('Setting value')

    def _lock_content(self, path: str):
        if not self.is_main:
            try:
                lockObj: Any = win32.Dispatch(self._prog_id_filelock)
                path = lockObj.LockScalaFile(path)
                item = self._StringAndLock(path)
                item.lockObj = lockObj
                return item
            except com_error as error:
                self.error('error while locking content {} because of com_error {}'.format(
                    path, str(error)))

        else:
            print('Locking content')
            return None

    class _StringAndLock(str):
        def __init__(self, string: str):
            self.string = string
            self.lockObj: Any = None

        def __del__(self):
            self.lockObj.UnlockScalaFile()

    class Array(MutableSequence[Any]):

        def __init__(self, key: str, scala_player) -> None:
            self._key = key
            self._player: ScalaPlayer = scala_player
            self._item: List[Any] = list(self._player._get_value(self._key))

        def __repr__(self) -> str:
            return str(self)

        def __str__(self):
            return str(self._item)

        def __getitem__(self, index: int):
            return self._item[index]

        def __setitem__(self, index, value):
            self._item[index] = value
            self._player._set_value(self._key, tuple(self._item))

        def __delitem__(self, _):
            self._player.warn(
                'deleting ScalaScript array items is not allowed')

        def __len__(self):
            return len(self._item)

        def insert(self, index: int, value: Any) -> None:
            self._player.warn(
                'inserting ScalaScript array items is not allowed')

        def clear(self) -> None:
            self._player.warn(
                'deleting ScalaScript array items is not allowed')

        def extend(self, values: Any) -> None:
            self._player.warn(
                'extending ScalaScript array items is not allowed')

        def pop(self, index: int = -1):
            self._player.warn(
                'deleting ScalaScript array items is not allowed')

        def remove(self, value: Any):
            self._player.warn(
                'deleting ScalaScript array items is not allowed')

    class Variables(MutableMapping[str, Any]):
        def __init__(self, scala_player) -> None:
            self._player: ScalaPlayer = scala_player

        def __delitem__(self, _) -> None:
            self._player.warn('variable from scala can not be deleted')

        def __iter__(self) -> Iterator[str]:
            for key in self._player._get_keys():
                yield key

        def __len__(self) -> int:
            return len(self._player._get_keys())

        def __getitem__(self, key: str) -> Any:
            return self._player._get_value(key)

        def __setitem__(self, key: str, value: Any):
            if isinstance(value, (tuple, list)):
                _array = self._player.Array(key, self._player)
                for i, element in enumerate(value):
                    _array[i] = element
            else:
                self._player._set_value(key, value)

        def __contains__(self, key: str):
            return (key in self._player._get_keys())

        def keys(self) -> KeysView[str]:
            return self._player._get_keys()

        def items(self) -> ItemsView[str, Any]:
            for key in self._player._get_keys():
                yield key, self._player._get_value(key)

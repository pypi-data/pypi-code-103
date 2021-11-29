
from generallibrary import deco_cache, initBases
from generalfile.optional_dependencies._extension import _Extension

import configparser
import json


class Path_Cfg:
    """ Cfg methods for Path. """
    @property
    @deco_cache()
    def cfg(self):
        """ Easily modify cfg files with a dictionary. """
        return _Cfg(self)


@initBases
class _Cfg(_Extension):
    def write(self, dict_=None, overwrite=False):
        """ Write to this path with a given dictionary. """
        config = configparser.RawConfigParser()
        config.read_dict(dictionary=dict_)
        with self.WriteContext(self.path, overwrite=overwrite) as write_path:
            return write_path.open_operation("w", lambda stream: config.write(stream))

    def _read_json_cast(self, value):
        try:
            return json.loads(value.replace("'", '"'))
        except json.decoder.JSONDecodeError:
            return value

    def read(self, default=...):
        """ Read from this path to get a dictionary. """
        config = configparser.RawConfigParser()
        with self.ReadContext(self.path) as read_path:

            if not read_path.exists():
                if default is Ellipsis:
                    raise FileNotFoundError
                else:
                    return default

            config.read(read_path)
        return {s: {key: self._read_json_cast(value) for key, value in config.items(s)} for s in config.sections()}

    def append(self, dict_):
        """ Update this cfg with a dictionary. """
        with self.AppendContext(self.path) as append_path:
            # append_path.cfg.write(dict_=append_path.cfg.read() | dict_, overwrite=True)
            append_path.cfg.write(dict_={**append_path.cfg.read(), **dict_}, overwrite=True)










































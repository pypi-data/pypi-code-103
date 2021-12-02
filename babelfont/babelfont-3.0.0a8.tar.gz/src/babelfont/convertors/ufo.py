from babelfont import *
from babelfont.convertors.designspace import Designspace
import ufoLib2


class UFO(Designspace):
    suffix = ".ufo"

    @classmethod
    def load(cls, convertor):
        self = cls()
        self.ufo = ufoLib2.Font(convertor.filename)
        self.font = Font()
        return self._load()

    def _load(self):
        self.font.masters = [self._load_master(self.ufo)]
        self._load_metadata(self.ufo)

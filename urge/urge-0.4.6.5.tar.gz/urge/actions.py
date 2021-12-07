import typing as t
from urge import procs

# from .base import Action, action
# from .procs import weather, youdao, browser, memegen, fileoperation
from urge.base import Action, action
from urge.procs import weather, youdao, browser, memegen, fileoperation
from dataclasses import dataclass
from path import Path


class do(Action):
    '''
    Do, do my work\n
    Do my dirty work, scapegoat\n
    '''

    procs = []

    def __init__(self, *args) -> None:
        assert isinstance(self.procs, list)
        for f in args:
            self.procs.append(f)


@dataclass
class web_screenshot(Action):
    url: str
    procs = [browser.web_screenshot]


@dataclass
class get_now_temp(Action):
    city: str
    ascii_graphs: bool = True
    procs = [weather.get_weather, weather.ret_weather]
    # Should add something like this
    # procs = [weather.get_weather, _p(weather.ret_weather,{'ascii_graphs':True})]
    # procs = [weather.get_weather, _p(weather.ret_weather,ascii_graphs=True)]
    # The idea here is turn {"ascii_graphs":True} into self.ascii_graphs=True


@dataclass
class get_simple_temp(Action):
    city: str
    ascii_graphs: bool = False
    procs = [weather.get_weather, weather.ret_weather]


@dataclass
class translate(Action):
    q: str
    full: bool = False
    procs = [youdao.trans_post, youdao.trans_filter]


@dataclass
class simple_translate(Action):
    q: str
    procs = [youdao.simple_translate]


@dataclass
class easy_ocr(Action):
    path: str
    procs = [youdao.pic2base64, youdao.ocr_post, youdao.ocr_ret]


@dataclass
class pic_translate(Action):
    path: str
    procs = [youdao.pic2base64, youdao.pictrans_post, youdao.pictrans_write]


@dataclass
class handwrite_ocr(Action):
    path: str
    procs = [youdao.pic2base64, youdao.ocr_post, youdao.ocr_ret]


@dataclass
class receipt_ocr(Action):
    path: str
    procs = [youdao.pic2base64, youdao.receipt_ocr_post, youdao.receipt_ocr_ret]


@dataclass
class table_ocr(Action):
    path: str
    procs = [youdao.pic2base64, youdao.table_ocr_post, youdao.table_write_excel]


@dataclass
class meme_gen(Action):
    name: str
    up: t.Optional[str]
    down: str
    procs = [memegen.get_meme]


@dataclass
class list_all(Action):
    path: str
    procs = [fileoperation.list_all]


@dataclass
class create(Action):
    path: str
    procs = [fileoperation.create]


@dataclass
class create_folder(Action):
    path: str
    procs = [fileoperation.create_folder]


class find:
    def __init__(self, path: t.Text, pattern: t.Text, recursive=False) -> None:
        self.handler = fileoperation.walk if recursive else fileoperation.find
        self._list = self.handler(path=path, pattern=pattern)
        if isinstance(self._list, t.Generator):
            self._list = list(self._list)
            # when self.__dict__ deepcopy it goes nuts
            # Maybe I can do self.pipe(seed) without deepcopy...

    @action([fileoperation._delete_all])
    def delete(self):
        return dict(f_list=self._list)

    @action([fileoperation._rename_all])
    def rename(self, with_suffix: str = None, with_preafix: str = None):
        return locals()

    @action([fileoperation._zip_files])
    def zip(self, with_folder=False):
        return dict(f_list=self._list, with_folder=with_folder)

    @action([fileoperation])
    def unzip(self):
        ...

    @action([fileoperation._move_all])
    def move(self, dst: str):
        return dict(f_list=self._list, dst=dst)

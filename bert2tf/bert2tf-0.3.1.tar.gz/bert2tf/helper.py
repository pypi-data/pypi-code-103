import asyncio
import os
from typing import Optional, Tuple

if False:
    from uvloop import Loop

_ATTRIBUTES = {'bold': 1,
               'dark': 2,
               'underline': 4,
               'blink': 5,
               'reverse': 7,
               'concealed': 8}

_HIGHLIGHTS = {'on_grey': 40,
               'on_red': 41,
               'on_green': 42,
               'on_yellow': 43,
               'on_blue': 44,
               'on_magenta': 45,
               'on_cyan': 46,
               'on_white': 47
               }

_COLORS = {
    'grey': 30,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37}

_RESET = '\033[0m'


def complete_path(path: str, extra_search_paths: Optional[Tuple[str]] = None) -> str:
    _p = None
    if os.path.exists(path):
        # this checks both abs and relative paths already
        _p = path
    else:
        _p = _search_file_in_paths(path, extra_search_paths)
    if _p:
        return os.path.abspath(_p)
    else:
        raise FileNotFoundError(f'can not find {path}')


def _search_file_in_paths(path, extra_search_paths: Optional[Tuple[str]] = None):
    """searches in all dirs of the PATH environment variable and all dirs of files used in the call stack.
    """
    import inspect
    search_paths = []
    if extra_search_paths:
        search_paths.extend((v for v in extra_search_paths))

    frame = inspect.currentframe()

    # iterates over the call stack
    while frame:
        search_paths.append(os.path.dirname(inspect.getfile(frame)))
        frame = frame.f_back
    search_paths += os.environ['PATH'].split(os.pathsep)

    # return first occurrence of path. If it does not exist, return None.
    for p in search_paths:
        _p = os.path.join(p, path)
        if os.path.exists(_p):
            return _p


def colored(text: str, color: str = None, on_color: str = None, attrs: str = None) -> str:
    fmt_str = '\033[%dm%s'
    if color:
        text = fmt_str % (_COLORS[color], text)

    if on_color:
        text = fmt_str % (_HIGHLIGHTS[on_color], text)

    if attrs:
        if isinstance(attrs, str):
            attrs = [attrs]
        if isinstance(attrs, list):
            for attr in attrs:
                text = fmt_str % (_ATTRIBUTES[attr], text)
    text += _RESET
    return text


def print_load_table(load_stat):
    from .logging import default_logger

    load_table = []
    cached = set()

    for k, v in load_stat.items():
        for cls_name, import_stat, err_reason in v:
            if cls_name not in cached:
                load_table.append('%-5s %-25s %-40s %s' % (
                    colored('✓', 'green') if import_stat else colored('✗', 'red'),
                    cls_name if cls_name else colored('Module load error', 'red'), k, str(err_reason)))
                cached.add(cls_name)
    if load_table:
        load_table.sort()
        load_table = ['', '%-5s %-25s %-40s %-s' % ('Load', 'Class', 'Module', 'Dependency'),
                      '%-5s %-25s %-40s %-s' % ('-' * 5, '-' * 25, '-' * 40, '-' * 10)] + load_table
        default_logger.info('\n'.join(load_table))


def show_ioloop_backend(loop: Optional['Loop'] = None) -> None:
    if loop is None:
        loop = asyncio.get_event_loop()
    from .logging import default_logger
    default_logger.info(f'using {loop.__class__} as event loop')


def get_or_reuse_loop():
    """Get a new eventloop or reuse the current opened eventloop"""
    try:
        loop = asyncio.get_running_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        use_uvloop()
        # no running event loop
        # create a new loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def use_uvloop():
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except (ModuleNotFoundError, ImportError):
        from .logging import default_logger
        default_logger.error(
            'in bert2tf, it uses uvloop to manage events and sockets, Try "pip install uvloop"')


import hashlib
import http.server
import io
import json
import logging
import os
import pathlib
import shutil
import textwrap
import threading
import webbrowser
import zipfile
from functools import partial
from urllib.request import urlopen

from ..procret import registry


__all__ = 'run',

logger = logging.getLogger('procpath')


def install_sqliteviz(zip_url: str, target_dir: pathlib.Path):
    response = urlopen(zip_url)
    with zipfile.ZipFile(io.BytesIO(response.read())) as z:
        z.extractall(target_dir)

    # Make it compatible with Sqliteviz < 0.15 that expects v1 format in
    # "queries.json" and Sqliteviz >= 0.15 that's expects v1 or v2 format
    # in "inquiries.json"
    bundle = json.dumps(list(get_visualisation_bundle()), sort_keys=True)
    for json_name in ('queries.json', 'inquiries.json'):
        (target_dir / json_name).write_text(bundle)


def get_line_chart_config(title: str):
    return {
        'data': [{
            'meta': {'columnNames': {'x': 'ts', 'y': 'value'}},
            'mode': 'lines',
            'type': 'scatter',
            'x': None,
            'xsrc': 'ts',
            'y': None,
            'ysrc': 'value',
            'transforms': [{
                'groups': None,
                'groupssrc': 'pid',
                'meta': {'columnNames': {'groups': 'pid'}},
                'styles': [],
                'type': 'groupby',
            }],
        }],
        'frames': [],
        'layout': {
            'autosize': True,
            'title': {'text': title},
            'xaxis': {
                'autorange': True,
                'range': [],
                'type': 'date'
            },
            'yaxis': {
                'autorange': True,
                'range': [],
                'type': 'linear'
            },
        },
    }


def get_visualisation_bundle():
    """Get Sqliteviz import-able visualisation bundle."""

    for query in registry.values():
        yield {
            'id': hashlib.md5(query.short_query.encode()).hexdigest()[:21],
            'createdAt': '2021-10-29T00:00:00Z',
            'name': query.title,
            'query': textwrap.dedent(query.short_query).strip(),
            'chart': get_line_chart_config(query.title),
        }


def serve_dir(bind: str, port: int, directory: str):
    server_cls = http.server.ThreadingHTTPServer
    handler_cls = partial(http.server.SimpleHTTPRequestHandler, directory=directory)
    with server_cls((bind, port), handler_cls) as httpd:
        httpd.serve_forever()


def run(bind: str, port: int, open_in_browser: bool, reinstall: bool, build_url: str):
    user_cache_dir = pathlib.Path(os.getenv('XDG_CACHE_HOME', os.path.expanduser('~/.cache')))
    sqliteviz_dir = user_cache_dir / 'procpath' / 'sqliteviz'
    if not sqliteviz_dir.exists() or reinstall:
        shutil.rmtree(sqliteviz_dir, ignore_errors=True)
        sqliteviz_dir.mkdir(parents=True)
        logger.info('Downloading %s into %s', build_url, sqliteviz_dir)
        install_sqliteviz(build_url, sqliteviz_dir)
    else:
        logger.info('Serving existing Sqliteviz from %s', sqliteviz_dir)

    url = 'http://{host}:{port}/'.format(port=port, host=bind or 'localhost')
    logger.info('Serving Sqliteviz at %s', url)

    server_fn = partial(serve_dir, bind, port, str(sqliteviz_dir))
    server = threading.Thread(target=server_fn, daemon=True)
    server.start()

    if open_in_browser:
        webbrowser.open(url)

    server.join()

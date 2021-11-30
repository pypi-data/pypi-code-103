# -*- coding: utf-8 -*-
"""收集运行环境变量信息"""
import fast_tracker

from fast_tracker.common.system_info import (total_physical_memory,
                                             logical_processor_count, physical_processor_count)

import sys
import os
import platform

try:
    import fast_tracker.core._thread_utilization
except ImportError:
    pass


def environment_settings():
    env = [('Agent Version', '.'.join(map(str, fast_tracker.version_info))), ('Arch', platform.machine()),
           ('OS', platform.system()), ('OS version', platform.release()),
           ('Total Physical Memory (MB)', total_physical_memory()), ('Logical Processors', logical_processor_count())]

    physical_processor_packages, physical_cores = physical_processor_count()

    if physical_processor_packages:
        env.append(('Physical Processor Packages',
                    physical_processor_packages))

    if physical_cores:
        env.append(('Physical Cores', physical_cores))

    env.append(('Python Program Name', sys.argv[0]))
    env.append(('Python Executable', sys.executable))
    env.append(('Python Home', os.environ.get('PYTHONHOME', '')))
    env.append(('Python Path', os.environ.get('PYTHONPATH', '')))
    env.append(('Python Prefix', sys.prefix))
    env.append(('Python Exec Prefix', sys.exec_prefix))
    env.append(('Python Runtime', '.'.join(platform.python_version_tuple())))
    env.append(('Python Implementation', platform.python_implementation()))
    env.append(('Python Version', sys.version))
    env.append(('Python Platform', sys.platform))
    env.append(('Python Max Unicode', sys.maxunicode))
    extensions = []

    if 'fast_tracker.core._thread_utilization' in sys.modules:
        extensions.append('fast_tracker.core._thread_utilization')
    env.append(('Compiled Extensions', ', '.join(extensions)))

    dispatcher = []

    if not dispatcher and 'mod_wsgi' in sys.modules:
        mod_wsgi = sys.modules['mod_wsgi']
        if hasattr(mod_wsgi, 'process_group'):
            if mod_wsgi.process_group == '':
                dispatcher.append(('Dispatcher', 'Apache/mod_wsgi (embedded)'))
            else:
                dispatcher.append(('Dispatcher', 'Apache/mod_wsgi (daemon)'))
            env.append(('Apache/mod_wsgi Process Group',
                        mod_wsgi.process_group))
        else:
            dispatcher.append(('Dispatcher', 'Apache/mod_wsgi'))
        if hasattr(mod_wsgi, 'version'):
            dispatcher.append(('Dispatcher Version', str(mod_wsgi.version)))
        if hasattr(mod_wsgi, 'application_group'):
            env.append(('Apache/mod_wsgi Application Group',
                        mod_wsgi.application_group))

    if not dispatcher and 'uwsgi' in sys.modules:
        dispatcher.append(('Dispatcher', 'uWSGI'))
        uwsgi = sys.modules['uwsgi']
        if hasattr(uwsgi, 'version'):
            dispatcher.append(('Dispatcher Version', uwsgi.version))

    if not dispatcher and 'flup.server.fcgi' in sys.modules:
        dispatcher.append(('Dispatcher', 'flup/fastcgi (threaded)'))

    if not dispatcher and 'flup.server.fcgi_fork' in sys.modules:
        dispatcher.append(('Dispatcher', 'flup/fastcgi (prefork)'))

    if not dispatcher and 'flup.server.scgi' in sys.modules:
        dispatcher.append(('Dispatcher', 'flup/scgi (threaded)'))

    if not dispatcher and 'flup.server.scgi_fork' in sys.modules:
        dispatcher.append(('Dispatcher', 'flup/scgi (prefork)'))

    if not dispatcher and 'flup.server.ajp' in sys.modules:
        dispatcher.append(('Dispatcher', 'flup/ajp (threaded)'))

    if not dispatcher and 'flup.server.ajp_fork' in sys.modules:
        dispatcher.append(('Dispatcher', 'flup/ajp (forking)'))

    if not dispatcher and 'flup.server.cgi' in sys.modules:
        dispatcher.append(('Dispatcher', 'flup/cgi'))

    if not dispatcher and 'gunicorn' in sys.modules:
        if 'gunicorn.workers.ggevent' in sys.modules:
            dispatcher.append(('Dispatcher', 'gunicorn (gevent)'))
        elif 'gunicorn.workers.geventlet' in sys.modules:
            dispatcher.append(('Dispatcher', 'gunicorn (eventlet)'))
        else:
            dispatcher.append(('Dispatcher', 'gunicorn'))
        gunicorn = sys.modules['gunicorn']
        if hasattr(gunicorn, '__version__'):
            dispatcher.append(('Dispatcher Version', gunicorn.__version__))

    if not dispatcher and 'tornado' in sys.modules:
        dispatcher.append(('Dispatcher', 'tornado'))
        tornado = sys.modules['tornado']
        if hasattr(tornado, 'version_info'):
            dispatcher.append(('Dispatcher Version',
                               str(tornado.version_info)))
    env.extend(dispatcher)
    plugins = []

    for name, module in list(sys.modules.items()):
        if module is None:
            continue

        if name.startswith('fast_tracker.hooks.'):
            plugins.append(name)

        elif name.find('.') == -1 and hasattr(module, '__file__'):
            plugins.append(name)

    env.append(('Plugin List', plugins))

    return env

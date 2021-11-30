# -*- coding: utf-8 -*-
import os
import sys
import time

startup_debug = os.environ.get('FAST_STARTUP_DEBUG', 'off').lower() in ('on', 'true', '1')


def log_message(text, *args):
    if startup_debug:
        text = text % args
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        sys.stdout.write('FAST: %s (%d) - %s\n' % (timestamp,
                                                   os.getpid(), text))
        sys.stdout.flush()


log_message('working_directory = %r', os.getcwd())

log_message('sys.prefix = %r', os.path.normpath(sys.prefix))

try:
    log_message('sys.real_prefix = %r', sys.real_prefix)
except AttributeError:
    pass

log_message('sys.version_info = %r', sys.version_info)
log_message('sys.executable = %r', sys.executable)

if hasattr(sys, 'flags'):
    log_message('sys.flags = %r', sys.flags)

log_message('sys.path = %r', sys.path)

for name in sorted(os.environ.keys()):
    if name.startswith('FAST_') or name.startswith('PYTHON'):
        log_message('%s = %r', name, os.environ.get(name))

import imp

boot_directory = os.path.dirname(__file__)
root_directory = os.path.dirname(os.path.dirname(boot_directory))

log_message('root_directory = %r', root_directory)
log_message('boot_directory = %r', boot_directory)

path = list(sys.path)

if boot_directory in path:
    del path[path.index(boot_directory)]

try:
    (file, pathname, description) = imp.find_module('sitecustomize', path)
except ImportError:
    pass
else:
    log_message('sitecustomize = %r', (file, pathname, description))

    imp.load_module('sitecustomize', file, pathname, description)

expected_python_prefix = os.environ.get('FAST_PYTHON_PREFIX')
actual_python_prefix = os.path.realpath(os.path.normpath(sys.prefix))

expected_python_version = os.environ.get('FAST_PYTHON_VERSION')
actual_python_version = '.'.join(map(str, sys.version_info[:2]))

python_prefix_matches = expected_python_prefix == actual_python_prefix
python_version_matches = expected_python_version == actual_python_version

log_message('python_prefix_matches = %r', python_prefix_matches)
log_message('python_version_matches = %r', python_version_matches)

if python_prefix_matches and python_version_matches:

    config_file = os.environ.get('FAST_CONFIG_FILE', None)
    environment = os.environ.get('FAST_ENVIRONMENT', None)

    log_message('initialize_agent = %r', bool(config_file))

    if config_file:
        do_insert_path = root_directory not in sys.path
        if do_insert_path:
            sys.path.insert(0, root_directory)

        import fast_tracker.config

        log_message('agent_version = %r', fast_tracker.version)

        if do_insert_path:
            try:
                del sys.path[sys.path.index(root_directory)]
            except Exception:
                pass
        fast_tracker.config.initialize(config_file, environment)

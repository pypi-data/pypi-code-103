# -*- coding: utf-8 -*-

import logging
import multiprocessing
import os
import re
import socket
import subprocess
import sys
import threading

from fast_tracker.common.utilization import CommonUtilization

try:
    from subprocess import check_output as _execute_program
except ImportError:
    def _execute_program(*popenargs, **kwargs):

        if 'stdout' in kwargs:
            raise ValueError(
                    'stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE,
                *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd, output=output)
        return output

try:
    import resource
except ImportError:
    pass

_logger = logging.getLogger(__name__)

LOCALHOST_EQUIVALENTS = set([
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '0:0:0:0:0:0:0:0',
    '0:0:0:0:0:0:0:1',
    '::1',
    '::',
])


def logical_processor_count():

    try:
        return multiprocessing.cpu_count()
    except NotImplementedError:
        pass

    # For Jython, we need to query the Java runtime environment.

    try:
        from java.lang import Runtime
        runtime = Runtime.getRuntime()
        res = runtime.availableProcessors()
        if res > 0:
            return res
    except ImportError:
        pass

    # Assuming that Solaris will support POSIX API for querying
    # the number of CPUs. Just in case though, work it out by
    # looking at the devices corresponding to the available CPUs.

    try:
        pseudoDevices = os.listdir('/devices/pseudo/')
        expr = re.compile('^cpuid@[0-9]+$')

        res = 0
        for pd in pseudoDevices:
            if expr.match(pd) is not None:
                res += 1

        if res > 0:
            return res
    except OSError:
        pass

    return 1


def _linux_physical_processor_count(filename=None):

    filename = filename or '/proc/cpuinfo'

    processors = 0
    physical_processors = {}

    try:
        with open(filename, 'r') as fp:
            processor_id = None
            cores = None

            for line in fp:
                try:
                    key, value = line.split(':')
                    key = key.lower().strip()
                    value = value.strip()

                except ValueError:
                    continue

                if key == 'processor':
                    processors += 1

                    if cores and processor_id:
                        physical_processors[processor_id] = cores

                        processor_id = None
                        cores = None

                elif key == 'physical id':
                    processor_id = value

                elif key == 'cpu cores':
                    cores = int(value)

        if cores and processor_id:
            physical_processors[processor_id] = cores

    except Exception:
        pass

    num_physical_processors = len(physical_processors) or (processors
                                        if processors == 1 else None)
    num_physical_cores = sum(physical_processors.values()) or (processors
                                        if processors == 1 else None)

    return num_physical_processors, num_physical_cores


def _darwin_physical_processor_count():

    physical_processor_cmd = ['/usr/sbin/sysctl', '-n', 'hw.packages']

    try:
        num_physical_processors = int(_execute_program(physical_processor_cmd,
            stderr=subprocess.PIPE))
    except (subprocess.CalledProcessError, ValueError):
        num_physical_processors = None

    physical_core_cmd = ['/usr/sbin/sysctl', '-n', 'hw.physicalcpu']

    try:
        num_physical_cores = int(_execute_program(physical_core_cmd,
            stderr=subprocess.PIPE))
    except (subprocess.CalledProcessError, ValueError):
        num_physical_cores = None

    return (num_physical_processors, num_physical_cores)


def physical_processor_count():

    if sys.platform.startswith('linux'):
        return _linux_physical_processor_count()
    elif sys.platform == 'darwin':
        return _darwin_physical_processor_count()

    return None, None


def _linux_total_physical_memory(filename=None):
    filename = filename or '/proc/meminfo'

    try:
        parser = re.compile(r'^(?P<key>\S*):\s*(?P<value>\d*)\s*kB')
        with open(filename, 'r') as fp:
            for line in fp.readlines():
                match = parser.match(line)
                if not match:
                    continue
                key, value = match.groups(['key', 'value'])
                if key == 'MemTotal':
                    memory_bytes = float(value) * 1024
                    return memory_bytes / (1024 * 1024)
    except Exception:
        pass


def _darwin_total_physical_memory():
    command = ['/usr/sbin/sysctl', '-n', 'hw.memsize']

    try:
        return float(_execute_program(command,
                stderr=subprocess.PIPE)) / (1024 * 1024)
    except subprocess.CalledProcessError:
        pass
    except ValueError:
        pass


def total_physical_memory():
    if sys.platform.startswith('linux'):
        return _linux_total_physical_memory()
    elif sys.platform == 'darwin':
        return _darwin_total_physical_memory()


def _linux_physical_memory_used(filename=None):

    filename = filename or '/proc/%d/statm' % os.getpid()

    try:
        with open(filename, 'r') as fp:
            rss_pages = float(fp.read().split()[1])
            memory_bytes = rss_pages * resource.getpagesize()
            return memory_bytes / (1024 * 1024)

    except Exception:
        return 0


def physical_memory_used():

    if sys.platform.startswith('linux'):
        return _linux_physical_memory_used()
    try:
        rusage = resource.getrusage(resource.RUSAGE_SELF)
    except NameError:
        pass
    else:
        if sys.platform == 'darwin':

            memory_bytes = float(rusage.ru_maxrss)
            return memory_bytes / (1024 * 1024)

        elif rusage.ru_maxrss > 0:
            memory_kbytes = float(rusage.ru_maxrss)
            return memory_kbytes / 1024

    return 0


def _resolve_hostname(use_dyno_names, dyno_shorten_prefixes):
    dyno_name = os.environ.get('DYNO')
    if not use_dyno_names or not dyno_name:
        return socket.gethostname()

    for prefix in dyno_shorten_prefixes:
        if prefix and dyno_name.startswith(prefix):
            return '%s.*' % prefix

    return dyno_name


_nr_cached_hostname_lock = threading.Lock()
_nr_cached_ipaddress_lock = threading.Lock()

_nr_cached_hostname = None
_nr_cached_ip_address = None


def gethostname(use_dyno_names=False, dyno_shorten_prefixes=()):

    global _nr_cached_hostname
    global _nr_cached_hostname_lock

    if _nr_cached_hostname:
        return _nr_cached_hostname
    with _nr_cached_hostname_lock:
        if _nr_cached_hostname is None:
            _nr_cached_hostname = _resolve_hostname(use_dyno_names,
                    dyno_shorten_prefixes)

    return _nr_cached_hostname


def getips():
    global _nr_cached_ip_address
    global _nr_cached_ipaddress_lock

    if _nr_cached_ip_address is not None:
        return _nr_cached_ip_address

    with _nr_cached_ipaddress_lock:
        if _nr_cached_ip_address is None:
            _nr_cached_ip_address = []

            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            except Exception:
                return _nr_cached_ip_address

            try:
                s.connect(('1.1.1.1', 1))
                _nr_cached_ip_address.append(s.getsockname()[0])
            except Exception:
                pass
            finally:
                s.close()

    return _nr_cached_ip_address


class BootIdUtilization(CommonUtilization):
    VENDOR_NAME = 'boot_id'
    METADATA_URL = '/proc/sys/kernel/random/boot_id'

    @classmethod
    def fetch(cls):
        if not sys.platform.startswith('linux'):
            return

        try:
            with open(cls.METADATA_URL, 'rb') as f:
                return f.readline().decode('ascii')
        except:
            cls.record_error(cls.METADATA_URL, 'File read error.')
            pass

    @staticmethod
    def get_values(value):
        return value

    @classmethod
    def sanitize(cls, value):
        if value is None:
            return

        stripped = value.strip()

        if len(stripped) != 36:
            cls.record_error(cls.METADATA_URL, stripped)

        return stripped[:128] or None

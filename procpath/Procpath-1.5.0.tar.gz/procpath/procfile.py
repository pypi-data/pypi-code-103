"""
This module represents several Procfs [1]_ sources.

.. [1] https://www.kernel.org/doc/html/latest/filesystems/proc.html
"""

import os
import stat
from collections import Counter
from functools import partial, wraps
from typing import List, NamedTuple, NamedTupleMeta, Optional


__all__ = 'registry',

registry = {}


def read_file(fn):
    """Wrap target function to pass it bytes read from the filename."""

    @wraps(fn)
    def wrapper(filename, **kwargs):
        with open(filename, 'rb') as f:
            return fn(f.read(), **kwargs)

    wrapper.schema = fn.schema
    wrapper.empty = fn.empty

    return wrapper


class Stat(NamedTuple):
    """
    Representation of ``/proc/{pid}/stat``, see ``man proc``.

    Fields are read up until ``rss`` plus the range from
    ``delayacct_blkio_ticks`` to ``cguest_time``. Other fields don't
    seem to be useful for the monitoring purposes.

    Formats of the fields are defined in C `printf`_ syntax.

    .. _printf: http://www.cplusplus.com/reference/cstdio/printf/
    """

    pid: int
    """
    The process ID.

    :format: %d
    """

    comm: str
    """
    The filename of the executable. This is visible whether or not the
    executable is swapped out.

    :format: %s
    """

    state: str
    """
    One of the following characters, indicating process state:

        R  Running

        S  Sleeping in an interruptible wait

        D  Waiting in uninterruptible disk sleep

        Z  Zombie

        T  Stopped (on a signal) or (before Linux 2.6.33)
           trace stopped

        t  Tracing stop (Linux 2.6.33 onward)

        W  Paging (only before Linux 2.6.0)

        X  Dead (from Linux 2.6.0 onward)

        x  Dead (Linux 2.6.33 to 3.13 only)

        K  Wakekill (Linux 2.6.33 to 3.13 only)

        W  Waking (Linux 2.6.33 to 3.13 only)

        P  Parked (Linux 3.9 to 3.13 only)

    :format: %c
    """

    ppid: int
    """
    The PID of the parent of this process.

    :format: %d
    """

    pgrp: int
    """
    The process group ID of the process.

    :format: %d
    """

    session: int
    """
    The session ID of the process.

    :format: %d
    """

    tty_nr: int
    """
    The controlling terminal of the process. (The minor device number
    is contained in the combination of bits 31 to 20 and 7 to 0; the
    major device number is in bits 15 to 8.)

    :format: %d
    """

    tpgid: int
    """
    The ID of the foreground process group of the controlling terminal
    of the process.

    :format: %d
    """

    flags: int
    """
    The kernel flags word of the process.  For bit meanings, see the
    PF_* defines in the Linux kernel source file include/linux/sched.h.
    Details depend on the kernel version.

    The format for this field was %lu before Linux 2.6.

    :format: %u
    """

    minflt: int
    """
    The number of minor faults the process has made
    which have not required loading a memory page from disk.

    :format: %lu
    """

    cminflt: int
    """
    The number of minor faults that the process's
    waited-for children have made.

    :format: %lu
    """

    majflt: int
    """
    The number of major faults the process has made
    which have required loading a memory page from disk.

    :format: %lu
    """

    cmajflt: int
    """
    The number of major faults that the process's
    waited-for children have made.

    :format: %lu
    """

    utime: int
    """
    Amount of time that this process has been scheduled
    in user mode, measured in clock ticks (divide by
    sysconf(_SC_CLK_TCK)).  This includes guest time,
    guest_time (time spent running a virtual CPU, see
    below), so that applications that are not aware of
    the guest time field do not lose that time from
    their calculations.

    :format: %lu
    """

    stime: int
    """
    Amount of time that this process has been scheduled
    in kernel mode, measured in clock ticks (divide by
    sysconf(_SC_CLK_TCK)).

    :format: %lu
    """

    cutime: int
    """
    Amount of time that this process's waited-for children have been
    scheduled in user mode, measured in clock ticks (divide by
    sysconf(_SC_CLK_TCK)). (See also times(2).)  This includes guest
    time, cguest_time (time spent running a virtual CPU, see below).

    :format: %ld
    """

    cstime: int
    """
    Amount of time that this process's waited-for children have been
    scheduled in kernel mode, measured in clock ticks (divide by
    sysconf(_SC_CLK_TCK)).

    :format: %ld
    """

    priority: int
    """
    (Explanation for Linux 2.6) For processes running a
    real-time scheduling policy (policy below; see
    sched_setscheduler(2)), this is the negated schedul‐
    ing priority, minus one; that is, a number in the
    range -2 to -100, corresponding to real-time priori‐
    ties 1 to 99.  For processes running under a non-
    real-time scheduling policy, this is the raw nice
    value (setpriority(2)) as represented in the kernel.
    The kernel stores nice values as numbers in the
    range 0 (high) to 39 (low), corresponding to the
    user-visible nice range of -20 to 19.

    Before Linux 2.6, this was a scaled value based on
    the scheduler weighting given to this process.

    :format: %ld
    """

    nice: int
    """
    The nice value (see setpriority(2)), a value in the
    range 19 (low priority) to -20 (high priority).

    :format: %ld
    """

    num_threads: int
    """
    Number of threads in this process (since Linux 2.6).
    Before kernel 2.6, this field was hard coded to 0 as
    a placeholder for an earlier removed field.

    :format: %ld
    """

    itrealvalue: int
    """
    The time in jiffies before the next SIGALRM is sent to the process
    due to an interval timer.  Since kernel 2.6.17, this field is no
    longer maintained, and is hard coded as 0.

    :format: %ld
    """

    starttime: int
    """
    The time the process started after system boot. In
    kernels before Linux 2.6, this value was expressed
    in jiffies.  Since Linux 2.6, the value is expressed
    in clock ticks (divide by sysconf(_SC_CLK_TCK)).

    The format for this field was %lu before Linux 2.6.

    :format: %llu
    """

    vsize: int
    """
    Virtual memory size in bytes.

    :format: %lu
    """

    rss: int
    """
    Resident Set Size: number of pages the process has
    in real memory.  This is just the pages which count
    toward text, data, or stack space.  This does not
    include pages which have not been demand-loaded in,
    or which are swapped out.

    :format: %ld
    """

    delayacct_blkio_ticks: int = None
    """
    Aggregated block I/O delays, measured in clock
    ticks (centiseconds). Available since Linux 2.6.18.

    :format: %llu
    """

    guest_time: int = None
    """
    Guest time of the process (time spent running a
    virtual CPU for a guest operating system), measured
    in clock ticks (divide by sysconf(_SC_CLK_TCK)).
    Available since Linux 2.6.24.

    :format: %lu
    """

    cguest_time: int = None
    """
    Guest time of the process's children, measured in clock ticks
    (divide by sysconf(_SC_CLK_TCK)). Available since Linux 2.6.24.

    :format: %ld
    """

    @classmethod
    def from_bytes(cls, b):
        pid, _, rest = b.partition(b' (')
        comm, _, rest = rest.rpartition(b') ')
        state, _, rest = rest.partition(b' ')
        fields = [int(pid), comm.decode(), state.decode()]

        read_fields = 41  # cguest_time is 44th, -3 for already read fields
        raw = rest.split(b' ', maxsplit=read_fields)[:read_fields]
        del raw[21:38]  # rsslim is 24th, delayacct_blkio_ticks is 41th, -3
        fields.extend(map(int, raw))

        return cls(*fields)

def read_stat(b, *, dictcls=dict, **kwargs):
    return dictcls(zip(Stat._fields, Stat.from_bytes(b)))

read_stat.schema = Stat
read_stat.empty = Stat(*[None] * len(Stat._fields))._asdict()
registry['stat'] = read_file(read_stat)


def read_cmdline(b, **kwargs):
    return b.replace(b'\x00', b' ').strip().decode()

read_cmdline.schema = 'cmdline'
read_cmdline.empty = None
registry['cmdline'] = read_file(read_cmdline)


class Io(NamedTuple):
    """Representation of ``/proc/{pid}/io``, see ``man proc``."""

    rchar: int
    """
    I/O counter: chars read.

    The number of bytes which this task has caused to be read from
    storage. This is simply the sum of bytes which this process passed
    to read() and pread(). It includes things like tty IO and it is
    unaffected by whether or not actual physical disk IO was required
    (the read might have been satisfied from pagecache).
    """

    wchar: int
    """
    I/O counter: chars written.

    The number of bytes which this task has caused, or shall cause to
    be written to disk. Similar caveats apply here as with rchar.
    """

    syscr: int
    """
    I/O counter: read syscalls.

    Attempt to count the number of read I/O operations, i.e. syscalls
    like read() and pread().
    """

    syscw: int
    """
    I/O counter: write syscalls.

    Attempt to count the number of write I/O operations, i.e. syscalls
    like write() and pwrite().
    """

    read_bytes: int
    """
    I/O counter: bytes read.

    Attempt to count the number of bytes which this process really did
    cause to be fetched from the storage layer. Done at the
    submit_bio() level, so it is accurate for block-backed filesystems.
    """

    write_bytes: int
    """
    I/O counter: bytes written.

    Attempt to count the number of bytes which this process caused to
    be sent to the storage layer. This is done at page-dirtying time.
    """

    cancelled_write_bytes: int
    """
    The big inaccuracy here is truncate. If a process writes 1MB to a
    file and then deletes the file, it will in fact perform no
    writeout. But it will have been accounted as having caused 1MB of
    write. In other words: The number of bytes which this process
    caused to not happen, by truncating pagecache. A task can cause
    "negative" IO too. If this task truncates some dirty pagecache,
    some IO which another task has been accounted for (in its
    write_bytes) will not be happening. We _could_ just subtract that
    from the truncating task's write_bytes, but there is information
    loss in doing that.
    """

    @classmethod
    def from_bytes(cls, b):
        pairs = [line.decode().split(': ', 1) for line in b.splitlines()]
        d = {k: int(v) for k, v in pairs if k in cls._field_set}
        return cls(**d)

Io._field_set = set(Io._fields)

def read_io(b, *, dictcls=dict, **kwargs):
    return dictcls(zip(Io._fields, Io.from_bytes(b)))

read_io.schema = Io
read_io.empty = Io(*[None] * len(Io._fields))._asdict()
registry['io'] = read_file(read_io)


class StatusMeta(NamedTupleMeta):
    """Metaclass for ``(in_type, out_type)`` annotated named tuple."""

    def __new__(cls, typename, bases, ns):
        field_conv_map = {}
        types = ns.get('__annotations__', {})
        for field_name, annotation in types.items():
            assert isinstance(annotation, tuple)
            field_conv_map[field_name] = annotation[0]
            types[field_name] = annotation[1]

        rescls = super().__new__(cls, typename, bases, ns)
        rescls._field_conv_map = field_conv_map

        field_types = rescls.__annotations__
        rescls._optional_none = {f: None for f, t in field_types.items() if Optional[t] == t}

        return rescls

class Status(NamedTuple, metaclass=StatusMeta):
    """Representation of ``/proc/{pid}/status``, see ``man proc``."""

    def _kb(s) -> int:  # @NoSelf
        return int(s.split(maxsplit=1)[0])

    def _slashed_pair(s) -> List[int]:  # @NoSelf
        a, _, b = s.partition('/')
        return [int(a), int(b)]

    def _whitespace_separated_list(s) -> List[int]:  # @NoSelf
        return [int(v) for v in s.split()]

    def _comma_separated_hex_list(s) -> List[int]:  # @NoSelf
        return [int(h, 16) for h in s.split(',')]

    def _state(s) -> str:  # @NoSelf
        return s.split(maxsplit=1)[0].upper()

    name: (str, str)
    """
    Command run by this process.  Strings longer than TASK_COMM_LEN
    (16) characters (including the terminating null byte) are silently
    truncated.
    """

    umask: (partial(int, base=8), Optional[int])
    """Process umask; see umask(2) (since Linux 4.7)."""

    state: (_state, str)
    """
    Current state of the process. One of:

    - R (running)
    - S (sleeping)
    - D (disk sleep)
    - T (stopped)
    - t (tracing stop)
    - Z (zombie)
    - X (dead)

    Only the letter code is kept.
    """

    tgid: (int, int)
    """Thread group ID (i.e., Process ID)."""

    ngid: (int, Optional[int])
    """NUMA group ID (0 if none; since Linux 3.13)."""

    pid: (int, int)
    """Thread ID (see gettid(2))."""

    ppid: (int, int)
    """PID of parent process."""

    tracerpid: (int, int)
    """
    PID of process tracing this process (0 if not being traced).
    """

    uid: (_whitespace_separated_list, List[int])
    """Real, effective, saved set, and filesystem UIDs."""

    gid: (_whitespace_separated_list, List[int])
    """Real, effective, saved set, and filesystem GIDs."""

    fdsize: (int, int)
    """Number of file descriptor slots currently allocated."""

    groups: (_whitespace_separated_list, List[int])
    """Supplementary group list."""

    nstgid: (_whitespace_separated_list, Optional[List[int]])
    """
    Thread group ID (i.e., PID) in each of the PID namespaces of which
    [pid] is a member. The leftmost entry shows the value with respect
    to the PID namespace of the process that mounted this procfs (or
    the root namespace if mounted by the kernel), followed by the value
    in successively nested inner namespaces (since Linux 4.1).
    """

    nspid: (_whitespace_separated_list, Optional[List[int]])
    """
    Thread ID in each of the PID namespaces of which [pid] is a member.
    The fields are ordered as for NStgid (since Linux 4.1).
    """

    nspgid: (_whitespace_separated_list, Optional[List[int]])
    """
    Process group ID in each of the PID namespaces of which [pid] is a
    member. The fields are ordered as for NStgid (since Linux 4.1).
    """

    nssid: (_whitespace_separated_list, Optional[List[int]])
    """
    Descendant namespace session ID hierarchy Session ID in each of the
    PID namespaces of which [pid] is a member. The fields are ordered
    as for NStgid (since Linux 4.1).
    """

    vmpeak: (_kb, Optional[int])
    """Peak virtual memory size, in kB."""

    vmsize: (_kb, Optional[int])
    """Virtual memory size, in kB."""

    vmlck: (_kb, Optional[int])
    """Locked memory size, in kB (see mlock(2))."""

    vmpin: (_kb, Optional[int])
    """
    Pinned memory size (since Linux 3.2). These are pages that can't be
    moved because something needs to directly access physical memory,
    in kB.
    """

    vmhwm: (_kb, Optional[int])
    """Peak resident set size, in kB ("high water mark")."""

    vmrss: (_kb, Optional[int])
    """
    Resident set size, in kB. Note that the value here is the sum of
    RssAnon, RssFile, and RssShmem.
    """

    rssanon: (_kb, Optional[int])
    """Size of resident anonymous memory, in kB (since Linux 4.5)."""

    rssfile: (_kb, Optional[int])
    """Size of resident file mappings, in kB (since Linux 4.5)."""

    rssshmem: (_kb, Optional[int])
    """
    Size of resident shared memory, in kB (includes System V shared
    memory, mappings from tmpfs(5), and shared anonymous mappings).
    (since Linux 4.5).
    """

    vmdata: (_kb, Optional[int])
    """Size of data, in kB."""

    vmstk: (_kb, Optional[int])
    """Size of stack, in kB."""

    vmexe: (_kb, Optional[int])
    """Size of text segments, in kB."""

    vmlib: (_kb, Optional[int])
    """Shared library code size, in kB."""

    vmpte: (_kb, Optional[int])
    """Page table entries size, in kB (since Linux 2.6.10)."""

    vmpmd: (_kb, Optional[int])
    """
    Size of second-level page tables, in kB
    (added in Linux 4.0; removed in Linux 4.15).
    """

    vmswap: (_kb, Optional[int])
    """
    Swapped-out virtual memory size by anonymous private pages, in kB;
    shmem swap usage is not included (since Linux 2.6.34).
    """

    hugetlbpages: (_kb, Optional[int])
    """
    Size of hugetlb memory portions, in kB (since Linux 4.4).
    """

    coredumping: (int, Optional[int])
    """
    Contains the value 1 if the process is currently dumping core, and
    0 if it is not (since Linux 4.15). This information can be used by
    a monitoring process to avoid killing a process that is currently
    dumping core, which could result in a corrupted core dump file.
    """

    threads: (int, int)
    """Number of threads in process containing this thread."""

    sigq: (_slashed_pair, List[int])
    """
    This field contains two numbers that relate to queued signals for
    the real user ID of this process.  The first of these is the number
    of currently queued signals for this real user ID, and the second
    is the resource limit on the number of queued signals for this
    process (see the description of RLIMIT_SIGPENDING in getrlimit(2)).
    """

    sigpnd: (partial(int, base=16), int)
    """
    Mask of signals pending for thread (see pthreads(7) and signal(7)).
    """

    shdpnd: (partial(int, base=16), int)
    """
    Mask of signals pending for process as a whole (see pthreads(7)
    and signal(7)).
    """

    sigblk: (partial(int, base=16), int)
    """Masks indicating signals being blocked (see signal(7))."""

    sigign: (partial(int, base=16), int)
    """Masks indicating signals being ignored (see signal(7))."""

    sigcgt: (partial(int, base=16), int)
    """Masks indicating signals being caught (see signal(7))."""

    capinh: (partial(int, base=16), int)
    """
    Masks of capabilities enabled in inheritable sets
    (see capabilities(7)).
    """

    capprm: (partial(int, base=16), int)
    """
    Masks of capabilities enabled in permitted sets
    (see capabilities(7)).
    """

    capeff: (partial(int, base=16), int)
    """
    Masks of capabilities enabled in effective sets
    (see capabilities(7)).
    """

    capbnd: (partial(int, base=16), Optional[int])
    """
    Capability bounding set (since Linux 2.6.26, see capabilities(7)).
    """

    capamb: (partial(int, base=16), Optional[int])
    """
    Ambient capability set (since Linux 4.3, see capabilities(7)).
    """

    nonewprivs: (int, Optional[int])
    """
    Value of the no_new_privs bit (since Linux 4.10, see prctl(2)).
    """

    seccomp: (int, Optional[int])
    """
    Seccomp mode of the process (since Linux 3.8, see seccomp(2)).

    - 0 means SECCOMP_MODE_DISABLED
    - 1 means SECCOMP_MODE_STRICT
    - 2 means SECCOMP_MODE_FILTER

    This field is provided only if the kernel was built with the
    CONFIG_SECCOMP kernel configuration option enabled.
    """

    speculation_store_bypass: (str.strip, Optional[str])
    """
    Speculation flaw mitigation state (since Linux 4.17, see prctl(2)).
    """

    cpus_allowed: (partial(int, base=16), Optional[int])
    """
    Mask of CPUs on which this process may run
    (since Linux 2.6.24, see cpuset(7)).
    """

    cpus_allowed_list: (str.strip, Optional[str])
    """
    Same as previous, but in "list format"
    (since Linux 2.6.26, see cpuset(7)).
    """

    mems_allowed: (_comma_separated_hex_list, Optional[List[int]])
    """
    Mask of memory nodes allowed to this process
    (since Linux 2.6.24, see cpuset(7)).
    """

    mems_allowed_list: (str.strip, Optional[str])
    """
    Same as previous, but in "list format"
    (since Linux 2.6.26, see cpuset(7)).
    """

    voluntary_ctxt_switches: (int, Optional[int])
    """Number of voluntary context switches (since Linux 2.6.23)."""

    nonvoluntary_ctxt_switches: (int, Optional[int])
    """Number of involuntary context switches (since Linux 2.6.23)."""

    @classmethod
    def from_bytes(cls, b):
        fields = {}
        # decode order is important for PyPy performance
        nameline, rest = b.split(b'\n', 1)
        fields['name'] = nameline.decode().split(':', 1)[1].strip()
        for line in rest.lower().decode().splitlines():
            k, _, v = line.partition(':')
            if k in cls._field_conv_map:
                fields[k] = cls._field_conv_map[k](v)

        return cls(**{**cls._optional_none, **fields})

def read_status(b, *, dictcls=dict, **kwargs):
    return dictcls(zip(Status._fields, Status.from_bytes(b)))

read_status.schema = Status
read_status.empty = Status(*[None] * len(Status._fields))._asdict()
registry['status'] = read_file(read_status)


class Fd(NamedTuple):
    """
    Counts of file descriptor types in ``/proc/{pid}/fd/*``.

    For more details see ``man proc`` and ``man fstat``.
    """

    anon: int = 0
    """
    For file descriptors that have no corresponding inode (e.g., file
    descriptors produced by epoll_create(2), eventfd(2),
    inotify_init(2), signalfd(2), and timerfd(2)), the entry will be a
    symbolic link with contents of the form::

        anon_inode:<file-type>

    In some cases, the file-type is surrounded by square brackets like:

    - ``anon_inode:[eventfd]``
    - ``anon_inode:[eventpoll]``
    - ``anon_inode:[timerfd]``
    - ``anon_inode:[signalfd]``
    - ``anon_inode:inotify``
    - ``anon_inode:dmabuf``
    - ``anon_inode:sync_fence``

    """

    dir: int = 0
    """Directory."""

    chr: int = 0
    """Character device."""

    blk: int = 0
    """Block device."""

    reg: int = 0
    """Regular file."""

    fifo: int = 0
    """FIFO (named pipe)."""

    lnk: int = 0
    """Symbolic link."""

    sock: int = 0
    """Socket file."""

    _lookup = {
        0: 'anon',
        stat.S_IFDIR: 'dir',
        stat.S_IFCHR: 'chr',
        stat.S_IFBLK: 'blk',
        stat.S_IFREG: 'reg',
        stat.S_IFIFO: 'fifo',
        stat.S_IFLNK: 'lnk',
        stat.S_IFSOCK: 'sock',
    }

    @classmethod
    def _scan_fd(cls, dirname):
        for entry in os.scandir(dirname):
            try:
                yield cls._lookup[stat.S_IFMT(entry.stat().st_mode)]
            except (KeyError, FileNotFoundError):
                pass

    @classmethod
    def from_dir(cls, dirname):
        return cls(**Counter(cls._scan_fd(dirname)))

def read_fd(dirname, *, dictcls=dict, **kwargs):
    return dictcls(zip(Fd._fields, Fd.from_dir(dirname)))

read_fd.schema = Fd
read_fd.empty = Fd()._asdict()
registry['fd'] = read_fd


class SmapsRollup(NamedTuple):
    """
    Representation of ``/proc/{pid}/smaps_rollup``.

    This file was added to the Kernel in version 4.14. It provides
    pre-summed memory information for a process, and contains most of
    the fields of ``/proc/{pid}/smaps``.

    All fields are expressed in kB. Kernel threads have the file empty.
    """

    rss: Optional[int]
    """
    Resident Set Size. Sum of the mappings that are currently
    resident in RAM.
    """

    pss: Optional[int]
    """
    Proportional Set Size. The process' proportional share of its
    mappings. If a process has 100 unshared pages(``USS``), and 100
    shared with another process, its ``PSS`` will be 150.
    """

    shared_clean: Optional[int]
    """The number of clean shared pages in process' mappings."""

    shared_dirty: Optional[int]
    """The number of dirty shared pages in process' mappings."""

    private_clean: Optional[int]
    """The number of clean private pages in process' mappings."""

    private_dirty: Optional[int]
    """The number of dirty private pages in process' mappings."""

    referenced: Optional[int]
    """
    It indicates the amount of memory currently marked as referenced
    or accessed.
    """

    anonymous: Optional[int]
    """
    It shows the amount of memory that does not belong to any file.
    """

    lazyfree: Optional[int]
    """
    It shows the amount of memory which is marked by
    ``madvise(MADV_FREE)``. The memory isn't freed immediately with
    ``madvise()``. It's freed in memory pressure if the memory is
    clean.
    """

    anonhugepages: Optional[int]
    """
    It shows the amount of memory backed by transparent huge pages.
    """

    shmempmdmapped: Optional[int]
    """
    It shows the amount of shared (shmem/tmpfs) memory backed by
    huge pages.
    """

    shared_hugetlb: Optional[int]
    """
    It shows the amount of memory backed by hugetlbfs page which is not
    counted in ``rss`` or ``pss`` fields for historical reasons. And
    it is not included in ``shared_clean`` and ``shared_dirty`` fields.
    """

    private_hugetlb: Optional[int]
    """
    It shows the amount of memory backed by hugetlbfs page which is not
    counted in ``rss`` or ``pss`` fields for historical reasons. And
    it is not included in ``private_clean`` and ``private_dirty``
    fields.
    """

    swap: Optional[int]
    """
    It shows how much would-be-anonymous memory is also used, but out
    on swap.
    """

    swappss: Optional[int]
    """
    It shows proportional swap share of process' mappings. Unlike
    ``swap``, this does not take into account swapped out page of
    underlying shmem objects.
    """

    locked: Optional[int]
    """It indicates the mappings that are locked in memory."""

    @classmethod
    def from_bytes(cls, b):
        fields = {k: None for k in cls._fields}
        if b:
            for line in b[b.index(b'\n') + 1:].lower().decode().splitlines():
                k, _, v = line.partition(':')
                if k in fields:
                    v, _, _ = v.rpartition(' ')
                    fields[k] = int(v)

        return cls(**fields)

def read_smaps_rollup(b, *, dictcls=dict, **kwargs):
    return dictcls(zip(SmapsRollup._fields, SmapsRollup.from_bytes(b)))

read_smaps_rollup.schema = SmapsRollup
read_smaps_rollup.empty = SmapsRollup(*[None] * len(SmapsRollup._fields))._asdict()
registry['smaps_rollup'] = read_file(read_smaps_rollup)

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile

import appdirs
import julia


APPNAME = 'InterpretableAI'
NEEDS_RESTART = False


def iswindows():
    return (appdirs.system.startswith('win32') or
            appdirs.system.startswith('cygwin'))


def isapple():
    return appdirs.system.startswith('darwin')


def islinux():
    return appdirs.system.startswith('linux')


def julia_exename():
    return 'julia.exe' if iswindows() else 'julia'


def julia_default_depot():
    if iswindows():
        key = 'USERPROFILE'
    else:
        key = 'HOME'

    return os.path.join(os.environ[key], '.julia')


def get_prefs_dir():
    depot = os.environ.get('JULIA_DEPOT_PATH', julia_default_depot())
    prefs = os.path.join(depot, 'prefs')
    pathlib.Path(prefs).mkdir(parents=True, exist_ok=True)
    return prefs


# Configure julia with options specified in environment variables
def iai_run_julia_setup(**kwargs):
    if NEEDS_RESTART:
        raise Exception(
            'Need to restart Python after installing the IAI system image')

    # Check if system image replacement was queued on Windows
    replace_sysimg_file = sysimage_replace_prefs_file()
    if os.path.isfile(replace_sysimg_file):
        with open(replace_sysimg_file) as f:
            lines = f.read().splitlines()
        sysimage_do_replace(*lines)
        os.remove(replace_sysimg_file)

    if 'IAI_DISABLE_COMPILED_MODULES' in os.environ:  # pragma: no cover
        kwargs['compiled_modules'] = False

    if 'IAI_JULIA' in os.environ:  # pragma: no cover
        kwargs['runtime'] = os.environ['IAI_JULIA']
    else:
        julia_path = julia_load_install_path()
        if julia_path:
            kwargs['runtime'] = os.path.join(julia_path, 'bin',
                                             julia_exename())

    if 'IAI_SYSTEM_IMAGE' in os.environ:  # pragma: no cover
        kwargs['sysimage'] = os.environ['IAI_SYSTEM_IMAGE']
    else:
        sysimage_path = sysimage_load_install_path()
        if sysimage_path:
            kwargs['sysimage'] = sysimage_path

    # Add Julia bindir to path on Windows so that DLLs can be found
    if 'runtime' in kwargs and os.name == 'nt':
        bindir = os.path.dirname(kwargs['runtime'])
        os.environ['PATH'] += os.pathsep + bindir

    # Load Julia with IAI_DISABLE_INIT to avoid interfering with stdout
    os.environ['IAI_DISABLE_INIT'] = 'True'

    # Start julia once in case artifacts need to be downloaded
    # Skip if julia is already inited, as we may not know `runtime`
    if not julia.libjulia.get_libjulia():
        args = [kwargs.get('runtime', julia_exename())]
        if 'sysimage' in kwargs:
            args.extend(['-J', kwargs['sysimage']])
        args.extend(['-e', 'nothing'])
        subprocess.run(args, stdout=subprocess.DEVNULL)

    # Do custom Julia init if required
    if len(kwargs) > 0:
        julia.Julia(**kwargs)

    from julia import Main as _Main

    del os.environ['IAI_DISABLE_INIT']

    return _Main


def install(runtime=os.environ.get("IAI_JULIA", "julia"), **kwargs):
    """Install Julia packages required for `interpretableai.iai`.

    This function must be called once after the package is installed to
    configure the connection between Python and Julia.

    Parameters
    ----------
    Refer to the
    `installation instructions <https://docs.interpretable.ai/v3.0.0/IAI-Python/data/#Python-Installation-1>`
    for information on any additional parameters that may be required.

    Examples
    --------
    >>> install(**kwargs)
    """
    import julia
    os.environ['IAI_DISABLE_INIT'] = 'True'
    julia.install(julia=runtime, **kwargs)
    del os.environ['IAI_DISABLE_INIT']


# JULIA


def julia_default_install_dir():
    return os.path.join(appdirs.user_data_dir(APPNAME), 'julia')


def julia_latest_version():
    url = 'https://julialang-s3.julialang.org/bin/versions.json'
    versions_json = urllib.request.urlopen(url).read().decode('utf-8')
    versions = json.loads(versions_json)
    return max(k for (k, v) in versions.items() if v['stable'])


def julia_tgz_url(version):
    arch = 'x64'
    short_version = version[:3]
    if islinux():
        os = 'linux'
        slug = 'linux-x86_64'
        ext = 'tar.gz'
    elif isapple():
        os = 'mac'
        slug = 'mac64'
        ext = 'dmg'
    elif iswindows():
        os = 'winnt'
        slug = 'win64'
        ext = 'zip'
    else:  # pragma: no cover
        raise Exception(
            'Unsupported operating system: {0}'.format(appdirs.system))

    url = "https://julialang-s3.julialang.org/bin/{0}/{1}/{2}/julia-{3}-{4}.{5}".format(os, arch, short_version, version, slug, ext)

    return url


def julia_path_prefs_file():
    return os.path.join(get_prefs_dir(), 'IAI-pyjulia')


def julia_save_install_path(path):
    with open(julia_path_prefs_file(), 'w') as f:
        f.write(path)


def julia_load_install_path():
    path = julia_path_prefs_file()
    if os.path.isfile(path):
        with open(path) as f:
            julia_path = f.read()
        if isinstance(julia_path, bytes):  # pragma: no cover
            julia_path = julia_path.decode('utf-8')
        return julia_path
    else:
        return None


def install_julia(version='latest', prefix=julia_default_install_dir()):
    """Download and install Julia automatically.

    Parameters
    ----------
    version : string, optional
        The version of Julia to install (e.g. `'1.6.3'`).
        Defaults to `'latest'`, which will install the most recent stable
        release.
    prefix : string, optional
        The directory where Julia will be installed. Defaults to a location
        determined by
        `appdirs.user_data_dir <https://pypi.org/project/appdirs/>`.

    Examples
    --------
    >>> install_julia(**kwargs)
    """
    if version == 'latest':
        version = julia_latest_version()  # pragma: no cover
    url = julia_tgz_url(version)

    print('Downloading {0}'.format(url), file=sys.stderr)
    filename, _ = urllib.request.urlretrieve(url)

    dest = os.path.join(prefix, version)
    if os.path.exists(dest):  # pragma: no cover
        shutil.rmtree(dest)

    if islinux():
        with tarfile.open(filename) as f:
            f.extractall(dest)
        subfolder = 'julia-' + version
    elif iswindows():
        with zipfile.ZipFile(filename) as f:
            f.extractall(dest)
        subfolder = 'julia-' + version
    elif isapple():
        subfolder = install_julia_dmg(filename, dest)

    dest = os.path.join(dest, subfolder)

    julia_save_install_path(dest)

    install(runtime=os.path.join(dest, 'bin', julia_exename()))

    print('Installed Julia to {0}'.format(dest), file=sys.stderr)
    return True


# From https://github.com/johnnychen94/jill.py/blob/3b2a29e263ed712f54b0ad2a103083aa2f8045bb/jill/install.py#L221-L238
def install_julia_dmg(package_path, install_dir):
    with DmgMounter(package_path) as root:
        # mounted image contents:
        #   ['.VolumeIcon.icns', 'Applications', 'Julia-1.3.app']
        appname = next(filter(lambda x: x.lower().startswith('julia'),
                              os.listdir(root)))
        src_path = os.path.join(root, appname)
        dest_path = os.path.join(install_dir, appname)
        # preserve lib symlinks, otherwise it might cause troubles
        # see also: https://github.com/JuliaGPU/CUDA.jl/issues/249
        shutil.copytree(src_path, dest_path, symlinks=True)
    return os.path.join(appname, "Contents", "Resources", "julia")

# From https://github.com/johnnychen94/jill.py/blob/3b2a29e263ed712f54b0ad2a103083aa2f8045bb/jill/utils/mount_utils.py#L34-L69
class DmgMounter():
    def __init__(self, src_path, mount_root=".", verbose=False, max_try=5):
        self.src_path = src_path
        self.mount_root = os.path.abspath(mount_root)
        mount_name = os.path.splitext(os.path.split(self.src_path)[1])[0]
        self.mount_point = os.path.join(self.mount_root, mount_name)
        self.extra_args = ["-mount", "required"]
        self.max_try = max_try
        if not verbose:
            self.extra_args.append("-quiet")

    @staticmethod
    def umount(mount_point):
        if os.path.exists(mount_point):
            rst = subprocess.run(["umount", mount_point])
            return not rst.returncode
        return True

    def __enter__(self):  # pragma: no cover
        assert sys.platform == "darwin"
        args = ["hdiutil", "attach", self.src_path,
                "-mountpoint", self.mount_point]
        args.extend(self.extra_args)
        DmgMounter.umount(self.mount_point)

        # the mount might fail for unknown reason,
        # set a max_try here to work it around
        cur_try = 1
        while cur_try <= self.max_try:
            is_success = subprocess.run(args).returncode == 0
            if is_success:
                return self.mount_point
            time.sleep(0.5)
            cur_try += 1

        raise IOError(f"{self.src_path} is not mounted successfully")

    def __exit__(self, type, value, tb):
        DmgMounter.umount(self.mount_point)


# IAI SYSTEM IMAGE


def sysimage_default_install_dir():
    return os.path.join(appdirs.user_data_dir(APPNAME), 'sysimage')


def get_latest_iai_version():
    url = 'https://docs.interpretable.ai/stable_version.txt'
    return urllib.request.urlopen(url).read().decode('utf-8')


def iai_download_url(julia_version, iai_version):
    if isapple():
        os_code = 'macos'
    elif iswindows():
        os_code = 'win64'
    elif islinux():
        os_code = 'linux'
    else:  # pragma: no cover
        raise Exception(
            'Unsupported operating system: {0}'.format(appdirs.system))

    if iai_version.startswith('v'):
        iai_version = iai_version[1:]

    if iai_version == 'dev':
        url = 'https://iai-system-images.s3.amazonaws.com/{0}/julia{1}/master/latest.zip'.format(os_code, julia_version)
    else:
        url = 'https://iai-system-images.s3.amazonaws.com/{0}/julia{1}/v{2}/sys-{0}-julia{1}-iai{2}.zip'.format(os_code, julia_version, iai_version)

    return url


# Saving location of system image

def sysimage_path_prefs_file():
    return os.path.join(get_prefs_dir(), 'IAI')


def sysimage_save_install_path(path):
    with open(sysimage_path_prefs_file(), 'w') as f:
        f.write(path)


def sysimage_load_install_path():
    path = sysimage_path_prefs_file()
    if os.path.isfile(path):
        with open(path) as f:
            sysimage_path = f.read()
        if isinstance(sysimage_path, bytes):  # pragma: no cover
            sysimage_path = sysimage_path.decode('utf-8')
        return sysimage_path
    else:
        return None


# Saving replacement command

def sysimage_replace_prefs_file():
    return os.path.join(get_prefs_dir(), 'IAI-replacedefault')


def sysimage_save_replace_command(image_path, target_path):
    with open(sysimage_replace_prefs_file(), 'w') as f:
        print(image_path, file=f)
        print(target_path, file=f)


def sysimage_do_replace(image_path, target_path):
    print('Replacing default system image at {0} with IAI system image'.format(target_path), file=sys.stderr)
    os.chmod(target_path, 0o777)
    os.remove(target_path)
    shutil.copyfile(image_path, target_path)


# Top-level system image installation

def install_system_image(version='latest', replace_default=False,
                         prefix=sysimage_default_install_dir()):
    """Download and install the IAI system image automatically.

    Parameters
    ----------
    version : string, optional
        The version of the IAI system image to install (e.g. `'2.1.0'`).
        Defaults to `'latest'`, which will install the most recent release.
    replace_default : bool
        Whether to replace the default Julia system image with the downloaded
        IAI system image. Defaults to `False`.
    prefix : string, optional
        The directory where Julia will be installed. Defaults to a location
        determined by
        `appdirs.user_data_dir <https://pypi.org/project/appdirs/>`.

    Examples
    --------
    >>> install_system_image(**kwargs)
    """
    if version == 'latest':
        version = get_latest_iai_version()

    Main = iai_run_julia_setup()

    julia_version = Main.string(Main.VERSION)

    url = iai_download_url(julia_version, version)

    print('Downloading {0}'.format(url), file=sys.stderr)
    filename, _ = urllib.request.urlretrieve(url)

    if version != 'dev':
        version = 'v{0}'.format(version)
    dest = os.path.join(prefix, version)
    if os.path.exists(dest):  # pragma: no cover
        shutil.rmtree(dest)

    with zipfile.ZipFile(filename) as f:
        f.extractall(dest)

    if islinux():
        image_name = 'sys.so'
    elif isapple():
        image_name = 'sys.dylib'
    elif iswindows():
        image_name = 'sys.dll'
    else:  # pragma: no cover
        raise Exception(
            'Unsupported operating system: {0}'.format(appdirs.system))
    image_path = os.path.join(dest, image_name)

    sysimage_save_install_path(image_path)
    print('Installed IAI system image to {0}'.format(dest), file=sys.stderr)

    if replace_default:
        target_path = os.path.join(
            Main.eval('unsafe_string(Base.JLOptions().julia_bindir)'),
            '..', 'lib', 'julia', image_name,
        )
        # Windows can't replace the current sysimg as it is loaded into this
        # session so we save a command to run later
        if iswindows():
            sysimage_save_replace_command(image_path, target_path)
        else:
            sysimage_do_replace(image_path, target_path)

    # Need to restart R to load with the system image before IAI can be used
    global NEEDS_RESTART
    NEEDS_RESTART = True
    return True


def cleanup_installation():
    """Remove all files created by :meth:`interpretableai.install_julia` and
    :meth:`interpretableai.install_system_image`.

    Examples
    --------
    >>> cleanup_installation()
    """
    for f in (
            julia_path_prefs_file(),
            sysimage_path_prefs_file(),
            sysimage_replace_prefs_file(),
    ):
        if os.path.exists(f):
            os.remove(f)

    for path in (
            julia_default_install_dir(),
            sysimage_default_install_dir(),
    ):
        if os.path.exists(path):
            shutil.rmtree(path)

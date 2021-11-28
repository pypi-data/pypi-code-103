import sys
import os
import tomli
import pkg_resources
import importlib_metadata
from collections import deque
from warnings import warn
from pipes import quote
from configparser import ConfigParser, SectionProxy
from enum import Enum, auto
from itertools import chain
from typing import (
    Optional,
    Dict,
    Iterable,
    Set,
    Tuple,
    List,
    IO,
    Union,
    Callable,
    Any,
)
from packaging.utils import canonicalize_name
from packaging.requirements import InvalidRequirement, Requirement
from more_itertools import unique_everseen
from ..utilities import lru_cache, run
from ..errors import append_exception_text

_BUILTIN_DISTRIBUTION_NAMES: Tuple[str] = ("distribute",)
# This variable tracks the absolute file paths from which a package has been
# re-installed, in order to avoid performing a reinstall redundantly
_reinstalled_locations: Set[str] = set()


@lru_cache()
def normalize_name(name: str) -> str:
    """
    Normalize a project/distribution name
    """
    return pkg_resources.safe_name(canonicalize_name(name)).lower()


class ConfigurationFileType(Enum):

    REQUIREMENTS_TXT = auto()
    SETUP_CFG = auto()
    TOX_INI = auto()
    PYPROJECT_TOML = auto()


@lru_cache()
def get_configuration_file_type(path: str) -> ConfigurationFileType:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    basename: str = os.path.basename(path).lower()
    if basename == "setup.cfg":
        return ConfigurationFileType.SETUP_CFG
    elif basename == "tox.ini":
        return ConfigurationFileType.TOX_INI
    elif basename == "pyproject.toml":
        return ConfigurationFileType.PYPROJECT_TOML
    elif basename.endswith(".txt"):
        return ConfigurationFileType.REQUIREMENTS_TXT
    else:
        raise ValueError(
            f"{path} is not a recognized type of configuration file."
        )


def is_configuration_file(path: str) -> bool:
    try:
        get_configuration_file_type(path)
    except (FileNotFoundError, ValueError):
        return False
    return True


def refresh_working_set() -> None:
    """
    Force a refresh of all distribution information and clear related caches
    """
    get_installed_distributions.cache_clear()
    is_editable.cache_clear()
    is_installed.cache_clear()
    get_requirement_string_distribution_name.cache_clear()
    pkg_resources.working_set.entries = []
    pkg_resources.working_set.__init__()  # type: ignore


@lru_cache()
def get_installed_distributions() -> Dict[str, pkg_resources.Distribution]:
    """
    Return a dictionary of installed distributions.
    """
    installed: Dict[str, pkg_resources.Distribution] = {}
    for distribution in pkg_resources.working_set:
        installed[normalize_name(distribution.project_name)] = distribution
    return installed


def get_distribution(name: str) -> pkg_resources.Distribution:
    return get_installed_distributions()[normalize_name(name)]


@lru_cache()
def is_installed(distribution_name: str) -> bool:
    return normalize_name(distribution_name) in get_installed_distributions()


def get_requirement_distribution_name(requirement: Requirement) -> str:
    return normalize_name(requirement.name)


@lru_cache()
def get_requirement_string_distribution_name(requirement_string: str) -> str:
    return get_requirement_distribution_name(
        get_requirement(requirement_string)
    )


@lru_cache()
def is_requirement_string(requirement_string: str) -> bool:
    try:
        Requirement(requirement_string)
    except InvalidRequirement:
        return False
    return True


def _iter_file_requirement_strings(path: str) -> Iterable[str]:
    lines: List[str]
    requirement_file_io: IO[str]
    with open(path) as requirement_file_io:
        lines = requirement_file_io.readlines()
    return filter(is_requirement_string, lines)


def _iter_setup_cfg_requirement_strings(path: str) -> Iterable[str]:
    parser: ConfigParser = ConfigParser()
    parser.read(path)
    requirement_strings: Iterable[str] = ()
    if ("options" in parser) and ("install_requires" in parser["options"]):
        requirement_strings = chain(
            requirement_strings,
            filter(
                is_requirement_string,
                parser["options"]["install_requires"].split("\n"),
            ),
        )
    if "options.extras_require" in parser:
        extras_require: SectionProxy = parser["options.extras_require"]
        extra_requirements_string: str
        for extra_requirements_string in extras_require.values():
            requirement_strings = chain(
                requirement_strings,
                filter(
                    is_requirement_string,
                    extra_requirements_string.split("\n"),
                ),
            )
    return unique_everseen(requirement_strings)


def _iter_tox_ini_requirement_strings(path: str) -> Iterable[str]:
    parser: ConfigParser = ConfigParser()
    parser.read(path)

    def get_section_option_requirements(
        section_name: str, option_name: str
    ) -> Iterable[str]:
        if parser.has_option(section_name, option_name):
            return filter(
                is_requirement_string,
                parser.get(section_name, option_name).split("\n"),
            )
        return ()

    def get_section_requirements(section_name: str) -> Iterable[str]:
        requirements: Iterable[str] = get_section_option_requirements(
            section_name, "deps"
        )
        if section_name == "tox":
            requirements = chain(
                requirements,
                get_section_option_requirements(section_name, "requires"),
            )
        return requirements

    return unique_everseen(
        chain(("tox",), *map(get_section_requirements, parser.sections()))
    )


def _iter_pyproject_toml_requirement_strings(path: str) -> Iterable[str]:
    pyproject_io: IO[str]
    with open(path) as pyproject_io:
        pyproject: Dict[str, Any] = tomli.loads(pyproject_io.read())
        if ("build-system" in pyproject) and (
            "requires" in pyproject["build-system"]
        ):
            return pyproject["build-system"]["requires"]
    return ()


def iter_configuration_file_requirement_strings(path: str) -> Iterable[str]:
    """
    Read a configuration file and yield the parsed requirements.
    """
    configuration_file_type: ConfigurationFileType = (
        get_configuration_file_type(path)
    )
    if configuration_file_type == ConfigurationFileType.SETUP_CFG:
        return _iter_setup_cfg_requirement_strings(path)
    elif configuration_file_type == ConfigurationFileType.PYPROJECT_TOML:
        return _iter_pyproject_toml_requirement_strings(path)
    elif configuration_file_type == ConfigurationFileType.TOX_INI:
        return _iter_tox_ini_requirement_strings(path)
    else:
        assert (
            configuration_file_type == ConfigurationFileType.REQUIREMENTS_TXT
        )
        return _iter_file_requirement_strings(path)


@lru_cache()
def is_editable(distribution_name: str) -> bool:
    """
    Return `True` if the indicated distribution is an editable installation.
    """
    return _distribution_is_editable(get_distribution(distribution_name))


def _distribution_is_editable(
    distribution: pkg_resources.Distribution,
) -> bool:
    """
    Return `True` if the `distribution` is an editable installation.
    """
    egg_link_file_name: str = f"{distribution.project_name}.egg-link"

    def project_egg_link_exists(path: str) -> bool:
        return os.path.isfile(os.path.join(path, egg_link_file_name))

    return any(map(project_egg_link_exists, sys.path))


def _get_setup_py_distribution_name(path: str) -> str:
    current_directory: str = os.path.abspath(os.curdir)
    try:
        if os.path.basename(path).lower() == "setup.py":
            os.chdir(os.path.dirname(path))
        else:
            if not os.path.isdir(path):
                path = os.path.dirname(path)
            os.chdir(path)
            path = os.path.join(path, "setup.py")
        try:
            name: str = (
                run(
                    f"{quote(sys.executable)} {quote(path)} --name", echo=False
                )
                .strip()
                .split("\n")[-1]
            )
        except OSError:
            name = ""
    finally:
        os.chdir(current_directory)
    return name


def _get_setup_cfg_distribution_name(path: str) -> str:
    if os.path.basename(path).lower() != "setup.cfg":
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        path = os.path.join(path, "setup.cfg")
    if os.path.isfile(path):
        parser: ConfigParser = ConfigParser()
        parser.read(path)
        if "metadata" in parser:
            return parser.get("metadata", "name", fallback="")
    return ""


def get_setup_distribution_name(path: str) -> str:
    """
    Get a distribution's name from setup.py or setup.cfg
    """
    return normalize_name(
        _get_setup_py_distribution_name(path)
        or _get_setup_cfg_distribution_name(path)
    )


def _setup(arguments: str) -> None:
    run(
        f"{quote(sys.executable)} setup.py {arguments}",
        echo=False,
    )


def _setup_location(location: str, arguments: Iterable[str]) -> None:
    # If there is no setup.py file, we can't update egg info
    if not os.path.isfile(os.path.join(location, "setup.py")):
        return
    if isinstance(arguments, str):
        arguments = (arguments,)
    current_directory: str = os.path.abspath(os.curdir)
    os.chdir(location)
    try:
        deque(map(_setup, arguments), maxlen=0)
    finally:
        os.chdir(current_directory)


def setup_dist_egg_info(directory: str) -> None:
    """
    Refresh dist-info and egg-info for the editable package installed in
    `directory`
    """
    directory = os.path.abspath(directory)
    if not os.path.isdir(directory):
        directory = os.path.dirname(directory)
    return _setup_location(directory, ("-q dist_info", "-q egg_info"))


def setup_dist_info(directory: str) -> None:
    """
    Refresh dist-info and egg-info for the editable package installed in
    `directory`
    """
    directory = os.path.abspath(directory)
    if not os.path.isdir(directory):
        directory = os.path.dirname(directory)
    return _setup_location(directory, "-q dist_info")


def setup_egg_info(directory: str) -> None:
    """
    Refresh dist-info and egg-info for the editable package installed in
    `directory`
    """
    directory = os.path.abspath(directory)
    if not os.path.isdir(directory):
        directory = os.path.dirname(directory)
    return _setup_location(directory, "-q egg_info")


def get_setup_distribution_requirements(
    path: str,
) -> Dict[str, Tuple[str, ...]]:
    """
    Get a distribution's name from setup.py or setup.cfg
    """
    return normalize_name(
        _get_setup_py_distribution_name(path)
        or _get_setup_cfg_distribution_name(path)
    )


def _get_location_distribution_name(location: str) -> str:
    """
    Get a distribution name based on an installation location, or return
    an empty string if no distribution can be found
    """
    setup_dist_egg_info(location)
    location = os.path.abspath(location)

    def _is_in_location(
        name_distribution: Tuple[str, pkg_resources.Distribution]
    ) -> bool:
        return os.path.abspath(name_distribution[1].location) == location

    def _get_name(
        name_distribution: Tuple[str, pkg_resources.Distribution]
    ) -> str:
        return name_distribution[0]

    try:
        return next(
            map(
                _get_name,
                filter(_is_in_location, get_installed_distributions().items()),
            )
        )
    except StopIteration:
        return get_setup_distribution_name(location)


def _get_pkg_requirement(
    requirement_string: str,
) -> pkg_resources.Requirement:
    requirement: Union[
        Requirement, pkg_resources.Requirement
    ] = _get_requirement(requirement_string, pkg_resources.Requirement.parse)
    assert isinstance(requirement, pkg_resources.Requirement)
    return requirement


def get_requirement(
    requirement_string: str,
) -> Requirement:
    requirement: Union[
        Requirement, pkg_resources.Requirement
    ] = _get_requirement(requirement_string, Requirement)
    assert isinstance(requirement, Requirement)
    return requirement


def _get_requirement(
    requirement_string: str,
    constructor: Callable[
        [str], Union[Requirement, pkg_resources.Requirement]
    ],
) -> Union[Requirement, pkg_resources.Requirement]:
    try:
        return constructor(requirement_string)
    except (
        InvalidRequirement,
        getattr(
            pkg_resources, "extern"
        ).packaging.requirements.InvalidRequirement,
        getattr(pkg_resources, "RequirementParseError"),
    ):
        # Try to parse the requirement as an installation target location,
        # such as can be used with `pip install`
        location: str = requirement_string
        extras: str = ""
        if "[" in requirement_string and requirement_string.endswith("]"):
            parts: List[str] = requirement_string.split("[")
            location = "[".join(parts[:-1])
            extras = f"[{parts[-1]}"
        location = os.path.abspath(location)
        name: str = _get_location_distribution_name(location)
        assert name, f"No distribution found in {location}"
        return constructor(f"{name}{extras}")


def get_required_distribution_names(
    requirement_string: str,
    exclude: Iterable[str] = (),
    recursive: bool = True,
) -> Set[str]:
    """
    Return a `set` of all distribution names which are required by the
    distribution specified in `requirement_string`.

    Parameters:

    - requirement_string (str): A distribution name, or a requirement string
      indicating both a distribution name and extras.
    - exclude ([str]): The name of one or more distributions to *exclude*
      from requirements lookup. Please note that excluding a distribution will
      also halt recursive lookup of requirements for that distribution.
    - recursive (bool): If `True` (the default), required distributions will
      be obtained recursively.
    """
    if isinstance(exclude, str):
        exclude = {normalize_name(exclude)}
    else:
        exclude = set(map(normalize_name, exclude))
    return set(
        _iter_requirement_names(
            _get_pkg_requirement(requirement_string),
            exclude=exclude,
            recursive=recursive,
        )
    )


def _get_pkg_requirement_name(requirement: pkg_resources.Requirement) -> str:
    return normalize_name(requirement.project_name)


def install_requirement(
    requirement: Union[str, Requirement, pkg_resources.Requirement],
    echo: bool = True,
) -> None:
    """
    Install a requirement

    Parameters:

    - requirement (str)
    - echo (bool) = True: If `True` (default), the `pip install`
      commands will be echoed to `sys.stdout`
    """
    if isinstance(requirement, str):
        requirement = Requirement(requirement)
    return _install_requirement(requirement, echo)


def _install_requirement(
    requirement: Union[Requirement, pkg_resources.Requirement],
    echo: bool = True,
) -> None:
    requirement_string: str = str(requirement)
    # Get the distribution name
    name: str = normalize_name(
        requirement.name
        if isinstance(requirement, Requirement)
        else requirement.project_name
    )
    distribution: Optional[pkg_resources.Distribution] = None
    editable: bool = False
    try:
        distribution = get_distribution(name)
        editable = _distribution_is_editable(distribution)
    except KeyError:
        pass
    # If the requirement is installed and editable, re-install from
    # the editable location
    if distribution and editable:
        # Refresh metadata
        setup_dist_egg_info(distribution.location)
        # Assemble a requirement specifier for the editable install
        requirement_string = distribution.location
        if requirement.extras:
            requirement_string = (
                f"{requirement_string}[{','.join(requirement.extras)}]"
            )
    # First attempt a user install, then a system install
    try:
        run(
            (
                f"{quote(sys.executable)} -m pip install --user "
                f"{quote(requirement_string)}"
            ),
            echo=echo,
        )
    except OSError:
        try:
            # If a user installation failed, attempt a system installation
            run(
                (
                    f"{quote(sys.executable)} -m pip install "
                    f"{quote(requirement_string)}"
                ),
                echo=echo,
            )
        except OSError as error:
            append_exception_text(
                error, f"Could not install {name} from {requirement_string}"
            )
            raise error
    # Refresh the metadata
    if distribution and editable:
        setup_dist_egg_info(distribution.location)
    else:
        refresh_working_set()


def _get_pkg_requirement_distribution(
    requirement: pkg_resources.Requirement, name: str, reinstall: bool = True
) -> Optional[pkg_resources.Distribution]:
    if name in _BUILTIN_DISTRIBUTION_NAMES:
        return None
    try:
        return get_installed_distributions()[name]
    except KeyError:
        if not reinstall:
            raise
        warn(
            f'The required distribution "{name}" was not installed, '
            "attempting to install it now..."
        )
        # Attempt to install the requirement...
        install_requirement(requirement)
        refresh_working_set()
        return _get_pkg_requirement_distribution(
            requirement, name, reinstall=False
        )


def _iter_requirement_names(
    requirement: pkg_resources.Requirement,
    exclude: Set[str],
    recursive: bool = True,
) -> Iterable[str]:
    name: str = normalize_name(requirement.project_name)
    extras: Set[str] = set(map(normalize_name, requirement.extras))
    if name in exclude:
        return ()
    # Ensure we don't follow the same requirement again, causing cyclic
    # recursion
    exclude.add(name)
    distribution: Optional[
        pkg_resources.Distribution
    ] = _get_pkg_requirement_distribution(requirement, name)
    if distribution is None:
        return ()
    # Ensure requirements are up-to-date
    if _distribution_is_editable(distribution):
        setup_dist_egg_info(distribution.location)
    requirements: List[pkg_resources.Requirement] = distribution.requires(
        extras=tuple(sorted(extras))
    )
    lateral_exclude: Set[str] = set()

    def iter_requirement_names_(
        requirement_: pkg_resources.Requirement,
    ) -> Iterable[str]:
        return _iter_requirement_names(
            requirement_,
            exclude=(
                exclude
                | (lateral_exclude - {_get_pkg_requirement_name(requirement_)})
            ),
            recursive=recursive,
        )

    def not_excluded(name: str) -> bool:
        if name not in exclude:
            # Add this to the exclusions
            lateral_exclude.add(name)
            return True
        return False

    if recursive:
        requirement_names = chain(
            filter(not_excluded, map(_get_pkg_requirement_name, requirements)),
            *map(iter_requirement_names_, requirements),
        )
    return requirement_names


def _iter_requirement_strings_required_distribution_names(
    requirement_strings: Iterable[str],
) -> Iterable[str]:
    visited_requirement_strings: Set[str] = set()
    if isinstance(requirement_strings, str):
        requirement_strings = (requirement_strings,)

    def get_required_distribution_names_(requirement_string: str) -> Set[str]:
        if requirement_string not in visited_requirement_strings:
            try:
                name: str = get_requirement_string_distribution_name(
                    requirement_string
                )
                visited_requirement_strings.add(requirement_string)
                return get_required_distribution_names(requirement_string) | {
                    name
                }
            except KeyError:
                pass
        return set()

    return unique_everseen(
        chain(*map(get_required_distribution_names_, requirement_strings)),
    )


def get_requirements_required_distribution_names(
    requirements: Iterable[str] = (),
) -> Set[str]:
    """
    Get the distributions required by one or more specified distributions or
    configuration files.

    Parameters:

    - requirements ([str]): One or more requirement specifiers (for example:
      "requirement-name[extra-a,extra-b]" or ".[extra-a, extra-b]) and/or paths
      to a setup.cfg, pyproject.toml, tox.ini or requirements.txt file
    """
    # Separate requirement strings from requirement files
    if isinstance(requirements, str):
        requirements = {requirements}
    else:
        requirements = set(requirements)
    requirement_files: Set[str] = set(
        filter(is_configuration_file, requirements)
    )
    requirement_strings: Set[str] = requirements - requirement_files
    name: str
    return set(
        sorted(
            _iter_requirement_strings_required_distribution_names(
                unique_everseen(
                    chain(
                        requirement_strings,
                        *map(
                            iter_configuration_file_requirement_strings,
                            requirement_files,
                        ),
                    )
                ),
            ),
            key=lambda name: name.lower(),
        )
    )


def iter_distribution_location_file_paths(location: str) -> Iterable[str]:
    location = os.path.abspath(location)
    name: str = get_setup_distribution_name(location)
    setup_dist_egg_info(location)
    metadata_path: str = os.path.join(
        location, f"{pkg_resources.to_filename(name)}.egg-info"
    )
    distribution: importlib_metadata.Distribution = (
        importlib_metadata.Distribution.at(metadata_path)
    )
    if not distribution.files:
        raise RuntimeError(f"No metadata found at {metadata_path}")
    return map(os.path.abspath, distribution.files)

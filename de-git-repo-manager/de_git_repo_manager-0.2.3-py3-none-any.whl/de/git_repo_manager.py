"""
create and maintain local and remote git repositories of Python projects
========================================================================

after installing this tool via `pip install de_git_repo_manager` the `grm` command will be available in your OS console.

check the available command line arguments and options by specifying the `--help` command line option::

    grm --help

additional information provided by `grm` on the available/registered actions of a local project are printed to the
console by specifying the `show-actions` action::

    grm show-actions

to get a more verbose output add the `--verbose` and/or :ref:`--debug_level <pre-defined-config-options>` command line
options::

    grm show-actions --verbose --debug_level=2

an identical execution using the short command line options looks like::

    grm -v -D 2 show-actions


file patching helper functions
------------------------------

this portion of the 'de' namespace is also providing some helper functions to patch code and documentation files.

the function :func:`bump_file_version` increments any part of a version number of a module, portion, app or package.

templates are patched with the functions :func:`patch_string` and :func:`refresh_templates`.

in conjunction with the template projects of the `de` namespace (like e.g. :mod:`de.tpl_project`) any common portions
file (even the ``setup.py`` file) can be created/maintained as a template in a single place, and then requested and
updated individually for each portion project.

.. hint::
    via the namespace root project, e.g. `the ae namespace <https://gitlab.com/ae-group/ae>`_ and the
    `this de namespace <https://gitlab.com/degroup/de>`_, their namespace portions are maintainable by `grm`.

"""
import ast
import glob
import os
import pprint
import re
import tempfile
from collections import OrderedDict

from contextlib import contextmanager
from difflib import context_diff, diff_bytes, ndiff, unified_diff
from functools import partial, wraps
from traceback import format_exc
from typing import (
    Any, AnyStr, Callable, Dict, Generator, Iterable, Iterator, List, Optional, Set, Tuple, Union, cast)

from github import Github
from gitlab import Gitlab
from gitlab.v4.objects import Project

from PIL import Image                                                                           # type: ignore

import ae.base                                                                                  # type: ignore # patch
from ae.base import (                                                                           # type: ignore
    PY_EXT, PY_INIT, UNSET,
    camel_to_snake, duplicates, in_wd, norm_name, norm_path, project_main_file, read_file, write_file)
from ae.paths import FilesRegister, path_files                                                  # type: ignore
from ae.console import ConsoleApp, sh_exec                                                      # type: ignore
from ae.inspector import module_attr, stack_var, try_eval                                       # type: ignore
from ae.literal import Literal                                                                  # type: ignore
from de.setup_project import (                                                                  # type: ignore
    APP_PRJ, MODULE_PRJ, NO_PRJ, PACKAGE_PRJ, PARENT_FOLDERS, PARENT_PRJ, REPO_CODE_DOMAIN, REPO_HOST_PROTOCOL,
    ROOT_PRJ, VERSION_PREFIX, VERSION_QUOTE,
    code_file_version, pev_str, pev_val, project_env_vars)


__version__ = '0.2.3'


# --------------- global constants ------------------------------------------------------------------------------------

ACTION_SHORTCUTS = {'actions': 'show_actions', 'check': 'check_integrity', 'clone': 'clone_project',
                    'commit': 'commit_project', 'prepare': 'prepare_commit', 'status': 'show_status'}

ANY_PRJ_TYPE = (APP_PRJ, MODULE_PRJ, PACKAGE_PRJ, ROOT_PRJ)
""" tuple of available project types (including the pseudo-project-types: no-/incomplete-project and parent-folder) """

ARG_MULTIPLES = ' ...'                                      #: mark multiple args in the :func:`_action` arg_names kwarg
ARG_ALL = 'ALL'                                             #: ALL argument, used for lists e.g. of namespace portions

COMMIT_MSG_FILE_NAME = '.commit_msg.txt'                    #: commit msg (=>de.tpl_project/templates/de_otf_.gitignore)

GIT_FOLDER_NAME = '.git'                                    #: git sub-folder in project path root of local repository

MAIN_BRANCH = 'develop'                                     #: main/develop/default branch name

OUTSOURCED_MARKER = 'THIS FILE IS EXCLUSIVELY MAINTAINED'   #: to mark an outsourced project file, maintained externally
OUTSOURCED_FILE_NAME_PREFIX = 'de_otf_'                     #: file name prefix of outsourced/externally maintained file

PACKAGE_VERSION_SEP = '=='                                  #: separates package name and version in pip req files

# these TEMPLATE_* constants get added by :func:`project_dev_vars` to be used/recognized by :func:`refresh_templates`
TEMPLATE_PLACEHOLDER_ID_PREFIX = "# "                       #: template id prefix marker
TEMPLATE_PLACEHOLDER_ID_SUFFIX = "#("                       #: template id suffix marker
TEMPLATE_PLACEHOLDER_ARGS_SUFFIX = ")#"                     #: template args suffix marker
TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID = "IncludeFile"        #: placeholder (func:`replace_with_file_content_or_default`)

TPL_FILE_NAME_PREFIX = 'de_tpl_'                            #: template file name prefix
TPL_IMPORT_NAME_PREFIX = 'de.tpl_'                          #: file name prefix of template projects
TPL_STOP_CNV_PREFIX = '_z_'                                 #: file name prefix to support template of template
TPL_VERSION_OPTION_SUFFIX = '_version'                      #: template version pull/clone command line option suffix

TPL_PACKAGES = [TPL_IMPORT_NAME_PREFIX + norm_name(_) for _ in ANY_PRJ_TYPE] + \
               [TPL_IMPORT_NAME_PREFIX + 'project']
""" import names of all template projects """

VERSION_MATCHER = re.compile("^" + VERSION_PREFIX + r"(\d+)[.](\d+)[.](\d+)[a-z0-9]*" + VERSION_QUOTE, re.MULTILINE)
""" pre-compiled regular expression to detect and bump the app/portion file version numbers of a version string.

The version number format has to be :pep:`conform to PEP396 <396>` and the sub-part to :ref:`Pythons distutils
<https://docs.python.org/3/distutils/setupscript.html#additional-meta-data>` (trailing version information indicating
sub-releases, are either “a1,a2,…,aN” (for alpha releases), “b1,b2,…,bN” (for beta releases) or “pr1,pr2,…,prN” (for
pre-releases).
"""


ActionSpecification = Dict[str, Union[str, Tuple[Tuple[str, ...], ...], bool]]
Replacer = Callable[[str], str]

RegisteredTemplateProject = Dict[str, str]                  #: registered template project info (tpl_projects item)
# PdvVarType = List[RegisteredTemplateProject]
PdvType = Dict[str, Any]    # silly mypy does not recognize PevType in using Union[PevType, Dict[str, PdvVarType]]


# --------------- global variables - most of them are constant after app initialization/startup -----------------------


ACTION_NAME = ''                                            #: command line action[_object] to be executed
ACTION_ARGS: List[str] = []                                 #: optional action arguments passed via command line
REGISTERED_ACTIONS = {}                                     #: implemented actions registered via :func:`_action` deco

INI_PDV: PdvType = {}    #: project environment development values of the initial specified|cwd project
PRJ_PDV: PdvType = {}    #: project environment dev values of another project manipulated by the specified action

LOCK_EXT = '.locked'                                        #: additional file extension to block updates from templates

PORTIONS_ARGS: List[str] = []                               #: package names of portions specified as command line args

PPF = pprint.PrettyPrinter(indent=6, width=189, depth=12).pformat   #: formatter for console printouts

_RCS: Dict[str, Callable] = {}
""" registered recordable callees, for check* actions, using other actions with temporary redirected callees. """

REGISTERED_TPL_PROJECTS: Dict[str, RegisteredTemplateProject] = {}  #: registered template projects

REMOTE_CLASS_NAMES: Dict[str, str] = {}                     #: class names of all supported remote hosts
REMOTE_REPO: Optional[Any] = None                           #: remote class instance (None for local_action)

TEMP_CONTEXT: Optional[tempfile.TemporaryDirectory] = None  #: temp patch folder context (optional/lazy/late created)
TEMP_PARENT_FOLDER: str                                     #: temporary parent folder for to clone git repos into

cae = ConsoleApp()                                          #: main app instance of this tool


# --------------- dev helper functions, decorators and context managers -----------------------------------------------


def _action(*project_types: str, **deco_kwargs) -> Callable:     # Callable[[Callable], Callable]:
    """ parametrized decorator to declare functions and :class:`_RemoteHost` methods as `grm` actions. """
    if not project_types:
        project_types = ANY_PRJ_TYPE

    def _deco(fun):
        # global REGISTERED_ACTIONS
        method_of = stack_var('__qualname__')
        if 'local_action' not in deco_kwargs:
            deco_kwargs['local_action'] = not method_of
        REGISTERED_ACTIONS[(method_of + "." if method_of else "") + fun.__name__] = {
            'project_types': project_types, 'docstring': fun.__doc__, **deco_kwargs}

        @wraps(fun)
        def _wrapped(*fun_args, **fun_kwargs):  # fun_args==(self, ) for remote action methods and ==() for functions
            _check_arguments()
            return fun(*fun_args, **fun_kwargs)
        return _wrapped

    return _deco


def _debug_or_verbose() -> bool:
    """ determine if verbose or debug option got specified (preventing on app init early call of cae.get_option()). """
    # noinspection PyProtectedMember
    return cae.debug or not cae._parsed_arguments or cae.get_option('verbose')


def _recordable_function(callee: Callable) -> Callable:
    """ decorator to register function as recordable (to be replaced/redirected in protocol mode). """
    _RCS[callee.__name__] = callee
    return callee


def _rc_id(instance: Any, method_name: str) -> str:
    """ compile recordable callee id of object method or module instance attribute/function. """
    return getattr(instance, '__class__', instance).__name__ + '.' + method_name


_RCS[_rc_id(ae.base, 'write_file')] = ae.base.write_file
_RCS[_rc_id(os, 'makedirs')] = os.makedirs


@contextmanager
def _record_calls(*recordable_methods: Any, **recordable_functions: Callable) -> Generator[None, None, None]:
    assert len(recordable_methods) % 3 == 0, "expecting 'object-or-module, method_name, callee, ...' argument triple(s)"

    ori_callees = {}

    try:
        for obj_idx in range(0, len(recordable_methods), 3):
            instance, method_name, callee = recordable_methods[obj_idx: obj_idx + 3]
            obj_method = _rc_id(instance, method_name)
            ori_callees[obj_method] = _RCS[obj_method]
            _RCS[obj_method] = callee

        for callee_name, callee in recordable_functions.items():
            ori_callees[callee_name] = _RCS[callee_name]
            _RCS[callee_name] = callee

        yield

    finally:
        for callee_name, ori_call in ori_callees.items():
            _RCS[callee_name] = ori_call


# --------------- global helpers --------------------------------------------------------------------------------------


def bump_file_version(file_name: str, version_part: int = 3) -> str:
    """ increment part of version number of module/script file, also removing any pre/alpha version sub-part/suffix.

    :param file_name:           module/script file name to be patched/version-bumped.
    :param version_part:        version number part to increment: 1=mayor, 2=minor, 3=build/revision (default=3).
    :return:                    empty string on success, else error string.
    """
    msg = f"bump_file_version({file_name}) expects "
    if not os.path.exists(file_name):
        return msg + f"existing code file in folder {os.getcwd()}"
    content = read_file(file_name)
    if not content:
        return msg + f"non-empty code file in {os.getcwd()}"

    content, replaced = VERSION_MATCHER.subn(
        lambda m: VERSION_PREFIX + ".".join(str(int(m.group(p)) + 1) if p == version_part else m.group(p)
                                            for p in range(1, 4)) + VERSION_QUOTE,
        content)

    if replaced != 1:
        return msg + f"single occurrence of module variable __version__, but found {replaced} times"
    _RCS[_rc_id(ae.base, 'write_file')](file_name, content)
    return ""


def deploy_template(tpl_file_path: str, dst_rel_path: str, patcher: str, f_vars: PdvType,
                    replacer: Optional[Dict[str, Replacer]] = None, dst_files: Optional[set] = None):
    """ create/update outsourced project file content from a template.

    :param tpl_file_path:       template file path.
    :param dst_rel_path:        relative path under the root folder of a project, without the project file name.ext.
    :param patcher:             patching template project or function (to be added into the outsourced project file).
    :param f_vars:              project env/dev variables dict of the destination project to patch/refresh,
                                providing values for (1) f-string template replacements, and (2) to specify the path of
                                the project folder in the `project_type` item.
    :param replacer:            optional replacer dict with key=placeholder-id and value=callable.
    :param dst_files:           optional set of project file paths to be excluded from to be created/updated. if the
                                project file got created/updated by this function then the destination file path will
                                be added to this set.

    .. note::
         the project file will kept unchanged if either:

         * the absolute file path is in :paramref:`deploy_template.dst_files`,
         * there exists a lock-file with the additional :data:`LOCK_EXT` file extension, or
         * the outsourced project text does not contain the :data:`OUTSOURCED_MARKER` string.

    """
    dst_file = os.path.basename(tpl_file_path)
    outsourced = dst_file.startswith(OUTSOURCED_FILE_NAME_PREFIX)
    formatting = dst_file.startswith(TPL_FILE_NAME_PREFIX)
    bin_copy = "" if outsourced or formatting else "b"
    if replacer is None:
        replacer = {}
    if dst_files is None:
        dst_files = set()

    new_content = read_file(tpl_file_path, extra_mode=bin_copy)

    if outsourced:
        new_content = _patch_outsourced(dst_file, new_content, patcher)
        dst_file = dst_file[len(OUTSOURCED_FILE_NAME_PREFIX):]
        formatting = dst_file.startswith(TPL_FILE_NAME_PREFIX)
    if formatting:
        new_content = patch_string(new_content, f_vars, **replacer)
        dst_file = dst_file[len(TPL_FILE_NAME_PREFIX):]
    if dst_file.startswith(TPL_STOP_CNV_PREFIX):    # needed only for de_otf__z_de_tpl_*.* or _z_*.* template files
        dst_file = dst_file[len(TPL_STOP_CNV_PREFIX):]

    dst_rel_path = os.path.join(f_vars.get('project_path', ""), dst_rel_path)
    dst_file = norm_path(os.path.join(dst_rel_path, patch_string(dst_file, f_vars)))
    if dst_file not in dst_files:
        dst_files.add(dst_file)
        exists = os.path.exists
        if not exists(dst_file + LOCK_EXT):
            old_content = read_file(dst_file, extra_mode=bin_copy) if exists(dst_file) else ""
            if not os.path.isdir(dst_rel_path):
                _RCS[_rc_id(os, 'makedirs')](dst_rel_path)
            if not old_content or not bin_copy and new_content != old_content and OUTSOURCED_MARKER in old_content:
                _RCS[_rc_id(ae.base, 'write_file')](dst_file, new_content, extra_mode=bin_copy)


def find_modules(project_path: str, namespace_name: str = '', package_name: str = '') -> List[str]:
    """ determine the modules of a project.

    :param project_path:        file path of the project root directory/folder.
    :param namespace_name:      namespace name or empty string for normal packages.
    :param package_name:        name of the package.
    :return:                    the portion type, the portion name/placeholder and a tuple of package module names.
    """
    # assert package_name == os.path.basename(project_path), except when set via setup.cfg/metadata/name
    if namespace_name:
        package_name = package_name[len(namespace_name) + 1:]
        module_dir = os.path.join(project_path, namespace_name)
    else:
        module_dir = project_path
    package_dir = os.path.join(module_dir, package_name)
    if os.path.isfile(os.path.join(package_dir, PY_INIT)):
        module_dir = package_dir

    return [os.path.basename(module_file) for module_file in glob.glob(os.path.join(module_dir, '*' + PY_EXT))]


def package_project_path(import_name: str, sister_fallback: bool = False) -> str:
    """ determine the path of the package's project root folder.

    :param import_name:         import name of the package.
    :param sister_fallback:     pass True to search package in sister project folders of the cwd, if not installed.
    :return:                    absolute package project path or empty string if package not installed/found as sister.
    """
    if not import_name:
        return ""

    package_name = norm_name(import_name)
    path = module_attr(import_name, attr_name='__file__') or ""
    while path and path != os.path.sep:
        path = os.path.dirname(path)
        if os.path.basename(path) == package_name:
            return path

    # fallback to sister search, for namespace root packages because their module instances have no __file__ attribute
    if sister_fallback:
        parent_path = os.path.dirname(os.getcwd())
        sister_path = os.path.join(parent_path, package_name)
        if os.path.basename(parent_path) in PARENT_FOLDERS and os.path.isdir(sister_path):
            return sister_path

    return ""


def patch_string(content: str, f_vars: PdvType, **replacer: Replacer) -> str:
    """ replace f-string / dynamic placeholders in content with variable values / return values of replacer callables.

    :param content:             f-string to patch (e.g. a template file's content).
    :param f_vars:              dict with additional variables used as globals for f-string replacements.
    :param replacer:            optional kwargs dict with key/name=placeholder-id and value=replacer-callable. if not
                                passed then the replacer with id TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID will be searched
                                and if found the callable :func:`replace_with_file_content_or_default` will be executed.
    :return:                    string extended with include snippets found in the same directory.
    :raises Exception:          if evaluation of :paramref;`~patch_string.content` f-string failed (because of
                                missing-globals-NameError/SyntaxError/ValueError/...).
    """
    glo_vars = globals().copy()     # provide globals of this module, eg. COMMIT_MSG_FILE_NAME for .gitignore template
    glo_vars.update(f_vars)
    glo_vars['_add_base_globals'] = ""
    content = try_eval('f"""' + content.replace('"""', r'\"\"\"') + '"""', glo_vars=glo_vars)
    if content:
        content = content.replace(r'\"\"\"', '"""')     # recover docstring delimiters

    for key, fun in replacer.items() or ((TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID, replace_with_file_content_or_default),):
        beg = 0
        pre = TEMPLATE_PLACEHOLDER_ID_PREFIX + key + TEMPLATE_PLACEHOLDER_ID_SUFFIX
        len_pre = len(pre)
        suf = TEMPLATE_PLACEHOLDER_ARGS_SUFFIX
        len_suf = len(suf)

        while True:
            beg = content.find(pre, beg)
            if beg == -1:
                break
            end = content.find(suf, beg)
            assert end != -1, f"patch_string() placeholder {key} is missing args suffix marker ({suf})"
            content = content[:beg] + fun(content[beg + len_pre: end]) + content[end + len_suf:]

    return content


def pdv_str(pdv: PdvType, var_name: str) -> str:
    """ string value of project development variable :paramref:`~pdv_str.var_name` of :paramref:`~pdv_str.pdv`.

    :param pdv:                 project development variables dict.
    :param var_name:            name of variable.
    :return:                    variable value or if not exists in pdv then the constant/default value of the module
                                :mod:`de_setup_project` or if no constant with this name exists then an empty string.
    :raises AssertionError:     if the specified variable value is not of type `str`. in this case use the function
                                :func:`pdv_val` instead.
    """
    return pev_str(pdv, var_name)


def pdv_val(pdv: PdvType, var_name: str) -> Any:        # silly mypy does not allow PdvVarType
    """ determine value of project development variable from passed pdv or :mod:`de_setup_project` module constant.

    :param pdv:                 project environment variables dict.
    :param var_name:            name of the variable to determine the value of.
    :return:                    project env var or module constant value. empty string if variable is not defined.
    """
    return pev_val(pdv, var_name)


def project_dev_vars(project_path: str = "") -> PdvType:
    """ analyse and map an extended project development environment, including template/root projects and git status.

    :param project_path:        optional rel/abs path of the package/app/project root directory of a new and existing
                                project (defaults to the current working directory if empty or not passed).
    :return:                    dict/mapping with the determined project development variable values.
    """
    pdv = cast(PdvType, project_env_vars(project_path=project_path, cae=cae))
    group_name = cae.get_option('group') or pdv_str(pdv, 'repo_group')
    is_root = pdv_str(pdv, 'project_type') == ROOT_PRJ
    namespace_name = pdv_str(pdv, 'namespace_name')
    project_path = pdv_str(pdv, 'project_path')     # re-read as absolute path
    sep = os.linesep

    # RTD-build is failing if the Sphinx dependency is included without a pinned version (RTD default is 1.8.5).
    # RTD-build default for sphinx_rtd_theme is <0.5 (0.4.3 get used), pin to current version 0.5.2
    pdv['docs_requirements'] = \
        sep.join(("sphinx==4.1.1", "sphinx_autodoc_typehints", "sphinx-rtd-theme==0.5.2", "sphinx_paramlinks")) \
        if not namespace_name or is_root else ""                                # templates/..._test_requirements.txt

    pdv['prj_id'] = "_".join(pdv_str(pdv, _) for _ in ('repo_domain', 'repo_group', 'package_name', 'package_version'))
    pdv['project_name'] = " ".join(pdv_str(pdv, _) for _ in ('package_name', 'project_type', 'package_version'))
    pdv['project_parent'] = _project_parent_path(pdv)   # empty if project/package is not installed as editable/develop
    pdv['repo_group'] = group_name or pdv_str(pdv, 'STK_AUTHOR')
    pdv['tpl_projects'] = tpl_projects = _template_projects(pdv)
    if not is_root and tpl_projects and tpl_projects[0]['import_name'] == namespace_name:   # and namespace_name
        pdv['root_version'] = tpl_projects[0]['version']

    if namespace_name and is_root:
        namespace_len = len(namespace_name)
        pypi_host = pdv_str(pdv, 'PYPI_PROJECT_ROOT')

        imp_names = []
        por_vars = OrderedDict()
        pypi_refs_rst = []
        pypi_refs_md = []
        for package_name_version in cast(List[str], pdv_val(pdv, 'portions_packages')):
            p_name = package_name_version.split(PACKAGE_VERSION_SEP)[0]
            portion_path = os.path.join(os.path.dirname(project_path), p_name)
            import_name = p_name[:namespace_len] + '.' + p_name[namespace_len + 1:]

            pypi_refs_rst.append(f'* `{p_name} <{pypi_host}/{p_name}>`_')
            pypi_refs_md.append(f'* [{p_name}]({pypi_host}/{p_name} "{namespace_name} namespace portion {p_name}")')

            por_vars[p_name] = project_dev_vars(project_path=portion_path)

            imp_names.append(import_name)
            for e_mod in find_modules(portion_path, namespace_name, p_name):
                if e_mod != PY_INIT:
                    imp_names.append(import_name + '.' + e_mod[:-len(PY_EXT)])

        pdv['portions_pypi_refs'] = sep.join(pypi_refs_rst)                     # templates/..._README.rst
        pdv['portions_pypi_refs_md'] = sep.join(pypi_refs_md)                   # templates/..._README.md
        pdv['portions_import_names'] = (sep + " " * 4).join(imp_names)          # templates/docs/..._index.rst
        pdv['portions_project_vars'] = por_vars
        pdv['portions_presets'] = {
            'ALL': set(_['package_name'] for _ in por_vars.values()),
            'editable': set(_['package_name'] for _ in por_vars.values() if _['project_parent']),
            'modified': set(_['package_name'] for _ in por_vars.values() if _['git_uncommitted_files']),
            'local': set(_['package_name'] for _ in por_vars.values() if _['git_unpublished_files']),
            'develop': set(_['package_name'] for _ in por_vars.values() if _['git_current_branch'] == MAIN_BRANCH),
        }

    pdv.update({k: v for k, v in globals().items() if k.startswith('TEMPLATE_')})

    _git_vars_update(pdv)
    pdv['upstream_url'] = pdv_val(pdv, 'git_remotes').get('upstream', "")

    return pdv


def refresh_templates(f_vars: PdvType, *exclude_folders: str, **replacer: Replacer) -> Set[str]:
    """ convert ae namespace package templates found in the cwd or underneath (except excluded) to the final files.

    :param f_vars:              project env/dev variables dict of the destination project to patch/refresh,
                                providing values for (1) f-string template replacements, and (2) to control the template
                                registering, patching and deployment via the variables:

                                * `namespace_name`: template projects used to refresh the destination project.
                                * `project_path`: project path of the destination/patched project.
                                * `project_type`: template projects used to refresh the destination project.
                                * `repo_url`: remote repository url of the destination project.
                                * `TEMPLATES_FOLDER`: folder under the template project root, containing the templates.
                                * `tpl_projects`: template projects data (import name, project path and version).

                                .. hint:: use the function :func:`project_dev_vars` to create this dict.

    :param exclude_folders:     optional source path prefixes that will be excluded from templates searching/patching.

    :param replacer:            dict of optional replacer with key=placeholder-id and value=callable.
                                if not passed then only the replacer with id TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID and
                                its callable/func :func:`replace_with_file_content_or_default` will be executed.

    :return:                    set of patched destination file names.
    """
    tpl_projects: List[RegisteredTemplateProject] = pdv_val(f_vars, 'tpl_projects')
    tpl_folder = pdv_str(f_vars, 'TEMPLATES_FOLDER')

    join = os.path.join
    glb = partial(glob.glob, recursive=True)
    isf = os.path.isfile
    dst_files: Set[str] = set()
    for tpl_prj in tpl_projects:
        tpl_root = tpl_prj['path']
        patcher = f"{os.path.basename(tpl_root)} V{tpl_prj['version']}"
        tpl_path = join(tpl_root, tpl_folder)
        template_files = [file for file in glb(join(tpl_path, "**/.*")) + glb(join(tpl_path, "**/*")) if isf(file)]
        for tpl_file_path in template_files:
            rel_path = os.path.relpath(cast(str, os.path.dirname(tpl_file_path)), tpl_path)
            if all(not rel_path.startswith(folder_prefix) for folder_prefix in exclude_folders):
                deploy_template(cast(str, tpl_file_path), rel_path, patcher, f_vars, replacer, dst_files)

    return dst_files


def replace_with_file_content_or_default(args_str: str) -> str:
    """ return file content if file name specified in first string arg exists, else return empty string or 2nd arg str.

    :param args_str:            pass either file name or file name and default string separated by a comma character.
    :return:                    file content or default string or empty string (if file not exists and no default string
                                defined as 2nd argument string).
    """
    file_name, *default = args_str.split(",", maxsplit=1)
    file_name = file_name.strip()
    if os.path.exists(file_name):
        ret = read_file(file_name)
    elif default:
        try:
            ret = Literal(default[0]).value
        except (SyntaxError, ValueError, Exception):
            ret = try_eval(default[0], ignored_exceptions=(Exception, ))
            if ret is UNSET:
                ret = default[0]
    else:
        ret = ""
    return ret


# --------------- module helpers --------------------------------------------------------------------------------------


def _act_callable(action: str) -> Optional[Callable]:
    glo = globals()
    if action in glo:
        return glo[action]
    return getattr(REMOTE_REPO or globals()[REMOTE_CLASS_NAMES[_repo_domain()]], action, cae.show_help)


def _act_spec() -> ActionSpecification:
    return REGISTERED_ACTIONS.get(
        ACTION_NAME,
        REGISTERED_ACTIONS.get(
            (REMOTE_REPO and REMOTE_REPO.__class__.__name__ or REMOTE_CLASS_NAMES[_repo_domain()]) + "." + ACTION_NAME,
            {'local_action': True}))


def _available_actions() -> Set[str]:
    return set(action.split(".")[-1] for action in REGISTERED_ACTIONS)


def _check_arguments():
    """ check and possibly complete the command line arguments, after _prepare_act_exec/INI_PRJ-initialization. """
    act_spec = _act_spec()
    cae.dpo(f"   -- check arguments of requested action {ACTION_NAME} ({act_spec['docstring'].strip('. ')})")
    cae.vpo(f"    - action arguments: {ACTION_ARGS}")

    arg_count = len(ACTION_ARGS)
    if 'arg_names' in act_spec:
        pos_names = []
        opt_names = []
        for arg_names in act_spec['arg_names']:
            for arg_name in arg_names:
                if arg_name.startswith('--'):
                    opt_names.append(arg_name[2:])
                else:
                    pos_names.append(arg_name)
            pos_cnt = len(pos_names)
            pos_ok = pos_cnt <= arg_count if pos_cnt and pos_names[-1].endswith(ARG_MULTIPLES) else pos_cnt == arg_count
            if pos_ok and all(cae.get_option(opt_name) for opt_name in opt_names):
                break
        else:
            _exit_error(9, f"  **  expected arguments: {_expected_args(act_spec['arg_names'])}")
    elif arg_count:
        _exit_error(9, f"  **  no arguments expected, but got {ACTION_ARGS}")

    prj_type = pdv_str(INI_PDV, 'project_type')
    cae.dpo(f"    - detected project type '{prj_type}' in {pdv_str(INI_PDV, 'project_path')}")
    if prj_type not in act_spec['project_types']:
        _exit_error(33, f"  **  action '{ACTION_NAME}' only available for project types: {act_spec['project_types']}")

    if _debug_or_verbose():
        cae.po("    = passed checks of basic command line options and arguments")


def _check_arg_namespace(project_type: str) -> str:
    namespace_name = cae.get_option('namespace') or pdv_str(INI_PDV, 'namespace_name')
    if project_type == ROOT_PRJ and not namespace_name:
        _exit_error(9, "***   new root package expects the --namespace command line option")
    return namespace_name


def _check_args_path_package(namespace_name: str, project_type: str) -> Tuple[str, str, str]:
    is_portion = namespace_name and project_type != ROOT_PRJ
    parent_folders = pdv_val(INI_PDV, 'PARENT_FOLDERS')

    project_path = cae.get_option('path')
    if project_path:
        project_path = norm_path(project_path)
        parent_path = os.path.dirname(project_path)
        package_name = os.path.basename(project_path)   # overwriting cae.get_option('package')
        if os.path.basename(parent_path) not in parent_folders:
            parent_path = ""
    else:
        package_name = cae.get_option('package')
        if not package_name:
            _exit_error(9, f"action '{ACTION_NAME}' expects either --path or --package command line option specified")
        if is_portion and not package_name.startswith(namespace_name + '_'):
            package_name = namespace_name + '_' + package_name
        parent_path = _project_parent_path(INI_PDV)
        project_path = os.path.join(parent_path, package_name)
    if not parent_path:
        ipp = pdv_str(INI_PDV, 'project_path')
        _exit_error(9, f"no project parent folder ({parent_folders}) found above the current/project folder {ipp}")
    parent_folder = os.path.basename(parent_path)
    if parent_folder not in PARENT_FOLDERS:
        _exit_error(9, f"specified project --path '{project_path}' has invalid parent folder '{parent_folder}'")

    if _debug_or_verbose():
        cae.po("    = passed checks of portions command line argument expressions")

    return project_path, package_name, is_portion


def _check_commit_msg_file(pdv: PdvType) -> str:
    commit_msg_file = os.path.join(pdv_str(pdv, 'project_path'), COMMIT_MSG_FILE_NAME)
    if not os.path.isfile(commit_msg_file) or not read_file(commit_msg_file):
        _exit_error(81, f"***   missing commit message in {commit_msg_file}{_hint(prepare_commit)}")
    return commit_msg_file


def _check_folders_files_completeness(pdv: PdvType):
    project_path = pdv_str(pdv, 'project_path')
    project_type = pdv_str(pdv, 'project_type')
    changes: List[Union[Tuple]] = []

    if not cae.get_option('path'):
        cae.set_option('path', project_path)

    with _record_calls(ae.base, 'write_file', lambda _dst_fn, *_, **__: changes.append(('wf', _dst_fn, _, __)),
                       os, 'makedirs', lambda _dir: changes.append(('md', _dir))):
        _renew_prj_dir(pdv_str(pdv, 'namespace_name'), pdv_str(pdv, 'package_name'), project_path, project_type)

    if changes:
        cae.po(f"  --  missing {len(changes)} basic project folders/files:")
        if cae.verbose:
            cae.po(PPF(changes))
            cae.po(f"   -- use the 'new-{project_type}' action to re-new/complete/update this project")
        else:
            for change in changes:
                cae.po(f"    - {change[0] == 'md' and 'folder' or 'file  '} {os.path.relpath(change[1], project_path)}")
    elif _debug_or_verbose():
        cae.po("    = project folders and files are complete and up-to-date")


def _check_resources_img(pdv: PdvType) -> List[str]:
    """ check images, message texts and sounds of the specified project. """
    local_images = FilesRegister()
    local_images.add_paths(os.path.join(pdv_str(pdv, 'project_path'), "img", "**"))
    for name, files in local_images.items():
        dup_files = duplicates(norm_path(str(file)) for file in files)
        assert not dup_files, f"duplicate image file paths for '{name}': {dup_files}"

    file_names: List[str] = []
    for name, files in local_images.items():
        file_names.extend(norm_path(str(file)) for file in files)
    dup_files = duplicates(file_names)
    assert not dup_files, f"image resources file paths duplicates: {dup_files}"

    for name, files in local_images.items():
        for file_name in (norm_path(str(file)) for file in files):
            assert read_file(file_name, extra_mode='b')
            # noinspection PyBroadException
            try:
                img = Image.open(file_name)
                img.verify()
            except Exception as ex:
                assert False, f"Pillow/PIL detected corrupt image file {file_name}; exception={ex}"

    if _debug_or_verbose():
        cae.po("    = passed image resources checks")

    return list(local_images.values())


def _check_resources_i18n_texts(pdv: PdvType) -> List[str]:
    local_msg_texts = FilesRegister()
    local_msg_texts.add_paths(os.path.join(pdv_str(pdv, 'project_path'), "loc", "**", "**Msg.txt"))

    for name, files in local_msg_texts.items():
        dup_files = duplicates(norm_path(str(file)) for file in files)
        assert not dup_files, f"duplicate translation messages file paths for '{name}': {dup_files}"

    file_names: List[str] = []
    for name, files in local_msg_texts.items():
        file_names.extend(norm_path(str(file)) for file in files)
    dup_files = duplicates(file_names)
    assert not dup_files, f"translation messages file paths duplicates: {dup_files}"

    for name, files in local_msg_texts.items():
        for file_name in (norm_path(str(file)) for file in files):
            content = read_file(file_name)
            assert content, f"empty translation message file {file_name}"
            eval_texts = try_eval(content, ignored_exceptions=(Exception, ))
            texts = ast.literal_eval(content)
            assert eval_texts == texts, f"eval and literal_eval results differ (in file {file_name})"
            assert isinstance(texts, dict), f"translation message file content must be a dict literal ({file_name})"
            for key, text in texts.items():
                assert isinstance(key, str), f"file content dict keys must be strings, but got {type(key)}"
                assert isinstance(text, (str, dict)), f"file content dict values must be str|dict, got {type(text)}"
                if isinstance(text, dict):
                    for sub_key, sub_txt in text.items():
                        assert isinstance(sub_key, str), f"sub-dict-keys must be strings, but got {type(sub_key)}"
                        if sub_key in ('app_flow_delay', 'fade_out_app', 'next_page_delay', 'page_update_delay',
                                       'tour_start_delay', 'tour_exit_delay'):
                            assert isinstance(sub_txt, float), f"sub-dict-values of {sub_key} must be floats"
                        else:
                            assert isinstance(sub_txt, str), f"sub-dict-values of {sub_key} must be strings"

    if _debug_or_verbose():
        cae.po("    = passed i18n translation texts checks")

    return list(local_msg_texts.values())


def _check_resources_snd(pdv: PdvType) -> List[str]:
    local_sounds = FilesRegister()
    local_sounds.add_paths(os.path.join(pdv_str(pdv, 'project_path'), "snd", "**"))

    for name, files in local_sounds.items():
        dup_files = duplicates(norm_path(str(file)) for file in files)
        assert not dup_files, f"duplicate sound file paths for '{name}': {dup_files}"

    file_names: List[str] = []
    for name, files in local_sounds.items():
        file_names.extend(norm_path(str(file)) for file in files)
    dup_files = duplicates(file_names)
    assert not dup_files, f"sound resources file paths duplicates: {dup_files}"

    for name, files in local_sounds.items():
        for file_name in (norm_path(str(file)) for file in files):
            assert read_file(file_name, extra_mode='b')

    if _debug_or_verbose():
        cae.po("    = passed sound resources checks")

    return list(local_sounds.values())


def _check_resources(pdv: PdvType):
    """ check images, message texts and sounds of the specified project. """
    resource_files = _check_resources_img(pdv) + _check_resources_i18n_texts(pdv) + _check_resources_snd(pdv)
    if resource_files:
        cae.po(f"  === {len(resource_files)} image/message-text/sound resource file checks passed")
        if _debug_or_verbose():
            cae.po(f"      {PPF(resource_files)}")


def _check_templates(pdv: PdvType):
    project_path = pdv_str(pdv, 'project_path')
    project_type = pdv_str(pdv, 'project_type')
    is_portion = pdv_str(pdv, 'namespace_name') and project_type != ROOT_PRJ
    rel_path = os.path.relpath

    missing: List[Tuple] = []
    outdated: List[Tuple] = []

    def _block_and_log_file_writes(dst_fn: str, content: AnyStr, extra_mode: str = ""):
        wf_args = (dst_fn, content, extra_mode)
        if not os.path.exists(dst_fn):
            missing.append(wf_args)
        else:
            old = read_file(dst_fn, extra_mode=extra_mode)
            if old != content:
                outdated.append(wf_args + (old, ))

    with _record_calls(ae.base, 'write_file', _block_and_log_file_writes,
                       os, 'makedirs', lambda _dir: None):
        checked = refresh_templates(pdv, *((pdv_str(pdv, 'DOCS_FOLDER'), ) if is_portion else ()))

    chk_files = " ".join(rel_path(fn, project_path) for fn in checked)
    mis_files = " ".join(rel_path(fn, project_path) for fn, *_ in missing)
    out_files = " ".join(rel_path(fn, project_path) for fn, *_ in outdated)
    tpl_projects: List[Dict[str, str]] = pdv_val(pdv, 'tpl_projects')
    verbose = cae.get_option('verbose')

    if _debug_or_verbose():
        tpl_files = PPF(tpl_projects) if cae.debug else " ".join(_['import_name'] for _ in tpl_projects)
        cae.po(f"   -- registered {len(tpl_projects)} template projects: {tpl_files}")

    if missing or outdated:
        if missing:
            cae.po(f"   -- {len(missing)} outsourced files missing:  {PPF(missing) if cae.debug else mis_files}")
        if outdated:
            cae.po(f"   -- {len(outdated)} outsourced files outdated: {PPF(outdated) if cae.debug else out_files}")
        for file_name, new_content, binary, old_content in outdated:
            cae.po(f"   -  {rel_path(file_name, project_path)}  ---")
            if verbose:
                if binary:
                    diff = cast(Iterator[str], [str(lin) for lin in diff_bytes(unified_diff, old_content, new_content)])
                elif cae.verbose:
                    diff = ndiff(old_content.splitlines(keepends=True), new_content.splitlines(keepends=True))
                else:
                    diff = context_diff(old_content.splitlines(keepends=True), new_content.splitlines(keepends=True))
            else:
                old_lines, new_lines = old_content.splitlines(keepends=True), new_content.splitlines(keepends=True)
                if cae.debug:
                    diff = unified_diff(old_lines, new_lines, n=cae.debug_level)
                else:
                    diff = cast(Iterator[str], [line for line in ndiff(old_lines, new_lines) if line[0:1].strip()])
            cae.po("      " + "      ".join(diff), end="")

        _exit_error(40, f"***** check cancelled. update templated files first via the 'new-{project_type}' action")

    elif checked:
        msg = ": " + (PPF(checked) if cae.debug else chk_files) if checked else ""
        cae.po(f"    = {len(checked)} outsourced files from {len(tpl_projects)} template projects are up-to-date{msg}")

    elif _debug_or_verbose():
        cae.po(f"    = no outsourced files found from {len(tpl_projects)} registered template projects")


def _check_types_linting_tests(pdv: PdvType):
    is_root = pdv_str(pdv, 'project_type') == ROOT_PRJ
    namespace_name = pdv_str(pdv, 'namespace_name')
    project_path = pdv_str(pdv, 'project_path')
    tests_folder = pdv_str(pdv, 'TESTS_FOLDER')
    excludes = [".buildozer"]
    line_len = 120
    args = []
    mypy_options = []
    if _debug_or_verbose():
        args.append("-v")
    if namespace_name and not is_root:
        mypy_options.append("--namespace-packages")
        args.append(namespace_name)
    else:
        args.append(pdv_str(pdv, 'version_file'))

    exclude_options = " ".join("--exclude " + _ for _ in excludes)
    ignore_options = " ".join("--ignore=" + _ for _ in excludes)
    with in_wd(project_path):
        _cl(60, f"flake8 --max-line-length={line_len} {exclude_options}", extra_args=args)

        os.makedirs("mypy_report", exist_ok=True)                               # _cl(61, "mkdir -p ./mypy_report")
        _cl(61, "mypy --show-error-codes --show-error-context --show-column-numbers"
            f" --pretty --lineprecision-report mypy_report {exclude_options}", extra_args=mypy_options + args)
        _cl(61, "anybadge --label=MyPy --value=passed --file=mypy_report/mypy.svg -o")

        os.makedirs(".pylint", exist_ok=True)
        out: List[str] = []
        _cl(62, f"pylint --output-format=text --max-line-length={line_len} {ignore_options} {' '.join(args)}",
            _exit_on_err=False, lines_output=out)   # instead of _exit_on_err, put the pylint option --exit-zero
        matcher = re.search("Your code has been rated at ([-0-9.]*)", os.linesep.join(out))
        if not matcher:
            _exit_error(62, f"   ** pylint score search failed in string {os.linesep.join(out)}")
        score = matcher.group(1)                                                                    # type: ignore
        _cl(62, f"anybadge -o --label=Pylint --file=.pylint/pylint.svg --value={score}"
                " 2=red 4=orange 8=yellow 10=green")
        cae.po(f"   == pylint score: {score}")

        if os.path.isdir(tests_folder):
            _cl(63, f"pytest --cov-report html --cov={not is_root and namespace_name or 'main'} {tests_folder}/")
            sub_dir = ".pytest_cache"
            cov_db = ".coverage"

            os.makedirs(sub_dir, exist_ok=True)
            os.rename(cov_db, os.path.join(sub_dir, cov_db))
            os.chdir(sub_dir)   # KIS: move .coverage and create coverage.txt/coverage.svg in the .pytest_cache sub-dir
            out = []
            _cl(63, "coverage report", lines_output=out)   # IO fixed: .coverage/COV_CORE_DATAFILE in cwd, txt->stdout
            write_file("coverage.txt", os.linesep.join(out))
            _cl(63, "coverage-badge -o coverage.svg -f")
            cov_rep_file = f"{project_path}/htmlcov/{pdv_str(pdv, 'package_name')}_py.html"
            if not os.path.isfile(cov_rep_file):
                cov_rep_file = f"{project_path}/htmlcov/index.html"
            cae.po(f"   == pytest coverage: {out[-1][-4:]} - check detailed report in file:///{cov_rep_file}")
            os.chdir("..")
        elif _debug_or_verbose():
            cae.po(f"    # skipping pytest because of missing unit test sub-folder '{tests_folder}'")

        if cae.verbose:
            cae.po(f"  --- files(hidden last) in/under {project_path}: {PPF(path_files('**/*') + path_files('**/.*'))}")


def _check_var(pdv: PdvType, var_name: str, var_value: Any):
    if cae.debug:
        new_value = pdv_str(pdv, var_name)
        dbg_msg = f" new={PPF(pdv)} ini={PPF(INI_PDV)}" if cae.verbose else ""
        assert new_value == var_value, f"{var_name.replace('_', ' ')} mismatch: {new_value} != {var_value}{dbg_msg}"


def _cl(err_no: int, command_line: str, _exit_on_err: bool = True, _exit_msg: str = "", **sh_kwargs: Any):
    if 'lines_output' not in sh_kwargs:
        sh_kwargs['lines_output'] = []

    sh_err = sh_exec(command_line, cae=cae, **sh_kwargs)

    if (sh_err and _exit_on_err) or _debug_or_verbose():
        for line in sh_kwargs['lines_output']:
            if cae.verbose or not line.startswith("LOG:  "):    # hiding mypy's end/useless (stderr) log entries
                cae.po(f"      {line}")
        cleaned_kwargs = sh_kwargs.copy()
        if not cae.debug:
            cleaned_kwargs.pop('lines_output')
        msg = f"command '{command_line}' {cleaned_kwargs or ''}"
        if not sh_err:
            cae.dpo(f"    = successfully executed {msg}")
        elif _exit_on_err:
            if _exit_msg:
                cae.po(f"      {_exit_msg}")
            _exit_error(err_no, f"  *** cl error {sh_err} in {msg}")        # app exit
        else:
            cae.dpo(f"    - ignoring cl error {sh_err} in {msg}")


def _exit_error(error_code: int, error_message: str = ""):
    """ quit this shell script, optionally displaying an error message. """
    if error_code <= 9:
        cae.show_help()
    if error_message:
        cae.po(error_message)
    cae.shutdown(error_code)


def _expected_args(arg_names: Tuple[Tuple[str, ...], ...]) -> str:
    return " or ".join(" ".join(_) for _ in arg_names)


@_recordable_function
def _git_add(pdv: PdvType):
    with in_wd(pdv_str(pdv, 'project_path')):
        _init_repo_if_not_exists()
        _cl(31, "git add -A")


def _git_checkout(pdv: PdvType, branch: str, from_branch: str = "", new_repo: bool = False):
    if not new_repo:
        changed = pdv_val(pdv, 'git_uncommitted_files')
        if changed:
            _exit_error(51, f"***   {pdv_str(pdv, 'package_name')} has {len(changed)} uncommitted files"
                            f" (in branch {_git_current_branch(pdv)}): {changed}; commit first")
    with in_wd(pdv_str(pdv, 'project_path')):
        _cl(57, f"git checkout -b {branch} {from_branch}")  # -B == -b -f

    _git_vars_update(pdv)


def _git_clone(repo_root: str, package_name: str, branch_or_tag: str = "", parent_path: str = "") -> Optional[str]:
    global TEMP_CONTEXT, TEMP_PARENT_FOLDER

    if not parent_path:
        if not TEMP_CONTEXT:
            TEMP_CONTEXT = tempfile.TemporaryDirectory()
            TEMP_PARENT_FOLDER = os.path.join(TEMP_CONTEXT.name, PARENT_FOLDERS[-1])
            _RCS[_rc_id(os, 'makedirs')](TEMP_PARENT_FOLDER)
        parent_path = TEMP_PARENT_FOLDER

    # https://stackoverflow.com/questions/791959/download-a-specific-tag-with-git says:
    # .. add -b <tag> to specify a release tag/branch to clone, adding --single-branch will speed-up the download
    extra_args = f" -b {branch_or_tag} --single-branch" if branch_or_tag else ""

    with in_wd(parent_path):
        _cl(40, f"git clone {repo_root}/{package_name}.git{extra_args}")
        return os.path.join(parent_path, package_name)


def _git_commit(pdv: PdvType, extra_options: Iterable[str] = ()):
    """ execute the command 'git commit -t=:data:`COMMIT_MSG_FILE_NAME`', with extra options, for the specified project.

    :param pdv:                 providing project-name and -path in which this git command gets executed.
    :param extra_options:       additional options passed to `git commit` command line, e.g. ["--patch", "--dry-run"].
    """
    file_name = _check_commit_msg_file(pdv)
    write_file(file_name, patch_string(read_file(file_name), pdv))
    with in_wd(pdv_str(pdv, 'project_path')):
        _cl(82, f"git commit --file={file_name} {' '.join(extra_options)}")


def _git_current_branch(pdv: PdvType) -> str:
    cur_branch: List[str] = []
    with in_wd(pdv_str(pdv, 'project_path')):
        _cl(27, "git branch --show-current", lines_output=cur_branch)
    return cur_branch and cur_branch[0] or ""


def _git_diff(pdv: PdvType) -> str:
    output: List[str] = []
    with in_wd(pdv_str(pdv, 'project_path')):
        compact_options = "" if cae.get_option('verbose') else "--compact-summary"      # alt: --name-only
        _cl(70, f"git diff --no-color --find-copies-harder --find-renames {compact_options}", lines_output=output)

    return os.linesep.join(output)


def _git_push(pdv: PdvType, branch: str, push_tags: bool = False):
    """ push portion in the current working directory to the specified branch. """
    protocol = pdv_str(pdv, 'REPO_HOST_PROTOCOL') or REPO_HOST_PROTOCOL
    domain = cae.get_option('domain') or REPO_CODE_DOMAIN
    group_name = pdv_str(INI_PDV, 'repo_group')
    package_name = pdv_str(pdv, 'package_name')
    usr = cae.get_option('gitUser')
    pwd = cae.get_option('gitToken')

    args = ["--tags"] if push_tags else []
    args.append(f"{protocol}{usr}:{pwd}@{domain}/{group_name}/{package_name}.git")
    args.append(branch)
    with in_wd(pdv_str(pdv, 'project_path')):
        _cl(80, "git push", extra_args=args)


def _git_remote(pdv: PdvType):
    with in_wd(pdv_str(pdv, 'project_path')):
        git_remotes: Dict[str, str] = pdv_val(pdv, 'git_remotes')
        repo_url = pdv_str(pdv, 'repo_url')
        if 'origin' not in git_remotes:
            _cl(32, f"git remote add origin {repo_url}")
        elif git_remotes['origin'] != repo_url:
            _cl(32, f"git remote set-url origin {repo_url}")


def _git_status(pdv: PdvType) -> str:
    output: List[str] = []
    with in_wd(pdv_str(pdv, 'project_path')):
        verbose_options = "=2 -vv --branch" if cae.get_option('verbose') else " -v"
        _cl(75, f"git status --find-renames --untracked-files=normal --porcelain{verbose_options}", lines_output=output)

    return os.linesep.join(output)


def _git_tag(pdv: PdvType):
    with in_wd(pdv_str(pdv, 'project_path')):
        _cl(87, "git tag -a", extra_args=(f"v{pdv_str(pdv, 'package_version')}", "-F", _check_commit_msg_file(pdv)))


def _git_vars_update(pdv: PdvType):
    pdv['git_branches'] = all_branches = cast(List[str], [])
    pdv['git_current_branch'] = ""
    pdv['git_uncommitted_files'] = uncommitted_files = cast(List[str], [])
    pdv['git_unpublished_files'] = unpublished_files = cast(List[str], [])
    pdv['git_remotes'] = remotes = {}

    project_path = pdv_str(pdv, 'project_path')
    if os.path.isdir(os.path.join(project_path, GIT_FOLDER_NAME)):
        with in_wd(project_path):

            remote_ids: List[str] = []
            _cl(21, "git remote", lines_output=remote_ids)
            for remote_id in remote_ids:
                remote_url: List[str] = []
                _cl(22, f"git remote get-url {remote_id}", lines_output=remote_url)
                remotes[remote_id] = remote_url[0]

            _cl(24, "git ls-files -m", lines_output=uncommitted_files)

            _cl(25, "git status --porcelain", lines_output=unpublished_files)
            unpublished_files[:] = [_[3:] for _ in unpublished_files]

            pdv['git_current_branch'] = _git_current_branch(pdv)

            _cl(27, "git branch -a --no-color", lines_output=all_branches)
            all_branches[:] = [branch_name[2:] for branch_name in all_branches]


def _hint(act_fun: Callable, run_grm_message_suffix: str = "") -> str:
    return f"{os.linesep}      (run: grm {act_fun.__name__}{run_grm_message_suffix})" if _debug_or_verbose() else ""


def _init_repo_if_not_exists() -> bool:
    if os.path.isdir(GIT_FOLDER_NAME):
        return False

    _cl(54, "git init")
    _cl(55, f"git checkout -b {MAIN_BRANCH}")
    _cl(56, "git commit", extra_args=("--allow-empty", "-m", "repository initialized by grm"))
    return True


def _patch_outsourced(file_name: str, content: str, patcher: str) -> str:
    ext = os.path.splitext(file_name)[1]
    sep = os.linesep
    if ext == '.md':
        beg, end = "<!--", "-->"
    elif ext == '.rst':
        beg, end = f"{sep}..{sep}   ", sep
    else:
        beg, end = "#", ""
    return f"{beg} {OUTSOURCED_MARKER} by the project {patcher} {end}{sep}{content}"


def _portion_args_package_names() -> List[str]:
    """ get package names of the portions specified as command line args, optionally filtered by --branch option. """
    if ACTION_ARGS == [ARG_ALL]:
        pkg_names = [_.split(PACKAGE_VERSION_SEP)[0] for _ in cast(List[str], pdv_val(INI_PDV, 'portions_packages'))]
    else:
        por_names = ACTION_ARGS
        names = try_eval(" ".join(por_names), (Exception, ), glo_vars=pdv_val(INI_PDV, 'portions_presets'))
        if isinstance(names, (list, set, tuple)):
            por_names = cast(List[str], names)

        pkg_prefix = pdv_str(INI_PDV, 'namespace_name') + '_'
        pkg_names = [("" if por_name.startswith(pkg_prefix) else pkg_prefix) + por_name for por_name in por_names]

    filter_branch = cae.get_option('branch')
    if filter_branch:
        portions_vars: Dict[str, Dict[str, Any]] = pdv_val(INI_PDV, 'portions_project_vars')
        pkg_names = [pkg for pkg in pkg_names if filter_branch in portions_vars[pkg]['git_branches']]

    if _debug_or_verbose() and len(pkg_names) < len(set(pkg_names)):
        cae.po(f"   ** {len(pkg_names) - len(set(pkg_names))} duplicate portions specified: {duplicates(pkg_names)}")

    return pkg_names


def _prepare_act_exec():
    """ init globals to prepare execution of requested action. """
    # global ACTION_ARGS, INI_PDV
    global ACTION_NAME, REMOTE_REPO

    ACTION_NAME = initial_action = norm_name(cae.get_argument('action'))
    ACTION_ARGS[:] = initial_args = cae.get_argument('arguments')
    actions = _available_actions()
    while ACTION_NAME not in actions:
        if not ACTION_ARGS:
            if initial_action in ACTION_SHORTCUTS:
                ACTION_NAME = ACTION_SHORTCUTS[initial_action]
                ACTION_ARGS[:] = initial_args
                break
            _exit_error(30, f"****  invalid action '{ACTION_NAME.replace('_', '-')}'. valid actions: {actions}")
        ACTION_NAME += '_' + norm_name(ACTION_ARGS[0])
        ACTION_ARGS[:] = ACTION_ARGS[1:]

    _register_args_and_local_templates()
    INI_PDV.update(project_dev_vars(project_path=cae.get_option('path')))
    extra_msg = ""

    if _debug_or_verbose():
        project_path = pdv_str(INI_PDV, 'project_path')
        cur_branch = pdv_str(INI_PDV, 'git_current_branch')
        if cur_branch != MAIN_BRANCH:
            cae.po(f"   -- current working branch of project at '{project_path}' is '{cur_branch}'")
        changed = pdv_val(INI_PDV, 'git_uncommitted_files')
        if changed:
            cae.po(f"   -- '{project_path}' has {len(changed)} uncommitted files: {changed}")
        extra_msg += f" ({project_path})"

    act_spec = _act_spec()
    if not act_spec['local_action']:
        personal_token = cae.get_option('gitToken') or input("...... enter personal access token:")
        if not personal_token:
            _exit_error(36, f"****  empty git host personal access token '{personal_token}'")

        repo_domain = _repo_domain()
        REMOTE_REPO = globals()[REMOTE_CLASS_NAMES[_repo_domain()]]()
        if not _act_callable(ACTION_NAME):
            _exit_error(38, f"****  action {ACTION_NAME} not implemented for {repo_domain}")
        if not REMOTE_REPO.connect(personal_token):
            _exit_error(39, f" ***  connection to {repo_domain} remote host server failed")

    if '_portions' in ACTION_NAME:  # multiple namespace portions action, where INI_PDV is from a namespace root project
        PORTIONS_ARGS.extend(_portion_args_package_names())
        extra_msg += f" portions ({len(PORTIONS_ARGS)}): {' '.join(PORTIONS_ARGS)}" if PORTIONS_ARGS else ""

    cae.po(f"----- {ACTION_NAME}: {pdv_str(INI_PDV, 'project_name')}{extra_msg}")


def _print_pdv(pdv: PdvType):
    cae.po(f"  --- {pdv['prj_id' if cae.debug else 'project_name']} project environment:")

    if not cae.get_option('verbose'):
        pdv = pdv.copy()
        pdv['setup_kwargs'] = pdv['setup_kwargs'].copy()
        nsp_len = len(pdv['namespace_name']) + 1    # namespace prefix length; not needs if pdv['namespace_name'] else 0

        pdv['data_files'] = [f"{sub_dir or '.': <15} == {' '.join(file[len(sub_dir):].strip('/') for file in files)}"
                             for sub_dir, files in pdv['data_files']]
        pdv['docs_require'] = " ".join(pdv['docs_require'])
        pdv['git_branches'] = " ".join(pdv['git_branches'])
        pdv['git_uncommitted_files'] = " ".join(pdv['git_uncommitted_files'])
        pdv['git_unpublished_files'] = " ".join(pdv['git_unpublished_files'])
        pdv['git_remotes'] = " ".join(f"{name}={url}" for name, url in pdv['git_remotes'].items())
        pdv['install_require'] = " ".join(pdv['install_require'])
        if 'long_desc_content' in pdv:
            pdv['long_desc_content'] = pdv['setup_kwargs']['long_description'] = pdv['long_desc_content'][:33] + "..."
        pdv['portions_packages'] = " ".join(pkg_name[nsp_len:] for pkg_name in pdv['portions_packages'])
        if pdv['project_type'] == ROOT_PRJ:
            pdv['portions_presets'] = [f"{preset: <9} == {' '.join(pkg_name[nsp_len:] for pkg_name in dep_packages)}"
                                       for preset, dep_packages in pdv['portions_presets'].items()]
        pdv['project_packages'] = " ".join(pdv['project_packages'])
        pdv['project_resources'] = " ".join(pdv['project_resources'])
        pdv['setup_require'] = " ".join(pdv['setup_require'])
        pdv['tests_require'] = " ".join(pdv['tests_require'])

    if not cae.verbose:
        pdv = pdv.copy()
        for name, val in list(pdv.items()):
            if not val or name in (
                    name.upper(), 'import_name', 'long_desc_content', 'long_desc_type', 'namespace_name', 'pip_name',
                    'portion_name', 'portions_pypi_refs', 'portions_pypi_refs_md', 'portions_import_names',
                    'portions_project_vars', 'repo_domain', 'repo_group', 'repo_host', 'repo_root', 'setup_kwargs', ):
                pdv.pop(name, None)

    cae.po(PPF(pdv))


def _project_parent_path(pdv: PdvType) -> str:
    parent_folders = pdv_val(pdv, 'PARENT_FOLDERS')[:-1]    # exclude dynamically added home/user folder
    parent_path = pdv_str(pdv, 'project_path') or os.getcwd()
    while os.path.basename(parent_path) not in parent_folders:
        if not parent_path or parent_path == os.path.sep:
            return ""
        parent_path = os.path.dirname(parent_path)
    return parent_path


def _register_args_and_local_templates():
    """ register local and arg-requested tpl versions, called on app start when REGISTERED_TPL_PROJECTS is clear. """
    for namespace_name in cae.get_option('namespaces'):
        project_path = package_project_path(namespace_name)
        if project_path:
            _register_template_project(namespace_name, project_path=project_path)

    for import_name in TPL_PACKAGES:
        project_path = package_project_path(import_name)
        if project_path:
            _register_template_project(import_name, project_path=project_path)

        tpl_version = cae.get_option(norm_name(import_name.split('.')[-1]) + TPL_VERSION_OPTION_SUFFIX)
        if tpl_version and (not project_path or tpl_version != REGISTERED_TPL_PROJECTS[import_name]['version']):
            _register_template_project(import_name, tpl_ver=tpl_version)


def _register_project_templates(project_templates_packages_versions: List[str], namespace_name: str):
    # register projects if the current action project (e.g. INI_PDV or PRJ_PDV)
    ns_len = len(namespace_name)
    for package_sep_version in project_templates_packages_versions:
        pkg_name, *ver = package_sep_version.split(PACKAGE_VERSION_SEP)
        import_name = (pkg_name[:ns_len] + '.' + pkg_name[ns_len + 1:]).strip('.')
        if ver and not any(norm_name(reg['import_name']) == pkg_name and reg['version'] == ver[0]
                           for reg in REGISTERED_TPL_PROJECTS.values()):
            # tpl_root=pdv_str(project_env_vars(project_path=package_project_path('de.setup_project')), 'repo_root')
            # .. would break ae-group because is patching de.setup_project.REPO_GROUP_SUFFIX in the grm runtime module.
            _register_template_project(import_name, tpl_ver=ver[0], tpl_root='https://gitlab.com/degroup')
        elif not ver and import_name not in REGISTERED_TPL_PROJECTS:
            project_path = package_project_path(import_name)
            if project_path:
                _register_template_project(import_name, project_path=project_path)
            else:
                cae.dpo(f"    - template project {import_name} not found")


def _register_template_project(import_name: str, project_path: str = "", tpl_ver: str = "", tpl_root: str = "") -> str:
    # global REGISTERED_TPL_PROJECTS
    assert project_path or tpl_ver, "_register_template_project() expects arguments project_path, or tpl_ver, or both"
    key = import_name
    if tpl_ver:
        key += PACKAGE_VERSION_SEP + tpl_ver
        if not project_path and tpl_root:
            project_path = _git_clone(tpl_root, norm_name(import_name), branch_or_tag=tpl_ver) or ""
    else:
        tpl_ver = code_file_version(project_main_file(import_name, project_path=project_path))
        if not tpl_ver:
            tpl_ver = module_attr(import_name, attr_name='__version__', project_path=project_path)
    cae.vpo(f"    - registered {import_name} package {tpl_ver} as template id '{key}'")

    REGISTERED_TPL_PROJECTS[key] = {
        'import_name': import_name,
        'path': project_path,
        'version': tpl_ver,
    }

    return key


def _renew_prj_dir(namespace_name: str, package_name: str, project_path: str, project_type: str):
    portion_name = package_name[len(namespace_name) + 1:]
    import_name = namespace_name + '.' + portion_name if namespace_name and portion_name else package_name
    is_root = project_type == ROOT_PRJ
    is_portion = namespace_name and not is_root

    is_file = os.path.isfile
    is_dir = os.path.isdir
    join = os.path.join
    sep = os.linesep

    sub_dir = join(project_path, pdv_str(INI_PDV, 'DOCS_FOLDER'))
    if (not namespace_name or is_root) and not is_dir(sub_dir):
        _RCS[_rc_id(os, 'makedirs')](sub_dir)

    tpl_folder = pdv_str(INI_PDV, 'TEMPLATES_FOLDER')
    sub_dir = join(project_path, tpl_folder)
    if is_root and not is_dir(sub_dir):
        _RCS[_rc_id(os, 'makedirs')](sub_dir)

    sub_dir = join(project_path, pdv_str(INI_PDV, 'TESTS_FOLDER'))
    if not is_dir(sub_dir):
        _RCS[_rc_id(os, 'makedirs')](sub_dir)

    file_name = join(project_path, pdv_str(INI_PDV, 'BUILD_CONFIG_FILE'))
    if project_type == APP_PRJ and not is_file(file_name):
        _RCS[_rc_id(ae.base, 'write_file')](file_name, f"# {OUTSOURCED_MARKER}{sep}[app]{sep}")

    file_name = join(project_path, '.python-version')  # virtual env name defaults to namespace/package name
    if not is_file(file_name):
        _RCS[_rc_id(ae.base, 'write_file')](file_name, namespace_name if is_portion else package_name)

    file_name = join(project_path, pdv_str(INI_PDV, 'REQ_FILE_NAME'))
    if not is_file(file_name):
        _RCS[_rc_id(ae.base, 'write_file')](file_name, f"# runtime dependencies of the {import_name} project")

    file_name = join(project_path, pdv_str(INI_PDV, 'REQ_TEST_FILE_NAME'))
    if not is_file(file_name) and not is_file(file_name + LOCK_EXT):
        # provide at least basic templates - to allow that this file will be overwritten by a later registered template
        tpl = join(os.path.dirname(project_path), 'de_tpl_project', tpl_folder, 'de_otf_de_tpl_test_requirements.txt')
        if is_file(tpl):
            deploy_template(tpl, "", "grm._renew_prj_dir", INI_PDV)
        else:
            cae.dpo(f"    * ignoring missing template file {tpl}")

    main_file = project_main_file(import_name, project_path=project_path)
    if not main_file:
        main_name = ('main' if project_type in (APP_PRJ, ROOT_PRJ) else
                     portion_name if is_portion else package_name) + PY_EXT
        if is_portion:
            main_path = join(project_path, *namespace_name.split('.'))
            if not is_dir(main_path):
                _RCS[_rc_id(os, 'makedirs')](main_path)
                if project_type == PACKAGE_PRJ:
                    main_name = PY_INIT
                    main_path = join(main_path, portion_name if is_portion else package_name)
                    _RCS[_rc_id(os, 'makedirs')](main_path)
        else:
            main_path = project_path
        main_file = norm_path(join(main_path, main_name))
    if not is_file(main_file):
        _RCS[_rc_id(ae.base, 'write_file')](main_file, f"\"\"\" {package_name} {project_type} main module \"\"\"{sep}"
                                                       f"{sep}"
                                                       f"__version__ = '0.0.0'")


def _renew_project(project_type: str):
    # global PRJ_PDV
    namespace_name = _check_arg_namespace(project_type)
    project_path, package_name, is_portion = _check_args_path_package(namespace_name, project_type)

    PRJ_PDV.clear()
    PRJ_PDV.update({'project_path': project_path, 'package_name': package_name})

    if not os.path.isdir(project_path):
        _RCS[_rc_id(os, 'makedirs')](project_path)

    with in_wd(project_path):
        new_repo = _init_repo_if_not_exists()
    if _git_current_branch(PRJ_PDV) == MAIN_BRANCH:
        branch_name = norm_name(
            cae.get_option('branch') or ("" if new_repo else "re") + "new_" + project_type + "_" + package_name)
        if branch_name != MAIN_BRANCH:
            _git_checkout(PRJ_PDV, branch_name, MAIN_BRANCH, new_repo=new_repo)

    _renew_prj_dir(namespace_name, package_name, project_path, project_type)

    PRJ_PDV.update(project_dev_vars(project_path=project_path))

    # debug asserts checking if project_env_vars() is correctly recognizing the just completed project type/name/version
    _check_var(PRJ_PDV, 'namespace_name', namespace_name)
    _check_var(PRJ_PDV, 'package_name', package_name)
    _check_var(PRJ_PDV, 'project_path', project_path)
    _check_var(PRJ_PDV, 'project_type', project_type)

    dst_files = refresh_templates(PRJ_PDV, *((pdv_str(PRJ_PDV, 'DOCS_FOLDER'),) if is_portion else ()))
    dbg_msg = ": " + " ".join(os.path.relpath(_, project_path) for _ in dst_files) if _debug_or_verbose() else ""
    cae.po(f"    - renewed {len(dst_files)} outsourced files{dbg_msg}")
    PRJ_PDV.update(project_dev_vars(project_path=project_path))

    _git_add(PRJ_PDV)
    _git_remote(PRJ_PDV)

    if is_portion:
        _renew_root_req_file(namespace_name, package_name, pdv_str(PRJ_PDV, 'REQ_FILE_NAME'))


def _renew_root_req_file(namespace_name: str, package_name: str, req_file: str):
    root_prj_path = REGISTERED_TPL_PROJECTS[namespace_name]['path']
    root_req = os.path.join(root_prj_path, req_file)
    if not os.path.isfile(root_req):
        _exit_error(9, f"{req_file} not found in {namespace_name} namespace root project path {root_prj_path}")
    req_content = read_file(root_req)
    if not _required_package(package_name, req_content):
        sep = os.linesep
        if not req_content.endswith(sep):
            req_content += sep
        write_file(root_req, req_content + package_name + sep)


def _repo_domain() -> str:
    repo_domain = cae.get_option('domain')
    domains = tuple(REMOTE_CLASS_NAMES.keys())
    if repo_domain and repo_domain not in domains:
        _exit_error(9, f"specified --remote host {repo_domain} not supported/implemented, pass {' or '.join(domains)}")
    return repo_domain or pdv_str(INI_PDV, 'repo_domain') or REPO_CODE_DOMAIN


def _required_package(package_name: str, packages_versions: List[str]) -> bool:
    return package_name in packages_versions or \
           any(_.startswith(package_name + PACKAGE_VERSION_SEP) for _ in packages_versions)


def _template_projects(pdv: PdvType) -> List[RegisteredTemplateProject]:
    """ determine template project paths/versions for the actual project_type/namespace, specified by pdv argument. """
    namespace_name = pdv_str(pdv, 'namespace_name')
    project_name = pdv_str(pdv, 'project_name')
    project_type = pdv_str(pdv, 'project_type')
    tests_require = pdv_val(pdv, 'tests_require')
    debug_msg = f"    * {project_name}: no {{name}} package in {pdv_str(pdv, 'REQ_TEST_FILE_NAME')}->templates blocked!"

    tpl_packages_versions = [_ for _ in tests_require
                             if _ == namespace_name or _.startswith(pdv_str(pdv, 'TPL_PACKAGE_NAME_PREFIX'))]
    _register_project_templates(tpl_packages_versions, namespace_name)

    tpl_projects = []   # collect projects of namespace, project type and generic project (highest priority first)

    if namespace_name:
        if namespace_name in tests_require:
            path = package_project_path(namespace_name)
            tpl_projects.append({'import_name': namespace_name, 'path': path,
                                 'version': code_file_version(project_main_file(namespace_name, project_path=path))})
        else:
            cae.dpo(debug_msg.format(name=f"{namespace_name} {ROOT_PRJ}"))

    prj_type_tpl = TPL_IMPORT_NAME_PREFIX + norm_name(project_type)
    if prj_type_tpl in REGISTERED_TPL_PROJECTS:
        if _required_package(norm_name(prj_type_tpl), tpl_packages_versions):
            tpl_projects.append(REGISTERED_TPL_PROJECTS[prj_type_tpl])
        else:
            cae.dpo(debug_msg.format(name=prj_type_tpl))

    prj_tpl = TPL_IMPORT_NAME_PREFIX + 'project'
    if prj_tpl in REGISTERED_TPL_PROJECTS:
        if _required_package(norm_name(prj_tpl), tpl_packages_versions):
            tpl_projects.append(REGISTERED_TPL_PROJECTS[prj_tpl])
        else:
            cae.dpo(debug_msg.format(name=prj_tpl))

    return tpl_projects


def _write_commit_message(pdv: PdvType):
    sep = os.linesep
    write_file(os.path.join(pdv_str(pdv, 'project_path'), COMMIT_MSG_FILE_NAME),
               f"V{{package_version}}: {sep}{sep}{_git_status(pdv)}")


# --------------- remote repo connection ------------------------------------------------------------------------------


class _RemoteHost:
    """ base class registering sub-classes as remote host repo class in :data:`REMOTES_CLASS_NAMES`. """
    def __init_subclass__(cls, **kwargs):
        """ register remote host class name; called on declaration of a subclass of :class:`_RemoteHost`. """
        # global REMOTE_CLASS_NAMES

        REMOTE_CLASS_NAMES[camel_to_snake(cls.__name__)[1:].replace('_', '.').lower()] = cls.__name__
        super().__init_subclass__(**kwargs)


class GithubCom(_RemoteHost):
    """ remote connection and actions on remote repo in github.com. """
    connection: Github                  #: connection to Gitlab/Github host

    def connect(self, personal_token: str) -> bool:
        """ connect to github.com remote host.

        :param personal_token:  personal token string.
        :return:                True on successful authentication else False.
        """
        try:
            self.connection = Github(personal_token)
        except (Exception, ) as ex:
            cae.po(f"****  Github connection exception: {ex}")
            return False
        return True

    # ----------- remote action methods ----------------------------------------------------------------------------

    @_action(PARENT_PRJ, arg_names=(('fork-repo-remote-url', ), ))
    def new_fork(self):
        """ create/renew fork of repo, specified by the action argument, to the current user/group. """
        prj = self.connection.get_repo(ACTION_ARGS[0])
        self.connection.get_user().create_fork(prj)


class GitlabCom(_RemoteHost):
    """ remote connection and actions on gitlab.com. """
    connection: Gitlab                  #: connection to Gitlab/Github host

    def connect(self, personal_token: str) -> bool:
        """ connect to gitlab.com remote host.

        :param personal_token:  personal token string.
        :return:                True on successful authentication else False.
        """
        try:
            self.connection = Gitlab(pdv_str(INI_PDV, 'repo_host'), private_token=personal_token)
            if cae.debug:
                self.connection.enable_debug()
            self.connection.auth()  # authenticate and create user attribute
        except (Exception, ) as ex:
            cae.po(f"****  Gitlab connection exception: {ex}")
            return False
        return True

    def group_id_from_name(self, group_name: str) -> str:
        """ convert group/user name to remote repo user id

        :param group_name:      group name to convert.
        :return:                gitlab group id of the group name passed in :paramref:`~group_id_from_name.group_name`.
        """
        return self.connection.groups.list(search=group_name)[0].id                 # type: ignore

    # ----------- remote action methods ----------------------------------------------------------------------------

    @_action(ROOT_PRJ)
    def deploy_portions(self):
        """ update common files and then deploy to specified/all portion repos of a namespace. """

    @_action(PARENT_PRJ, *ANY_PRJ_TYPE, arg_names=(('group/project', '--branch'), ))
    def new_fork(self):
        """ create/renew fork of repo specified by the action arg onto remote/git-host to our user/group namespace. """
        upstream_url = pdv_str(INI_PDV, 'upstream_url')
        if upstream_url:    # only renew origin from upstream if already forked
            with in_wd(pdv_str(INI_PDV, 'project_path')):
                _cl(20, f"git checkout {MAIN_BRANCH}")
                _cl(20, "git fetch upstream")
                _cl(20, f"git pull upstream {MAIN_BRANCH}")
                _cl(20, f"git push origin {MAIN_BRANCH}")
        else:
            grp_prj_path = ACTION_ARGS[0]
            group_name, project_name = grp_prj_path.split('/')
            prj = self.connection.projects.get(grp_prj_path)
            # moved to connect method: self.connection.auth()  # authenticate and create user attribute
            usr_name = self.connection.user.name
            protocol = pdv_str(INI_PDV, 'REPO_HOST_PROTOCOL') or REPO_HOST_PROTOCOL
            domain = cae.get_option('domain') or REPO_CODE_DOMAIN
            parent_path = pdv_str(INI_PDV, 'project_path')
            if pdv_str(INI_PDV, 'project_type') != PARENT_PRJ:
                parent_path = os.path.dirname(parent_path)
            project_path = os.path.join(parent_path, project_name)
            # prj.forks.create({'namespace': usr_name})
            prj.forks.create({})
            with in_wd(parent_path):
                _cl(21, f"git clone {protocol}{domain}/{usr_name}/{project_name}.git")
            with in_wd(project_path):
                _cl(21, f"git remote add upstream {protocol}{domain}/{group_name}/{project_name}")

        _git_checkout(INI_PDV, norm_name(cae.get_option('branch')))

    @_action()
    def push(self, release: bool = False):
        """ push project/package to remote domain. """
        group_name = pdv_str(INI_PDV, 'repo_group')
        package_name = pdv_str(INI_PDV, 'package_name')
        # using list because get raises 'gitlab.exceptions.GitlabGetError: 404: 404 Project Not Found' if prj not exists
        # project = self.connection.projects.get(group_name + '/' + package_name)
        prj_list = self.connection.projects.list(owned=True, search=package_name)
        if not prj_list:
            group_id = self.group_id_from_name(group_name)
            project_properties = {
                # ? using 'path' instead of 'name': 'project1', to specify namespace packages under the groupXY
                # path can contain only letters, digits, '_', '-' and '.'. Cannot start with '-', end in '.git'/'.atom'
                # 'path': pdv_str(INI_PDV, 'repo_url'),
                'name': package_name,
                'namespace_id': group_id,
                'description': pdv_str(INI_PDV, 'project_desc'),
                'default_branch': MAIN_BRANCH,
                'visibility': 'public'}
            cae.vpo(f"    - remote project properties of new package {package_name}: {project_properties}")
            project = cast(Project, self.connection.projects.create(project_properties))

            cae.dpo(f"   -- created project {project} under remote user/group {group_name}")

        branch_name = cae.get_option('branch') or pdv_str(INI_PDV, 'git_current_branch')
        if release:
            _git_tag(INI_PDV)
        _git_push(INI_PDV, branch=branch_name, push_tags=release)

    @_action()
    def release(self):
        """ push project/package to remote domain as new release. """
        if pdv_str(INI_PDV, 'upstream_url'):
            _exit_error(44, "forked repo can't be released" + _hint(self.push, " to origin+merge-request to upstream"))

        self.push(release=True)

        branch_name = f"release{pdv_str(INI_PDV, 'package_version')}"
        _git_checkout(INI_PDV, branch=branch_name, from_branch=MAIN_BRANCH)
        _git_push(INI_PDV, branch=branch_name)

    @_action(arg_names=(('group/project', ), ))
    def show_repo(self):
        """ determine properties of remote repository. """
        user_repo_name = ACTION_ARGS[0]
        # setup_prj = self.connection.projects.get('degroup/de_setup_project')
        # base_prj = self.connection.projects.get('ae-group/ae_base')
        repo = self.connection.projects.get(user_repo_name)
        cae.po(f"----  {user_repo_name} info:")
        cae.po(PPF(repo))

    @_action(arg_names=(('project-name-fragment', ), ))
    def search_repos(self):
        """ search remote repositories via project name fragment. """
        project_name_fragment = ACTION_ARGS[0]
        repos = self.connection.projects.list(owned=True, search=project_name_fragment)
        cae.po(f"----  found {len(repos)} project repositories containing {project_name_fragment}:")
        for repo in repos:
            cae.po(PPF(repo))


# --------------- local and remote action functions -------------------------------------------------------------------


@_action(APP_PRJ, MODULE_PRJ, PACKAGE_PRJ, ROOT_PRJ)
def bump_version():
    """ increment project version. """
    old_version = pdv_str(INI_PDV, 'package_version')
    bump_file_version(pdv_str(INI_PDV, 'version_file'), version_part=cae.get_option('version_increment_part'))
    INI_PDV.update(project_dev_vars(pdv_str(INI_PDV, 'project_path')))
    cae.po(f"    # bumped version {old_version} to {pdv_str(INI_PDV, 'package_version')}")


@_action()
def check_integrity():
    """ integrity check of files/folders completeness, outsourced/template files update-state and CI tests. """
    project_path = pdv_str(INI_PDV, 'project_path')
    project_type = pdv_str(INI_PDV, 'project_type')

    if project_type in (NO_PRJ, PARENT_PRJ):
        cae.po(f"  === nothing to check for {project_type or 'undefined'} project type at {project_path}")
        return

    _check_folders_files_completeness(INI_PDV)
    _check_templates(INI_PDV)
    _check_resources(INI_PDV)
    _check_types_linting_tests(INI_PDV)
    cae.po(f"  === {pdv_str(INI_PDV, 'project_name')} successfully passed integrity checks")


@_action(ROOT_PRJ, arg_names=((ARG_ALL, ), ('portions-sets-expr', ), ('portion-names' + ARG_MULTIPLES, )))
def check_portions_integrity():
    """ run integrity checks for the specified portions of a namespace. """
    portions_vars = pdv_val(INI_PDV, 'portions_project_vars')
    for package_name in PORTIONS_ARGS:
        por_pdv: PdvType = portions_vars[package_name]
        cae.po(f" ---  {pdv_str(por_pdv, 'portion_name') + '  ---': <18}{pdv_str(por_pdv, 'project_desc')}")
        _check_folders_files_completeness(por_pdv)
        _check_templates(por_pdv)
        _check_resources(por_pdv)
        _check_types_linting_tests(por_pdv)
        cae.po(f"  === {pdv_str(por_pdv, 'project_name')} successfully passed integrity checks")


@_action(PARENT_PRJ, arg_names=(('--domain', '--group', '--package'), ))
def clone_project():
    """ clone remote repo to the local machine. """
    repo_root = f"{pdv_str(INI_PDV, 'REPO_HOST_PROTOCOL')}{cae.get_option('domain')}/{cae.get_option('group')}"
    package_name = norm_name(cae.get_option('package'))
    project_path = _git_clone(repo_root, package_name, cae.get_option('branch'), pdv_str(INI_PDV, 'project_path'))
    cae.po(f"  === project {package_name} cloned from {repo_root} into project path {project_path}")


@_action(ROOT_PRJ,
         arg_names=(('--domain', '--group', '--package', ARG_ALL),
                    ('--domain', '--group', '--package', 'portions-sets-expr'),
                    ('--domain', '--group', '--package', 'portion-names' + ARG_MULTIPLES)))
def clone_portions():
    """ clone specified namespace portion repos to the local machine. """
    repo_root = f"{pdv_str(INI_PDV, 'REPO_HOST_PROTOCOL')}{cae.get_option('domain')}/{cae.get_option('group')}"
    portions_vars = pdv_val(INI_PDV, 'portions_project_vars')
    for package_name in PORTIONS_ARGS:
        por_pdv: PdvType = portions_vars[package_name]
        package_name = pdv_str(por_pdv, 'package_name')
        project_path = _git_clone(repo_root, package_name, cae.get_option('branch'), pdv_str(INI_PDV, 'project_path'))
        cae.po(f"   == {package_name} cloned from {repo_root} into project path {project_path}")


@_action(APP_PRJ, MODULE_PRJ, PACKAGE_PRJ, ROOT_PRJ)
def commit_project():
    """ commit changes to local repo using the prepared commit message in :data:`COMMIT_MSG_FILE_NAME`. """
    _git_add(INI_PDV)
    _git_commit(INI_PDV)
    cae.po(f"  === {pdv_str(INI_PDV, 'project_name')} successfully committed")


@_action(ROOT_PRJ, arg_names=((ARG_ALL, ), ('portions-sets-expr', ), ('portion-names' + ARG_MULTIPLES, )))
def commit_portions():
    """ commit changes to the portions of a namespace using the prepared message in :data:`COMMIT_MSG_FILE_NAME`. """
    portions_vars = pdv_val(INI_PDV, 'portions_project_vars')
    for package_name in PORTIONS_ARGS:
        por_pdv: PdvType = portions_vars[package_name]
        cae.po(f" ---  {pdv_str(por_pdv, 'portion_name') + '  ---': <18}{pdv_str(por_pdv, 'project_desc')}")
        _git_add(por_pdv)
        _git_commit(por_pdv)
    cae.po(f"  === committed {len(PORTIONS_ARGS)} {pdv_str(INI_PDV, 'namespace_name')} portions: {PORTIONS_ARGS}")


@_action(ROOT_PRJ, arg_names=((ARG_ALL, ), ('portions-sets-expr', ), ('portion-names' + ARG_MULTIPLES, )))
def install_portions_editable():
    """ install namespace portions as editable on local machine. """
    parent_path = os.path.dirname(pdv_str(INI_PDV, 'project_path'))
    for package_name in PORTIONS_ARGS:
        por_path = os.path.join(parent_path, package_name)
        if not os.path.exists(por_path):
            cae.po(f"local portions project root-folder/working-tree {por_path} not found")
        else:
            _cl(90, f"pip install -e {por_path}", _exit_msg=f"installation from local portions path {por_path} failed")
    cae.po(f"  === installed {len(PORTIONS_ARGS)} {pdv_str(INI_PDV, 'namespace_name')} portions: {PORTIONS_ARGS}")


@_action(arg_names=(('--path', ), ('--package', )))
def new_app():
    """ create or complete/renew an gui app project. """
    _renew_project(APP_PRJ)


@_action(arg_names=(('--path', ), ('--package', )))
def new_module():
    """ create or complete/renew module project. """
    _renew_project(MODULE_PRJ)


@_action(arg_names=(('--path', ), ('--package', )))
def new_package():
    """ create or complete/renew package project. """
    _renew_project(PACKAGE_PRJ)


@_action(arg_names=(('--path', ), ('--package', )))
def new_namespace_root():
    """ create or complete/renew namespace root package. """
    _renew_project(ROOT_PRJ)


@_action(APP_PRJ, MODULE_PRJ, PACKAGE_PRJ, ROOT_PRJ)
def prepare_commit():
    """ run code checks and prepare :data:`COMMIT_MSG_FILE_NAME` for the commit of a single project/package. """
    check_integrity()
    _git_add(INI_PDV)
    _write_commit_message(INI_PDV)
    cae.po("  === commit prepared")


@_action(ROOT_PRJ, arg_names=((ARG_ALL, ), ('portions-sets-expr', ), ('portion-names' + ARG_MULTIPLES, )))
def prepare_portions_commit():
    """ run code checks and prepare :data:`COMMIT_MSG_FILE_NAME` for the commit of portions of a namespace. """
    check_portions_integrity()

    portions_vars = pdv_val(INI_PDV, 'portions_project_vars')
    for package_name in PORTIONS_ARGS:
        por_pdv: PdvType = portions_vars[package_name]
        cae.po(f" ---  {pdv_str(por_pdv, 'portion_name') + '  ---': <18}{pdv_str(por_pdv, 'project_desc')}")
        _git_add(por_pdv)
        _write_commit_message(por_pdv)
    cae.po(f"  === prepared commit of {len(PORTIONS_ARGS)} namespace portions: {PORTIONS_ARGS}")


@_action()
def show_actions():
    """ get info of available/registered/implemented actions of the specified/current project and remote. """
    compact = not cae.get_option('verbose')

    cae.po(f" ---- {pdv_str(INI_PDV, 'project_name')} info:")

    repo_domain = _repo_domain()
    actions = sorted(_available_actions())
    if compact:
        cae.po(f"  --- registered and available actions (locally and on {repo_domain}):")
        cae.po(f"      {' '.join(act.replace('_', '-') for act in actions if _act_callable(act))}")
    else:
        cae.po(f"  --- all registered actions (locally and at {'|'.join(REMOTE_CLASS_NAMES.keys())}):")

        def _act_print(act_reg_key: str):
            if act_reg_key not in REGISTERED_ACTIONS:
                return
            reg = REGISTERED_ACTIONS[act_reg_key]
            cae.po(f"         <{act_reg_key.replace('_', '-')}>:{reg['docstring']}")
            if 'arg_names' in reg:
                cae.po(f"            args: {_expected_args(reg['arg_names'])}")
            cae.po(f"            project types: {', '.join(reg['project_types'])}")
            shortcut = next(sc for sc, act in ACTION_SHORTCUTS.items() if act == act_reg_key)
            if shortcut:
                cae.po(f"            shortcut: {shortcut}")

        for act in actions:
            cae.po(f"      {act.replace('_', '-')} -------------------------------------------------------------------")
            _act_print(act)
            for remote_class in REMOTE_CLASS_NAMES.values():
                _act_print(remote_class + "." + act)

        cae.po(f"  --- actions registered but not available on {repo_domain}:")
        cae.po(f"      {', '.join(_.replace('_', '-') for _ in actions if not _act_callable(_)) or '<none>'}")


@_action()
def show_status(pdv: Optional[PdvType] = None):
    """ show git status of the specified/current project and remote. """
    if pdv is None:
        pdv = INI_PDV

    _print_pdv(pdv)

    cae.po("  --- git diff:")
    cae.po(_git_diff(pdv))

    cae.po("  --- git status:")
    cae.po(_git_status(pdv))


@_action(ROOT_PRJ, arg_names=((ARG_ALL, ), ('portions-sets-expr', ), ('portion-names' + ARG_MULTIPLES, )))
def show_portions_status():
    """ run integrity checks for the specified portions of a namespace. """
    portions_vars = pdv_val(INI_PDV, 'portions_project_vars')
    for package_name in PORTIONS_ARGS:
        por_pdv: PdvType = portions_vars[package_name]
        cae.po(f" ---  {pdv_str(por_pdv, 'portion_name') + '  ---': <18}{pdv_str(por_pdv, 'project_desc')}")
        show_status(por_pdv)


# ----------------------- main ----------------------------------------------------------------------------------------


def main():
    """ main app script """
    cae.add_argument('action', help="action to execute (run `grm -v show-actions` to display all available actions)")
    cae.add_argument('arguments', help="additional arguments, depending on specified action", nargs='*')
    cae.add_option('branch', "branch or version-tag to checkout/filter-/work-on", "")
    cae.add_option('domain', "repository remote host domain of new project (gitlab.com|github.com)", "")
    cae.add_option('gitToken', "personal/private access token to connect to remote host", "", short_opt='t')
    cae.add_option('group', "group or user name of a new project repository at the remote host", "")
    cae.add_option('namespace', "namespace name for new namespace root or portion (module/package) project", "")
    cae.add_option('namespaces', "supported namespaces to register (for templates)", ['ae', 'de'], short_opt='s')
    cae.add_option('package', "package or portion name for a new (namespace) package", "", short_opt='k')
    cae.add_option('path', "project directory of a new (namespace) package (default=current working directory)", "")
    cae.add_option('verbose', "verbose console output", UNSET)
    cae.add_option('version_increment_part', "project version number part to increment (1=mayor, 2=namespace, 3=patch)",
                   3, short_opt='i', choices=range(1, 4))
    for import_name in TPL_PACKAGES:
        cae.add_option(norm_name(import_name.split('.')[-1]) + TPL_VERSION_OPTION_SUFFIX,
                       f"branch/version-tag of {import_name} template package (def=locally installed template)",
                       "",
                       short_opt=UNSET)
    cae.run_app()                                   # parse command line arguments

    _prepare_act_exec()                             # init globals, check if requested action is available/implemented
    _act_callable(ACTION_NAME)()                    # check action arguments and execute action

    if TEMP_CONTEXT:
        TEMP_CONTEXT.cleanup()


if __name__ == '__main__':
    try:
        main()
    except Exception as main_ex:
        debug_info = f":{os.linesep}{format_exc()}" if _debug_or_verbose() else ""
        _exit_error(99, f"****  exception {main_ex} raised on executing the '{ACTION_NAME}' action{debug_info}")

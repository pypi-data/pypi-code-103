"""
friendly.__init__.py
==============================

With the exceptions of the functions that are specific to the console,
this module contains all the functions that are part of the public API.
While Friendly is still considered to be in alpha stage,
we do attempt to avoid creating incompatibility for the functions
here when introducing changes.

The goal is to be even more careful to avoid introducing incompatibilities
when reaching beta stage, and planning to be always backward compatible
starting at version 1.0 -- except possibly for the required minimal
Python version.

Friendly is currently compatible with Python versions 3.6
or newer.

If you find that some additional functionality would be useful to
have as part of the public API, please let us know.
"""
import os
import sys

valid_version = sys.version_info.major >= 3 and sys.version_info.minor >= 6

if not valid_version:  # pragma: no cover
    print("Python 3.6 or newer is required.")
    sys.exit()

del valid_version
__version__ = "0.4.31"


# ===========================================

import inspect
from pathlib import Path

from friendly_traceback import (
    editors_helpers,
    exclude_directory_from_traceback,
    set_stream,
)
from friendly_traceback import explain_traceback as ft_explain_traceback
from friendly_traceback import install as ft_install
from friendly_traceback import set_formatter as ft_set_formatter
from friendly_traceback import set_lang as ft_set_lang
from friendly_traceback.config import session

# The following are not used here, and simply made available directly for convenience
from friendly_traceback import (  # noqa
    exclude_file_from_traceback,
    get_include,
    get_lang,
    get_output,
    get_stream,
    set_include,
)

from .my_gettext import current_lang
from friendly import rich_formatters, theme


exclude_directory_from_traceback(os.path.dirname(__file__))


def install(lang="en", formatter=None, redirect=None, include="explain", _debug=None):
    """
    Replaces ``sys.excepthook`` by friendly's own version.
    Intercepts, and can provide an explanation for all Python exceptions except
    for ``SystemExist`` and ``KeyboardInterrupt``.

    The optional arguments are:

        lang: language to be used for translations. If not available,
              English will be used as a default.

        formatter: if desired, sets a specific formatter to use.

        redirect: stream to be used to send the output.
                  The default is sys.stderr

        include: controls the amount of information displayed.
        See set_include() for details.
    """
    # Note: need "explain" since there is no interaction possible with install
    set_formatter(formatter=formatter)
    ft_install(lang=lang, redirect=redirect, include=include, _debug=_debug)


def explain_traceback(formatter=None, redirect=None):
    """Replaces a standard traceback by a friendlier one, giving more
    information about a given exception than a standard traceback.
    Note that this excludes ``SystemExit`` and ``KeyboardInterrupt``
    which are re-raised.

    If no formatter is specified, the default one will be used.

    By default, the output goes to ``sys.stderr`` or to some other stream
    set to be the default by another API call. However, if::

       redirect = some_stream

    is specified, the output goes to that stream, but without changing
    the global settings.

    If the string ``"capture"`` is given as the value for ``redirect``, the
    output is saved and can be later retrieved by ``get_output()``.
    """
    set_formatter(formatter=formatter)
    ft_explain_traceback(redirect=redirect)


def run(
    filename,
    lang=None,
    include=None,
    args=None,
    console=True,
    formatter=None,
    redirect=None,
    background=None,
    ipython_prompt=True,
):
    """Given a filename (relative or absolute path) ending with the ".py"
    extension, this function uses the
    more complex ``exec_code()`` to run a file.

    If console is set to ``False``, ``run()`` returns an empty dict
    if a ``SyntaxError`` was raised, otherwise returns the dict in
    which the module (``filename``) was executed.

    If console is set to ``True`` (the default), the execution continues
    as an interactive session in a Friendly console, with the module
    dict being used as the locals dict.

    Other arguments include:

    ``lang``: language used; currently only ``'en'`` (default) and ``'fr'``
    are available.

    ``include``: specifies what information is to be included if an
    exception is raised; the default is ``"friendly_tb"`` if console
    is set to ``True``, otherwise it is ``"explain"``

    ``args``: strings tuple that is passed to the program as though it
    was run on the command line as follows::

        python filename.py arg1 arg2 ...

    ``use_rich``: ``False`` by default. Set it to ``True`` if Rich is available
    and the environment supports it.

    ``theme``: Theme to be used with Rich. Currently only ``"dark"``,
    the default, and ``"light"`` are available. ``"light"`` is meant for
    light coloured background and has not been extensively tested.
    """
    _ = current_lang.translate
    if include is None:
        include = "friendly_tb" if console else "explain"
    if args is not None:
        sys.argv = [filename, *list(args)]
    else:
        filename = Path(filename)
        if not filename.is_absolute():
            frame = inspect.stack()[1]
            # This is the file from which run() is called
            run_filename = Path(frame[0].f_code.co_filename)
            run_dir = run_filename.parent.absolute()
            filename = run_dir.joinpath(filename)

        if not filename.exists():
            print(_("The file {filename} does not exist.").format(filename=filename))
            return

    session.install(lang=lang, include=include, redirect=redirect)
    set_lang(lang)
    session.set_formatter(formatter)

    module_globals = editors_helpers.exec_code(
        path=filename, lang=lang, include=include
    )
    if console:  # pragma: no cover
        start_console(
            local_vars=module_globals,
            formatter=formatter,
            banner="",
            include=include,
            background=background,
            ipython_prompt=ipython_prompt,
        )
    else:
        return module_globals


def set_formatter(
    formatter=None, color_system="auto", force_jupyter=None, background=None
):
    """Sets the default formatter. If no argument is given, a default
    formatter is used.
    """
    session.rich_add_vspace = True
    session.use_rich = True
    session.jupyter_button_style = ""
    if formatter in ["dark", "light"]:
        session.console = theme.init_rich_console(
            style=formatter,
            color_system=color_system,
            force_jupyter=force_jupyter,
            background=background,
        )
        set_stream(redirect=rich_formatters.rich_writer)
        formatter = rich_formatters.rich_markdown
    elif formatter == "interactive-dark":
        session.console = theme.init_rich_console(
            style="dark",
            color_system=color_system,
            force_jupyter=force_jupyter,
            background=background,
        )
        formatter = rich_formatters.jupyter_interactive
        session.jupyter_button_style = ";color: white; background-color:black;"
        set_stream()
    elif formatter in ["interactive", "interactive-light"]:
        session.console = theme.init_rich_console(
            style="light",
            color_system=color_system,
            force_jupyter=force_jupyter,
            background=background,
        )
        formatter = rich_formatters.jupyter_interactive
        set_stream()
    else:
        session.use_rich = False
        set_stream()
        theme.disable_rich()
        if formatter == "plain":
            formatter = "repl"
    ft_set_formatter(formatter=formatter)


def start_console(  # pragma: no cover
    local_vars=None,
    formatter=None,
    include="friendly_tb",
    lang="en",
    banner=None,
    background=None,
    displayhook=None,
    ipython_prompt=True,
):
    """Starts a Friendly console."""
    from . import console

    console.start_console(
        local_vars=local_vars,
        formatter=formatter,
        include=include,
        lang=lang,
        banner=banner,
        background=background,
        displayhook=displayhook,
        ipython_prompt=ipython_prompt,
    )


def set_lang(lang):
    ft_set_lang(lang)
    current_lang.install(lang)

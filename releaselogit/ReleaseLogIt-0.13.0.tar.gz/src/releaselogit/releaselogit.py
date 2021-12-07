"""Manage release notes for Python projects.

ReleaseIt keeps release notes for Python projects in a dict structure.
It aims to standardise, facilitate and automate the management of
release notes when publishing a project to GitHub, PyPI and
ReadTheDocs.  It is developed as part of the PackageIt project, but can
be used independently as well.

See also https://pypi.org/project/PackageIt/
"""

import logging
from pathlib import Path
import tempfile
import toml
from beetools.beearchiver import Archiver

_PROJ_DESC = __doc__.split("\n")[0]
_PROJ_PATH = Path(__file__)
_PROJ_NAME = _PROJ_PATH.stem
_PROJ_VERSION = "0.0.3"

_TOML_CONTENTS_DEF = """
[0.0.0]
Title = 'Creation of the project'
Description = ['List all the changes to the project here.',
               'Changes listed here will be in the release notes under the above heading.']
"""


class ReleaseLogIt:
    """ReleaseIt manages release notes for Python projects."""

    def __init__(self, p_src, p_parent_log_name="", p_verbose=True):
        """Initialize the class

        Parameters
        ----------
        p_src : Path
            Directory path where the release notes are or will be created in.
        p_parent_log_name : str, default = ''
            Name of the parent.  In combination witt he class name it will
            form the logger name.
        p_verbose: bool, default = True
            Write messages to the console.

        Examples
        --------
        >>> import tempfile
        >>> from pathlib import Path
        >>> t_releaseit = ReleaseLogIt(Path(tempfile.mkdtemp(prefix=_PROJ_NAME)))
        >>> t_releaseit.rel_list
        [['0', '0', '0']]
        """
        self.success = True
        if p_parent_log_name:
            self._log_name = "{}.{}".format(p_parent_log_name, _PROJ_NAME)
            self.logger = logging.getLogger(self._log_name)
        self.verbose = p_verbose

        self.src_pth = Path(p_src, "release.toml")
        if not self.src_pth.exists():
            self._create_def_config()
        self.rel_notes = {}
        rel_notes = toml.load(self.src_pth)
        self.rel_list = []
        self.cur_pos = -1
        self.rel_cntr = 0
        if self._validate_release_log(rel_notes):
            self.rel_notes = rel_notes
            self._get_release_list()
            self._sort()
            self.cur_pos = 0
            self.rel_cntr = len(self.rel_list)
        pass

    def __iter__(self):
        self.cur_pos = 0
        return self

    def __next__(self):
        if self.cur_pos < self.rel_cntr:
            element = self.rel_notes[self.rel_list[self.cur_pos][0]][
                self.rel_list[self.cur_pos][1]
            ][self.rel_list[self.cur_pos][2]]
            self.cur_pos += 1
            return element
        else:
            raise StopIteration

    def __repr__(self):
        return f"""ReleaseLogIt({self.cur_pos},"{'.'.join(self.rel_list[self.cur_pos])}")"""

    def __str__(self):
        return f"""{'.'.join(self.rel_list[self.cur_pos])}"""

    def add_release_note(self, p_release_note):
        if self._check_release_note(p_release_note):
            major = list(p_release_note.keys())[0]
            minor = list(p_release_note[major].keys())[0]
            patch = list(p_release_note[major][minor].keys())[0]
            if major in self.rel_notes.keys():
                if minor in self.rel_notes[major].keys():
                    if patch not in self.rel_notes[major][minor].keys():
                        self.rel_notes[major][minor][patch] = p_release_note[major][
                            minor
                        ][patch]
                    else:
                        return False
                else:
                    self.rel_notes[major][minor] = p_release_note[major][minor]
            else:
                self.rel_notes[major] = p_release_note[major]

            self.rel_list.append([major, minor, patch])
            self._sort()
            self.rel_cntr = len(self.rel_list)
        return True

    def _create_def_config(self):
        """Create the "release.toml" configuration file.

        Create the "release.toml" configuration file with the default
        contents as if it is the first release (0.0.1).  If the file
        already exists, it will be overwritten.
        This method is called during instantiation of the class.

        Parameters
        ----------

        Returns
        -------
        release_pth : Path
            Path to the "release.toml" file.
        """
        self.src_pth.write_text(_TOML_CONTENTS_DEF)
        return self.src_pth

    def _get_release_list(self):
        for major in self.rel_notes:
            for minor in self.rel_notes[major]:
                for patch in self.rel_notes[major][minor]:
                    self.rel_list.append([major, minor, patch])
        return self.rel_list

    def get_release_note_by_title(self, p_title):
        for rel in self.rel_list:
            if self.rel_notes[rel[0]][rel[1]][rel[2]]["Title"] == p_title:
                return self.rel_notes[rel[0]][rel[1]][rel[2]]
        return None

    def get_release_note_by_version(self, p_version):
        parts = p_version.split(".")
        if parts in self.rel_list:
            return self.rel_notes[parts[0]][parts[1]][parts[2]]
        return None

    def get_release_titles(self):
        titles = []
        for rel in self.rel_list:
            titles.append(self.rel_notes[rel[0]][rel[1]][rel[2]]["Title"])
        return titles

    def has_title(self, p_title):
        for seq in self.rel_list:
            if self.rel_notes[seq[0]][seq[1]][seq[2]]["Title"] == p_title:
                return True
        return False

    def latest(self):
        return self.rel_notes[self.rel_list[-1][0]][self.rel_list[-1][1]][
            self.rel_list[-1][2]
        ]

    def oldest(self):
        return self.rel_notes[self.rel_list[0][0]][self.rel_list[0][1]][
            self.rel_list[0][2]
        ]

    def _sort(self):
        self.rel_list = sorted(
            self.rel_list, key=lambda release_notes: release_notes[2]
        )
        self.rel_list = sorted(
            self.rel_list, key=lambda release_notes: release_notes[1]
        )
        self.rel_list = sorted(
            self.rel_list, key=lambda release_notes: release_notes[0]
        )
        return self.rel_list

    def _check_release_note(self, p_release_note):
        major = p_release_note.keys()
        if len(major) == 1:
            major = list(major)[0]
            if isinstance(major, str) and major.isnumeric():
                minor = p_release_note[major].keys()
                if len(minor) == 1:
                    minor = list(minor)[0]
                    if isinstance(minor, str) and minor.isnumeric():
                        patch = p_release_note[major][minor].keys()
                        if len(patch) == 1:
                            patch = list(patch)[0]
                            if isinstance(patch, str) and patch.isnumeric():
                                release_note_contents = p_release_note[major][minor][
                                    patch
                                ]
                                if "Description" not in release_note_contents.keys():
                                    return False
                                if not isinstance(
                                    release_note_contents["Description"], list
                                ):
                                    return False
                                if len(release_note_contents["Description"]) <= 0:
                                    return False
                                for desc in release_note_contents["Description"]:
                                    if not isinstance(desc, str):
                                        return False
                                if "Title" not in release_note_contents.keys():
                                    return False
                                if self.has_title(release_note_contents["Title"]):
                                    return False
                                return True
        return False

    def _validate_release_log(self, p_release_notes):
        for major in p_release_notes:
            for minor in p_release_notes[major]:
                for patch in p_release_notes[major][minor]:
                    release = {
                        major: {minor: {patch: p_release_notes[major][minor][patch]}}
                    }
                    if not self._check_release_note(release):
                        return False
        return True

    def write_toml(self):
        self.src_pth.write_text(toml.dumps(self.rel_notes))
        pass


def do_examples(p_cls=True):
    """A collection of implementation examples for ReleaseIt.

    A collection of implementation examples for ReleaseIt. The examples
    illustrate in a practical manner how to use the methods.  Each example
    show a different concept or implementation.

    Parameters
    ----------
    p_cls : bool, default = True
        Clear the screen or not at startup of Archiver

    Returns
    -------
    success : boolean
        Execution status of the method

    """
    b_tls = Archiver(_PROJ_DESC, _PROJ_PATH)
    b_tls.print_header(p_cls)
    success = do_example1()
    b_tls.print_footer()
    return success


def do_example1(p_cls=True):
    """A working example of the implementation of ReleaseIt.

    Example1 illustrate the following concepts:
    1. Creates to object
    2. Create a default 'release.toml' file in teh designated (temp) directory

    Parameters
    ----------
    p_cls : bool, default = True
        Clear the screen or not at startup of Archiver

    Returns
    -------
    success : boolean
        Execution status of the method

    """
    success = True
    releaseit = ReleaseLogIt(Path(tempfile.mkdtemp(prefix=_PROJ_NAME)))
    print(releaseit.src_pth)
    print(releaseit.rel_notes)
    return success


if __name__ == "__main__":
    do_examples()

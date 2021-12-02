"""This module defines classes to access and store recorded EMA data,
and methods and functions to read and write such data.
Data may (*in the future*) be stored in various file formats,
for now only Excel files can be used.

Each EMA Record is a list of nominal and ordinal elements, defining
* a subject ID label,
* a single SCENARIO specified by selected categories in one or more Scenario Dimension(s),
* ordinal RATING(s) for zero, one, or more perceptual ATTRIBUTE(s) in the current scenario.

*** Class Overview:

EmaFrame: defines layout and category labels of data in each EMA Record.
    Some properties of an EmaFrame instance can define selection criteria
    for a subset of data to be included for analysis.

EmaDataSet: all data to be used as input for statistical analysis.

*** Input File Formats:

* xlsx: Data can (for now) be imported ONLY from Excel workbook (xlsx) files,
with response data stored in designated columns of one or more worksheets.
Files in this format must be saved with extension '.xlsx'.

(Other data file formats may be allowed in future versions.)

*** Input Data Files:

All input files from an experiment must be stored in one directory tree.

If results are to be analyzed for more than one group of test subjects,
the data for each group must be stored in separate sub-directories
within the specified top directory.

Groups are identified by a tuple of grouping pairs (group_factor, group_category), where
group_factor is a grouping dimension, e.g., 'Age', or 'Gender', and
group_category is a nominal label within the factor, e.g., 'old', or 'female'.

A sequence of one element from each grouping pair must define a unique path
to files including data for subjects in ONE group.

File names are arbitrary, although they may be somehow associated with
the encoded name of the participant, to facilitate data organisation.

Each data file in ONE group directory may contain count profiles
from several subjects in this group.
Each subject in the same group must have a unique subject ID.

Different files in the same sub-directory
may include data for the same subject in the group,
e.g., results obtained in different test stages,
or simply for replicated EMA responses from the same subject.

Subjects in different groups may have the same subject ID values,
because the groups are separated anyway,
but normally the subject IDs would be unique across all groups.

*** Example Directory Tree:

Assume we have data files in the following directory structure:
~/ema_study / old_subjects / male, containing files Data_EMA_64.xlsx and Response_Data_LAB_64.xlsx
~/ema_study / old / female_subjects, containing files Subjects_EMA_64.xlsx and Data_EMA_65.xlsx
~/ema_study / young / male,  containing files EMA_64.xlsx and EMA_65.xlsx
~/ema_study / young / female, containing files EMA_64.xlsx and EMA_65.xlsx

Four separate groups may then be defined by factors Age and Gender,
and the analysis may be restricted to data in files with names including 'EMA_64'.


*** Accessing Input Data för Analysis:
*1: Create an EmaFrame object defining the experimental layout, e.g., as:

emf = EmaFrame(scenarios={'CoSS': [f'{i}.' for i in range(1, 8)],
                          'Important': ('Slightly', 'Medium', 'Very'),
                          },  # nominal variables
               attribute_grades={'Speech': ('Very Hard', 'Fairly Hard', 'Fairly Easy','Very Easy')},
        )
NOTE: Letter CASE is always distinctive, i.e., 'Male' and 'male' denote different categories.

*2: Load all test results into an EmaDataSet object:

ds = EmaDataSet.load(emf, path='~/ema_study',
                    grouping={'Age': ('young', 'old'),
                              'Gender': ('female', 'male'),
                              'Test': ('EMA_64',)}
                    fmt='xlsx',
                    subject='sheet',    # xlsx sheet title is subject ID
                    ema_vars={'CoSS': 'B',       # column B contains Scenario 'CoSS' category
                              'Important': 'C',  # column C contains Scenario 'Important' category
                              'Speech': 'D'     # column D contains 'Speech' ordinal rating
                              }
                    )

The loaded data structure ds can then be used as input for analysis.

The parameter emf is a EmaFrame object that defines the variables to be analyzed.

*** Selecting Subsets of Data for Analysis:
It is possible to define a data set including only a subset of recorded data.

For example, assume we want to analyze only two groups, old males, and old females.
and only responses for Scenario dimension 'CoSS'.
Then we must define a new EmaFrame object, and load only a subset of group data:

emf = EmaFrame(scenarios={'CoSS': [f'{i}.' for i in range(1, 8)],
                          },  # nominal variables
               attribute_grades={'Speech': ('Very Hard', 'Fairly Hard', 'Fairly Easy','Very Easy')},
        )
ds = EmaDataSet.load(emf, path='~/ema_study',
                    grouping={'Age': ('old',),
                              'Gender': ('female', 'male'),
                              'Test': ('EMA_64',)}
                    fmt='xlsx',
                    subject='sheet',    # xlsx sheet title is subject ID
                    ema_vars={'CoSS': 'B',       # column B contains Scenario 'CoSS' category
                              'Speech': 'D'     # column D contains 'Speech' ordinal rating
                              }
                    )

*** Version History:
* Version 0.5.1:
2021-11-26, EmaDataSet.load warning for input argument problems

* Version 0.5:
2021-10-15, first functional version
2021-11-18, grouping moved from EmaFrame -> EmaDataSet.load
2021-11-20, EmaDataSet.ensure_complete
2021-11-23, Group dir name MUST include both (g_factor, g_cat), e.g., 'Age_old'
2021-11-xx, allow empty scenarios or empty attribute_grades ***************** ???
"""
# ******** Allow (('Age', 'old'), ('Gender', 'female'),... ) for load group sequence
# ******** use EmaDataSet.groups keys like dir_names, i.e., ('Age_old', 'Gender_female',...) ???
# ******** -> easier to save in dir tree

import numpy as np
from pathlib import Path
from itertools import product
# import json
import logging

from EmaCalc import ema_file_xlsx

FILE_CLASS = {'xlsx': ema_file_xlsx.EmaFile,
              }
# = mapping of file format suffix to file reader module, only ONE format for now...

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


# ------------------------------------------------------------------
class EmaFrame:
    """Defines structure of EMA recorded dataset for one analysis.
    """
    def __init__(self,
                 scenarios=None,
                 stage_key='Stage',  # default scenario key for test stage
                 attribute_grades=None,
                 ):
        """
        :param scenarios: (optional) dict or iterable with elements (scene_factor, category_list), where
            scene_factor is a string label identifying one scenario "dimension",
            category_list is a list of labels for NOMINAL categories within this scene_factor.
        :param attribute_grades: (optional) dict or iterable with elements (attribute, response_list),
            attribute is string id of a rated perceptual attribute,
            response_list is an iterable with ORDINAL categories, strings or numeric
        :param stage_key: (optional) string key, MUST be member of scenarios.keys()
            scenarios[stage_key] = list of test stages (e.g., before vs after treatment),
                specified by experimenter, i.e., NOT given as an EMA response

        NOTE: scenarios, attribute_grades, grouping may define a subset of
            data in input data files, if not all variant are to be analyzed.

            Category label strings may be shorter than those occurring in data files,
            and will be considered matching if they agree within the given length.
        """
        self.stage_key = stage_key
        if scenarios is None:
            scenarios = dict()
        else:
            scenarios = dict(scenarios)
        # ensure first scenario key == self.stage_key:
        # **** requires python >= 3.9
        stage_dict = {self.stage_key: scenarios.pop(self.stage_key, (None,))}
        self.scenarios = stage_dict | scenarios

        if attribute_grades is None:
            self.attribute_grades = dict()
        else:
            self.attribute_grades = dict(attribute_grades)

    def __repr__(self):
        return (self.__class__.__name__ + '(\n\t\t' +
                ',\n\t\t'.join(f'{key}={repr(v)}'
                               for (key, v) in vars(self).items()) +
                '\n\t\t)')

    @property
    def scenario_shape(self):
        """tuple with number of nominal categories for each scenario factor"""
        return tuple(len(sc_list)
                     for sc_list in self.scenarios.values())

    @property
    def n_scenarios(self):  # **** needed ?
        return np.prod(self.scenario_shape, dtype=int)

    def scenario_axes(self, sc):
        """
        :param sc: sequence of one or more scenario keys
        :return: tuple of corresponding numerical axes
        """
        sc_keys = list(self.scenarios.keys())
        sc_ind = []
        for sc_i in sc:
            try:
                sc_ind.append(sc_keys.index(sc_i))
            except ValueError:
                logger.warning(f'{repr(sc_i)} is not a scenario key')
        return sc_ind

    @property
    def rating_shape(self):
        """tuple with number of ordinal response levels, for each attribute
        """
        return tuple(len(r_list)
                     for r_list in self.attribute_grades.values())

    @property
    def n_stages(self):
        # == scenario_shape[0]
        return len(self.scenarios[self.stage_key])

    def accept(self, ema):
        """Check that ema_record includes acceptable values
         for all variables required in self
        :param ema: dict with elements (key, value) from observed EMA record
        :return: boolean = True if acceptable
        """
        try:
            scenario_ok = all(0 <= _index_matching(sc_list, ema[sc_key])
                              for (sc_key, sc_list) in self.scenarios.items())
            rating_ok = all(0 <= _index_matching(r_list, ema[r_key])
                            for (r_key, r_list) in self.attribute_grades.items())
            return scenario_ok and rating_ok
        except (KeyError, ValueError):
            return False

    def scenario_index(self, r):
        """Encode an EMA record into an index tuple identifying the scenario
        :param r: dict with (key, value) pairs of scenarios and attribute_grades
        :return: sc_i = tuple (k_0, k_1, k_2, ...), where
            k_0 = test-stage index,
            k_i = index of i-th scenario
            len(sc_i) == len(self.scenarios)
        """
        try:
            return tuple(_index_matching(sc_list, r[sc_key])
                         for (sc_key, sc_list) in self.scenarios.items())
        except (KeyError, ValueError):
            return None

    def rating_index(self, r):
        """Encode an EMA record into an index tuple identifying
        rating responses
        :param r: dict with (key, value) pairs of scenarios and attribute_grades
        :return: y = tuple, with
            y[i] = scalar integer = ordinal value of i-th rating response
            y[i] = None, if response is missing
            len(y) == len(self.attribute_grades)
        """
        try:
            return tuple(_index_matching(r_list, r[r_key])
                         for (r_key, r_list) in self.attribute_grades.items())
        except (KeyError, ValueError):
            return None


# ------------------------------------------------------------
class EmaDataSet:
    """All data input for one complete EMA analysis.
    """
    def __init__(self, emf, groups):
        """
        :param emf: an EmaFrame instance
        :param groups: dict with elements (group_id: group_dict), where
            group_id = tuple with one or more pairs (g_factor, g_category),
                identifying the sub-population,
            group_dict = dict with elements (subject, ema_list), where
            ema_list = list with elements ema, where
                ema = tuple with elements (key, value), where
                key is one of [stage_key, scene_factor, attribute],
                value is one allowed category for this key.
                len(ema) = emf.n_variables
        """
        self.emf = emf
        self.groups = groups

    def __repr__(self):
        def sum_n_records(g_subjects):
            """Total number of EMA records across all subjects in group"""
            return sum(len(s_ema) for s_ema in g_subjects.values())
        # ---------------------------------------------------------------
        return (self.__class__.__name__ + '(\n\t'
                + f'emf= {self.emf},\n\t'
                + 'groups= {' + '\n\t\t'
                + '\n\t\t'.join((f'{g}: {len(g_subjects)} subjects '
                                 + f'with {sum_n_records(g_subjects)} EMA records in total,')
                                for (g, g_subjects) in self.groups.items())
                + '\n\t\t})')

    @classmethod
    def load(cls, emf, path,
             subject,
             ema_vars,
             grouping=None,
             fmt='xlsx'):
        """Create one class instance with selected data from input files.
        :param emf: EmaFrame instance
        :param path: string or Path defining top of directory tree with all data files
        :param subject: string to identify subject in specific file object,
        :param ema_vars: dict with args to specific file object,
            typically with elements (ema_key, column_address)
        :param grouping: (optional) dict or iterable with elements (group_dim, category_list),
            where
            group_dim is a string label identifying one "dimension" of sub-populations,
            category_list is a list of labels for allowed categories within group_factor.
            May be left empty, if only one (unnamed) group is included.
        :param fmt: (optional) string with file suffix for data files.
            If undefined, all files are tried, so mixed file formats can be used as input.
        :return: a single cls object
        """
        assert (fmt in FILE_CLASS.keys() or
                fmt in ['', None]), 'Unknown file format: ' + fmt
        # check that ema_vars.keys() are either Scenario or Attribute keys:
        emf_keys = set(emf.scenarios.keys()) | set(emf.attribute_grades.keys())
        ema_keys = set(ema_vars.keys())
        missing_emf = emf_keys - ema_keys
        if len(missing_emf) > 0:
            logger.warning(f'No file address defined for {missing_emf}')
        missing_ema = ema_keys - emf_keys
        if len(missing_ema) > 0:
            logger.warning(f'File address(es) {missing_ema} defined, but not needed.')
        path = Path(path)
        if grouping is None:
            grouping = {'': ('',)}  # ONE unnamed group Use None ??? *******'
        else:
            grouping = dict(grouping)
        # groups = {g: dict() for g in emf.groups}
        groups = {g: dict() for g in _groups(grouping)}
        # = empty dict for subjects in each group
        # for (g, g_path) in _gen_group_file_paths(path, fmt, [*emf.grouping.items()]):
        for (g, g_path) in _gen_group_file_paths(path, fmt, [*grouping.items()]):
            logger.info(f'Reading {g_path}')
            ema_file = FILE_CLASS[fmt](g_path,
                                       subject=subject,
                                       ema_vars=ema_vars)
            for r in ema_file:
                # add stage if only one allowed and not specified
                if emf.n_stages == 1 and emf.stage_key not in r.ema.keys():
                    r.ema[emf.stage_key] = emf.scenarios[emf.stage_key][0]
                if emf.accept(r.ema):
                    if r.subject not in groups[g]:
                        groups[g][r.subject] = []
                        # = initialized empty ema list for this new subject
                    groups[g][r.subject].append(r.ema)
                else:
                    logger.debug(f'Not Used: Subject {r.subject}: {r.ema}')
        return cls(emf, groups)

    # def add method, to include data from new files with different layout ???
    # ******* make symmetric use of file_args in load and save methods ***************

    def save(self, dir, subject, ema_vars, allow_over_write=False, fmt='xlsx'):
        """Save self.groups in a directory tree with one folder for each group,
        with one file for each subject.
        :param dir: Path or string defining the top directory where files are saved
        :param allow_over_write: boolean switch, over-write files if True
        :param fmt: string label specifying file format
        :param subject: string to identify subject in specific file object,
        :param ema_vars: dict with args to specific file object,
            typically with elements (ema_key, column_address)
        :return: None
        """
        for key in self.emf.scenarios.keys():
            if key not in ema_vars.keys():
                logger.warning('No column address for Scenario ' + repr(key) + ': Not saved!')
        for key in self.emf.attribute_grades.keys():
            if key not in ema_vars.keys():
                logger.warning('No column address for Attribute ' + repr(key) + ': Not saved!')
        dir = Path(dir)
        for (g, group_data) in self.groups.items():
            g = _dir_name(g, '/')
            if len(g) == 0:
                g_path = dir
            else:
                g_path = dir / g
            g_path.mkdir(parents=True, exist_ok=True)
            for (s_id, s_items) in group_data.items():
                try:
                    p = (g_path / s_id).with_suffix('.' + fmt)  # one file per subject
                    s_file = FILE_CLASS[fmt](file_path=p,
                                             subject=subject,
                                             ema_vars=ema_vars)
                    s_file.save(subject=s_id, items=s_items,
                                allow_over_write=allow_over_write)
                except (KeyError, NotImplementedError):
                    raise RuntimeError(f'Cannot save {self.__class__.__name__} in {repr(fmt)} format')

    def ensure_complete(self):
        """Check that we have at least one subject in every sub-population category,
        with at least one ema record for each subject (already checked in load method).
        :return: None

        Result:
        self.groups may be reduced:
        subjects with no records are deleted,
        groups with no subjects are deleted
        logger warnings for missing data.
        """
        for (g, g_subjects) in self.groups.items():
            incomplete_subjects = set(s for (s, s_ema) in g_subjects.items()
                                     if len(s_ema) == 0)
            for s in incomplete_subjects:
                logger.warning(f'No EMA data for subject {repr(s)} in group {repr(g)}. Deleted!')
                del g_subjects[s]
        incomplete_groups = set(g for (g, g_subjects) in self.groups.items()
                                if len(g_subjects) == 0)
        for g in incomplete_groups:
            logger.warning(f'No subjects in group {repr(g)}. Deleted!')
            del self.groups[g]
        if len(self.groups) == 0:
            raise RuntimeError('No remaining EMA data in any group.')


# -------------------------------------------- module help functions

def _dir_name(g, sep='_'):
    """make sure group name is a possible directory name
    :param g: string or tuple of strings
    :return: string to be used as directory
    """
    if type(g) is tuple:  # one or more (g_factor, g_cat) tuples
        g = sep.join(_dir_name(g_s, sep='_')
                     for g_s in g)
    return g


def _groups(group_factors):
    """
    :param group_factors: dict or iterable with elements (group_factor, category_list),
    :return: generator of all combinations of (gf, gf_category) pairs from each group factor
        Generated pairs are sorted like self.grouping
    """
    return product(*(product([gf], gf_cats)
                     for (gf, gf_cats) in group_factors.items())
                   )


def _gen_group_file_paths(path, fmt, group_factors, g_tuple=()):
    """generator of group keys and corresponding file Paths, recursively, for all groups
    :param path: Path instance defining top directory to be searched
    :param fmt: file suffix of desired files
    :param group_factors: list of tuples (g_factor, labels) as in CountProfileFrame
    :param g_tuple: list of tuples (g_factor, factor_label),
        defining a combined group label or a beginning of a complete such label
    :return: generator of tuples (group_key, file_path), where
        group_key is an element of emf.groups,
        file_path is a Path object to a file that may hold count data for the group.
    """
    for f in path.iterdir():
        if len(group_factors) == 0:
            if f.is_file() and fmt in f.suffix:
                # print(f'Reading file {f}')
                yield g_tuple, f
        else:  # len(grouping) >=1
            g_factor_key = group_factors[0][0]
            for g_cat in group_factors[0][1]:
                factor_cat = (g_factor_key, g_cat)
                # = new tuple to be included in final group label
                if f.is_dir():
                    # if f.name.find(g_cat) == 0:
                    if (f.name.find(g_factor_key) == 0
                            and f.name.find(g_cat) == len(g_factor_key) + 1):
                        # iterate recursively in sub-directory
                        yield from _gen_group_file_paths(f, fmt,
                                                         group_factors[1:],
                                                         (*g_tuple, factor_cat))
                elif f.is_file() and len(group_factors) == 1:
                    # at final sub-directory level, also accept group category in file name:
                    if (g_factor_key in f.name) and (g_cat in f.name) and fmt in f.suffix:
                        # print(f'Reading file {f}')
                        yield (*g_tuple, factor_cat), f


def _index_matching(category_list, label):
    """Like list.index, but allowing sub-string match
    :param category_list: list of string-valued labels
    :param label: a single label
    :return: index in str_list of element matching initial part of label
    """
    for (i, c_label) in enumerate(category_list):
        if label == c_label:
            return i
        elif label.find(c_label) == 0:
            return i
    raise ValueError('Label not matched')


# -------------------------------------------- TEST:
if __name__ == '__main__':
    # work_dir = Path('../..').resolve()
    home_dir = Path.home()
    work_dir = home_dir / 'Documents' / 'PythonTools' / 'EmaCalc_test'

    # = ORCA profile
    data_dir = work_dir / 'ORCA fake groups'
    print(f'*** Testing _gen_group_file_paths in {data_dir}')

    emf = EmaFrame(scenarios={'CoSS': [f'{i}.' for i in range(1, 8)],
                              'Viktigt': ['Lite / inte alls viktigt',
                                          'Ganska viktigt',
                                          'Mycket viktigt'],
                              # 'Test': (None, None),
                              },  # nominal variables
                   attribute_grades={'Speech': ['Mycket svårt',
                                                'Ganska svårt',
                                                'Lite / inte alls svårt']},  # ordinal variables
                   )
    print('emf=\n', emf)

    group_factors = {'Age': ['young', 'old'],
                     'Gender': ['male', 'female'],
                     'ORCA': ['AR_64']}
    # for (g, g_path) in _gen_group_file_paths(data_dir, 'xlsx', [*emf.grouping.items()]):
    for (g, g_path) in _gen_group_file_paths(data_dir, 'xlsx', [*group_factors.items()]):
        print('g= ', g, ': g_path= ', g_path)

    ds = EmaDataSet.load(emf, data_dir,
                         grouping=group_factors,
                         subject='A',
                         ema_vars={'CoSS': 'J',
                                   'Speech': 'P',
                                   'Viktigt': 'O'
                                   }
                         )
    print('ds= ', ds)

    # ***** TEST Empty scenarios or Empty attribute_grades *************'

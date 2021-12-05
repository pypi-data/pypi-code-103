#!/usr/bin/env python3

r"""
** Raisin: To perform cluster work easily! **
---------------------------------------------

The main aim of project *raisin* is to **share physical resources** of your laptop
with a community.
In counterpart, you can **benefit from the community resources**.

Notes
-----
* To generate the documentation, you have to install the package *pdoc3* with *pip* for example.
    Then, you just have to type the following command to generate the html files:
    * ``pdoc3 raisin/ -c latex_math=True --force --html``
* To run the test benches, you have to install the package *pytest* with *pip* for example.
    Then you have to type the following command:
    * ``clear && pytest --doctest-modules raisin/
        && find raisin/ -regex '.*test.*\.py' -exec pytest {} \;``
* Docstrings respect the following convention:
    * ``https://numpydoc.readthedocs.io/en/latest/format.html``
* For text formatting:
    * ``black -C -S -l 100 raisin``
"""

import inspect

from raisin.serialization import deserialize, dump, dumps, load, loads, serialize


__version__ = '3.0.0'
__author__ = 'Robin RICHARD (robinechuca) <raisin@ecomail.fr>'
__license__ = 'GNU Affero General Public License v3 or later (AGPLv3+)'
__all__ = ['deserialize', 'dump', 'dumps', 'load', 'loads', 'serialize']
__pdoc__ = {
    obj: 'Alias to ``raisin.{}.{}``'.format(
        (inspect.getsourcefile(globals()[obj]).split('raisin/')[-1][:-3])
        .replace('/', '.')
        .replace('.__init__', ''),
        obj,
    )
    for obj in __all__
}
__pdoc__ = {
    **__pdoc__,
    **{
        f'{cl}.{meth}': False
        for cl in __all__
        if globals()[cl].__class__.__name__ == 'type'
        for meth in globals()[cl].__dict__
        if not meth.startswith('_')
    },
}

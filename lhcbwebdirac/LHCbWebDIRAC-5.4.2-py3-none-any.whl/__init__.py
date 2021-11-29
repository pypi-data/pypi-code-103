###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import six

if six.PY2:
    from pkgutil import extend_path

    __path__ = extend_path(__path__, __name__)


# Define Version
if six.PY3:
    from pkg_resources import get_distribution, DistributionNotFound

    try:
        __version__ = get_distribution(__name__).version
        version = __version__
    except DistributionNotFound:
        # package is not installed
        version = "Unknown"
else:
    majorVersion = 5
    minorVersion = 3
    patchLevel = 1
    preVersion = 0

    version = "v%sr%s" % (majorVersion, minorVersion)
    buildVersion = "v%dr%d" % (majorVersion, minorVersion)
    if patchLevel:
        version = "%sp%s" % (version, patchLevel)
        buildVersion = "%s build %s" % (buildVersion, patchLevel)
    if preVersion:
        version = "%s-pre%s" % (version, preVersion)
        buildVersion = "%s pre %s" % (buildVersion, preVersion)


def extension_metadata():
    import importlib.resources  # pylint: disable=import-error,no-name-in-module

    return {
        "priority": 60,
        "web_resources": {
            "static": [importlib.resources.files("LHCbWebDIRAC") / "WebApp" / "static"],  # pylint: disable=no-member
        },
    }

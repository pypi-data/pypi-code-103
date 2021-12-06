# ios.diff
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



"""Cisco IOS configuration differences module.

This module compares two configurations for Cisco IOS devices and
produces a delta configuration.
"""



# --- imports ---



import sys

from .converters import converters
from ..diff import DiffConfig, pathstr
from .utils import explain_diffs



# --- context parser ---



class CiscoIOSDiffConfig(DiffConfig):
    """This class is used to compare two IOS configuration files and
    generate a configuration file to transform one into the other.
    """


    def _add_converters(self):
        "This method adds the converters for Cisco IOS."

        for cvt_class in converters:
            try:
                self._add_converter(cvt_class())
            except:
                print("with: cvt_class=" + repr(cvt_class),
                      file=sys.stderr)

                raise


    def _explain_comment(self, path):
        """This method overrides the empty inherited one to return a
        Cisco IOS comment giving the matched path.
        """

        return "! => " + pathstr(path)


    def _diffs_end(self):
        """This method overrides the empty inherited one to return a
        single line saying 'end'.
        """

        return ["end"]


    def init_rules_tree(self):
        """This method extends the inherited one to add some rules to
        the tree for the default CoPP (Control Plane Policing) IPv4
        extended and IPv6 ACLs.
        """

        super().init_rules_tree()

        self._rules_tree.update( {
            "ios-default": {
                "ip-access-list-extended": {
                    "acl-copp-match-igmp": {},
                    "acl-copp-match-pim-data": {},
                },
                "ipv6-access-list": {
                    "acl-copp-match-mld": {},
                    "acl-copp-match-ndv6": {},
                    "acl-copp-match-ndv6hl": {},
                    "acl-copp-match-pimv6-data": {},
                },
            },
        } )


    def init_rules_active(self):
        """This method extends the inherited one to add in some active
        rules to exclude the portions of the rules tree set up in
        init_rules_tree().
        """

        super().init_rules_active()

        self._rules_active.append( (False, ("ios-default", ) ) )

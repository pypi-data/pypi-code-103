# ios.diff
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



"""Cisco IOS configuration differences module.

This module compares two configurations for Cisco IOS devices and
produces a delta configuration.
"""



# --- imports ---



import re
import sys

import netaddr

from net_contextdiff.diff import DiffConvert, DiffConfig, pathstr
from .utils import is_int_physical, explain_diffs



# --- converter classes ---



# _cvts = []
#
# This is a list of converter classes to be added to the
# CiscoIOSConfigDiff object by the _add_converters() method.  Each
# class will be instantiated and added.

_cvts = []



# SYSTEM



class _Cvt_Hostname(DiffConvert):
    cmd = "hostname",

    def remove(self, old):
        return "no hostname"

    def update(self, old, upd, new):
        return "hostname " + upd

_cvts.append(_Cvt_Hostname)



# INTERFACE ...



class _Cvt_Int(DiffConvert):
    cmd = "interface", None

    def remove(self, old, int_name):
        # only remove the interface if it's not physical
        if is_int_physical(int_name):
            return

        return "no interface " + int_name

    def add(self, new, int_name):
        return "interface " + int_name

_cvts.append(_Cvt_Int)


class _CvtContext_Int(DiffConvert):
    "Abstract class for interface context converters to subclass."
    context = "interface", None


# we put the 'interface / shutdown' at the start to shut it down before
# we do any [re]configuration

class _Cvt_Int_Shutdown(_CvtContext_Int):
    cmd = "shutdown",
    name = "shutdown"

    def update(self, old, upd, new, int_name):
        return ("interface " + int_name,
                " " + ("" if upd else "no " ) + "shutdown")

_cvts.append(_Cvt_Int_Shutdown)


# we do VRF changes on an interface before we do any IP configuration,
# otherwise it will be removed

class _Cvt_Int_VRFFwd(_CvtContext_Int):
    cmd = "vrf-forwarding",

    def remove(self, old, int_name):
        return "interface " + int_name, " no vrf forwarding"

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " vrf forwarding " + upd
        # TODO: need to find some way to trigger reapplication of IP
        # information (address, HSRP, etc.)

_cvts.append(_Cvt_Int_VRFFwd)


class _Cvt_Int_ARPTime(_CvtContext_Int):
    cmd = "arp-timeout",

    def remove(self, old, int_name):
        return "interface " + int_name, " no arp timeout"

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " arp timeout %d" % upd

_cvts.append(_Cvt_Int_ARPTime)


class _Cvt_Int_CDPEna(_CvtContext_Int):
    cmd = "cdp-enable",

    def remove(self, old, int_name):
        # if the 'cdp enable' option is not present, that doesn't mean
        # it's disabled but just that it's not specified, so we assume
        # the default is for it to be enabled
        return "interface " + int_name, " cdp enable"

    def update(self, old, upd, new, int_name):
        return ("interface " + int_name,
                " " + ("" if upd else "no ") + "cdp enable")

_cvts.append(_Cvt_Int_CDPEna)


class _Cvt_Int_ChnGrp(_CvtContext_Int):
    cmd = "channel-group",

    def remove(self, old, int_name):
        return "interface " + int_name, " no channel-group"

    def update(self, old, upd, new, int_name):
        id_, mode = upd
        return ("interface " + int_name,
                " channel-group %d%s" % (id_, mode if mode else ""))

_cvts.append(_Cvt_Int_ChnGrp)


class _Cvt_Int_Desc(_CvtContext_Int):
    cmd = "description",

    def remove(self, old, int_name):
        return "interface " + int_name, " no description"

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " description " + upd

_cvts.append(_Cvt_Int_Desc)


class _Cvt_Int_Encap(_CvtContext_Int):
    cmd = "encapsulation",

    def remove(self, old, int_name):
        return "interface " + int_name, " no encapsulation " + rem

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " encapsulation " + upd

_cvts.append(_Cvt_Int_Encap)


class _Cvt_Int_IPAccGrp(_CvtContext_Int):
    cmd = "ip-access-group", None

    def remove(self, old, int_name, dir_):
        return "interface " + int_name, " no ip access-group " + dir_

    def update(self, old, upd, new, int_name, dir_):
        return "interface " + int_name, " ip access-group %s %s" % (upd, dir_)

_cvts.append(_Cvt_Int_IPAccGrp)


class _Cvt_Int_IPAddr(_CvtContext_Int):
    cmd = "ip-address",

    def remove(self, old, int_name):
        return "interface " + int_name, " no ip address"

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " ip address " + upd

_cvts.append(_Cvt_Int_IPAddr)


class _Cvt_Int_IPAddrSec(_CvtContext_Int):
    cmd = "ip-address-secondary", None

    def remove(self, old, int_name, addr):
        return "interface " + int_name, " no ip address %s secondary" % addr

    def update(self, old, upd, new, int_name, addr):
        return "interface " + int_name, " ip address %s secondary" % addr

_cvts.append(_Cvt_Int_IPAddrSec)


class _Cvt_Int_IPFlowMon(_CvtContext_Int):
    cmd = "ip-flow-monitor", None

    def remove(self, old, int_name, dir_):
        return ("interface " + int_name,
                " no ip flow monitor %s %s" % (old, dir_))

    def update(self, old, upd, new, int_name, dir_):
        l = ["interface " + int_name]

        # we must remove the old flow monitor before setting a new one
        if old:
            l += [" no ip flow monitor %s %s" % (old, dir_)]

        l += [" ip flow monitor %s %s" % (upd, dir_)]
        return l

_cvts.append(_Cvt_Int_IPFlowMon)


class _Cvt_Int_IPHlprAddr(_CvtContext_Int):
    cmd = "ip-helper-address", None

    def remove(self, old, int_name, addr):
        return "interface " + int_name, " no ip helper-address " + addr

    def update(self, old, upd, new, int_name, addr):
        return "interface " + int_name, " ip helper-address " + addr

_cvts.append(_Cvt_Int_IPHlprAddr)


class _Cvt_Int_IPIGMPVer(_CvtContext_Int):
    cmd = "ip-igmp-version",

    def remove(self, old, int_name):
        return "interface " + int_name, " no ip igmp version"

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " ip igmp version " + upd

_cvts.append(_Cvt_Int_IPIGMPVer)


class _Cvt_Int_IPMcastBdry(_CvtContext_Int):
    cmd = "ip-multicast-boundary",

    def remove(self, old, int_name):
        return "interface " + int_name, " no ip multicast boundary"

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " ip multicast boundary " + upd

_cvts.append(_Cvt_Int_IPMcastBdry)


class _Cvt_Int_IPPIMMode(_CvtContext_Int):
    cmd = "ip-pim", "mode"

    def remove(self, old, int_name):
        return "interface " + int_name, " no ip pim " + old

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " ip pim " + upd

_cvts.append(_Cvt_Int_IPPIMMode)


class _Cvt_Int_IPPIMBSRBdr(_CvtContext_Int):
    cmd = "ip-pim", "bsr-border"

    def remove(self, old, int_name):
        return "interface " + int_name, " no ip pim bsr-border"

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " ip pim bsr-border"

_cvts.append(_Cvt_Int_IPPIMBSRBdr)


class _Cvt_Int_IPProxyARP(_CvtContext_Int):
    cmd = "ip-proxy-arp",

    def update(self, old, upd, new, int_name):
        return ("interface " + int_name,
                " " + ("" if upd else "no ") + "ip proxy-arp")

_cvts.append(_Cvt_Int_IPProxyARP)


class _Cvt_Int_IPVerifyUni(_CvtContext_Int):
    cmd = "ip-verify-unicast",

    def remove(self, old, int_name):
        return "interface " + int_name, " no ip verify unicast"

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " ip verify unicast " + upd

_cvts.append(_Cvt_Int_IPVerifyUni)


class _Cvt_Int_IPv6Addr(_CvtContext_Int):
    cmd = "ipv6-address", None

    def remove(self, old, int_name, addr):
        return "interface " + int_name, " no ipv6 address " + addr

    def update(self, old, upd, new, int_name, addr):
        return "interface " + int_name, " ipv6 address " + addr

_cvts.append(_Cvt_Int_IPv6Addr)


class _Cvt_Int_IPv6MultBdry(_CvtContext_Int):
    cmd = "ipv6-multicast-boundary-scope",

    def remove(self, old, int_name):
        return "interface " + int_name, " no ipv6 multicast boundary scope"

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " ipv6 multicast boundary scope " + upd

_cvts.append(_Cvt_Int_IPv6MultBdry)


class _Cvt_Int_IPv6PIMBSRBdr(_CvtContext_Int):
    cmd = "ipv6-pim", "bsr-border"

    def remove(self, old, int_name):
        return "interface " + int_name, " no ipv6 pim bsr border"

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " ipv6 pim bsr border"

_cvts.append(_Cvt_Int_IPv6PIMBSRBdr)


class _Cvt_Int_IPv6TrafFilt(_CvtContext_Int):
    cmd = "ipv6-traffic-filter", None

    def remove(self, old, int_name, dir_):
        return "interface " + int_name, " no ipv6 traffic-filter " + dir_

    def update(self, old, upd, new, int_name, dir_):
        return ("interface " + int_name,
               " ipv6 traffic-filter %s %s" % (upd, dir_))

_cvts.append(_Cvt_Int_IPv6TrafFilt)


class _Cvt_Int_IPv6VerifyUni(_CvtContext_Int):
    cmd = "ipv6-verify-unicast",

    def remove(self, old, rem, int_name):
        return "interface " + int_name, " no ipv6 verify unicast"

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " ipv6 verify unicast " + upd

_cvts.append(_Cvt_Int_IPv6VerifyUni)


class _Cvt_Int_ServPol(_CvtContext_Int):
    cmd = "service-policy",

    # this uses truncate() to ensure that all removes happen before any
    # update()s - this because an old policy must be removed before a
    # new one of the same type/direction is added
    #
    # calls to remove() will be matched in alphabetical order which
    # would match the add first, if it's earlier in the list

    def truncate(self, old, rem, int_name):
        l = ["interface " + int_name]
        for policy in sorted(rem):
            l.append(" no service-policy " + policy)
        return l

    def update(self, old, upd, new, int_name):
        l = ["interface " + int_name]
        for policy in sorted(upd):
            l.append(" service-policy " + policy)
        return l

_cvts.append(_Cvt_Int_ServPol)


class _Cvt_Int_StandbyIP(_CvtContext_Int):
    cmd = "standby", "group", None, "ip"

    def remove(self, old, int_name, grp):
        return "interface " + int_name, " no standby %d ip" % grp

    def update(self, old, upd, new, int_name, grp):
        return "interface " + int_name, " standby %d ip %s" % (grp, upd)

_cvts.append(_Cvt_Int_StandbyIP)


class _Cvt_Int_StandbyIPSec(_CvtContext_Int):
    cmd = "standby", "group", None, "ip-secondary", None

    def remove(self, old, int_name, grp, addr):
        return ("interface " + int_name,
                " no standby %d ip %s secondary" % (grp, addr))

    def update(self, old, upd, new, int_name, grp, addr):
        return ("interface " + int_name,
                " standby %d ip %s secondary" % (grp, addr))

_cvts.append(_Cvt_Int_StandbyIPSec)


class _Cvt_Int_StandbyIPv6(_CvtContext_Int):
    cmd = "standby", "group", None, "ipv6", None

    def remove(self, old, int_name, grp, addr):
        return ("interface " + int_name,
                " no standby %d ipv6 %s" % (grp, addr))

    def update(self, old, upd, new, int_name, grp, addr):
        return ("interface " + int_name,
                " standby %d ipv6 %s" % (grp, addr))

_cvts.append(_Cvt_Int_StandbyIPv6)


class _Cvt_Int_StandbyPreempt(_CvtContext_Int):
    cmd = "standby", "group", None, "preempt"

    def remove(self, old, int_name, grp):
        return "interface " + int_name, " no standby %d preempt" % grp

    def update(self, old, upd, new, int_name, grp):
        return "interface " + int_name, " standby %d preempt" % grp

_cvts.append(_Cvt_Int_StandbyPreempt)


class _Cvt_Int_StandbyPri(_CvtContext_Int):
    cmd = "standby", "group", None, "priority"

    def remove(self, old, int_name, grp):
        return "interface " + int_name, " no standby %d priority" % grp

    def update(self, old, upd, new, int_name, grp):
        return "interface " + int_name, " standby %d priority %d" % (grp, upd)

_cvts.append(_Cvt_Int_StandbyPri)


class _Cvt_Int_StandbyTimers(_CvtContext_Int):
    cmd = "standby", "group", None, "timers"

    def remove(self, old, int_name, grp):
        return "interface " + int_name, " no standby %d timers" % grp

    def update(self, old, upd, new, int_name, grp):
        return "interface " + int_name, " standby %d timers %s" % (grp, upd)

_cvts.append(_Cvt_Int_StandbyTimers)


class _Cvt_Int_StandbyTrk(_CvtContext_Int):
    cmd = "standby", "group", None, "track", None

    def remove(self, old, int_name, grp, obj):
        return "interface " + int_name, " no standby %d track %s" % (grp, obj)

    def update(self, old, upd, new, int_name, grp, obj):
        return ("interface " + int_name,
                " standby %d track %s%s"
                    % (grp, obj, (" " + upd) if upd else ""))

_cvts.append(_Cvt_Int_StandbyTrk)


class _Cvt_Int_StandbyVer(_CvtContext_Int):
    cmd = "standby", "version"

    def remove(self, old, int_name):
        return "interface " + int_name, " no standby version"

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " standby version %d" % upd

_cvts.append(_Cvt_Int_StandbyVer)


class _Cvt_Int_StormCtrl(_CvtContext_Int):
    cmd = "storm-control", None

    def remove(self, old, int_name, traffic):
        return ("interface " + int_name,
                " no storm-control %s level" % traffic)

    def update(self, old, upd, new, int_name, traffic):
        return ("interface " + int_name,
                " storm-control %s level %.2f" % (traffic, upd))

_cvts.append(_Cvt_Int_StormCtrl)


class _Cvt_Int_SwPort(_CvtContext_Int):
    cmd = "switchport",

    def remove(self, old, int_name):
        # if the 'switchport' option is not present, that doesn't mean
        # it's disabled but just that it's not specified, so we assume
        # the default is for it to be disabled
        #
        # TODO: this is the case for routers (which we're concerned
        # about here) but not switches: we'd probably need a separate
        # platform for this
        return "interface " + int_name, " no switchport"

    def update(self, old, upd, new, int_name):
        return ("interface " + int_name,
                " " + ("" if upd else "no ") + "switchport")

_cvts.append(_Cvt_Int_SwPort)


class _Cvt_Int_SwPortMode(_CvtContext_Int):
    cmd = "switchport-mode",

    def remove(self, old, int_name):
        return "interface " + int_name, " no switchport mode"

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " switchport mode " + upd

_cvts.append(_Cvt_Int_SwPortMode)


class _Cvt_Int_SwPortNoNeg(_CvtContext_Int):
    cmd = "switchport-nonegotiate",

    def remove(self, old, int_name):
        return "interface " + int_name, " no switchport nonegotiate"

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " switchport nonegotiate"

_cvts.append(_Cvt_Int_SwPortNoNeg)


class _Cvt_Int_SwPortTrkNtv(_CvtContext_Int):
    # we just match the interface as we need to look inside it to see if
    # the interface is part of a channel group
    cmd = tuple()
    ext = "switchport-trunk-native",

    def remove(self, old, int_name):
        # if this interface is in a port-channel, we do all changes
        # there, so skip this
        if "channel-group" in old:
            return None

        return "interface " + int_name, " no switchport trunk native vlan"

    def update(self, old, upd, new, int_name):
        # if this interface is in a port-channel, we do all changes
        # there, so skip this
        if "channel-group" in new:
            return None

        return ("interface " + int_name,
                " switchport trunk native vlan %d" % self.get_ext(upd))

_cvts.append(_Cvt_Int_SwPortTrkNtv)


class _Cvt_Int_SwPortTrkAlw(_CvtContext_Int):
    # we just match the interface as we need to look inside it to see if
    # the interface is part of a channel group
    cmd = tuple()
    ext = "switchport-trunk-allow",

    def truncate(self, old, rem, int_name):
        # if this interface is in a port-channel, we do all changes
        # there, so skip this
        if "channel-group" in old:
            return None

        l = ["interface " + int_name]
        for tag in sorted(self.get_ext(rem)):
            l.append(" switchport trunk allowed vlan remove %d" % tag)
        return l

    def update(self, old, upd, new, int_name):
        # if this interface is in a port-channel, we do all changes
        # there, so skip this
        if "channel-group" in new:
            return None

        l = ["interface " + int_name]
        for tag in sorted(self.get_ext(upd)):
            l.append(" switchport trunk allowed vlan add %d" % tag)
        return l

_cvts.append(_Cvt_Int_SwPortTrkAlw)


class _Cvt_Int_XConn(_CvtContext_Int):
    cmd = "xconnect",

    def remove(self, old, int_name):
        return "interface " + int_name, " no xconnect"

    def update(self, old, upd, new, int_name):
        return "interface " + int_name, " xconnect " + upd

_cvts.append(_Cvt_Int_XConn)


# we put the 'interface / no shutdown' at the end to only enable the
# interface once it's been correctly [re]configured

class _Cvt_Int_NoShutdown(_CvtContext_Int):
    cmd = "shutdown",
    name = "no-shutdown"

    def remove(self, old, int_name):
        return "interface " + int_name, " no shutdown"

_cvts.append(_Cvt_Int_NoShutdown)



# IP[V6] ACCESS-LIST ...



class _Cvt_IPACL_Std(DiffConvert):
    cmd = "ip-access-list-standard", None

    def remove(self, old, acl_name):
        return "no ip access-list standard " + acl_name

    def update(self, old, upd, new, acl_name):
        r = ["ip access-list standard " + acl_name]
        r.extend(explain_diffs(old, new, indent=" "))
        return r

_cvts.append(_Cvt_IPACL_Std)


class _Cvt_IPACL_Ext(DiffConvert):
    cmd = "ip-access-list-extended", None

    def remove(self, old, acl_name):
        return "no ip access-list extended " + acl_name

    def update(self, old, upd, new, acl_name):
        r = ["ip access-list extended " + acl_name]
        r.extend(explain_diffs(old, new, indent=" "))
        return r

_cvts.append(_Cvt_IPACL_Ext)


class _Cvt_IPv6ACL_Ext(DiffConvert):
    cmd = "ipv6-access-list", None

    def remove(self, old, acl_name):
        return "no ipv6 access-list " + acl_name

    def update(self, old, upd, new, acl_name):
        r = ["ipv6 access-list " + acl_name]
        r.extend(explain_diffs(old, new, indent=" "))
        return r

_cvts.append(_Cvt_IPv6ACL_Ext)



# IP[V6] PREFIX-LIST ...



class _Cvt_IPPfxList(DiffConvert):
    cmd = "ip-prefix-list", None

    def remove(self, old, pfx_name):
        return "no ip prefix-list " + pfx_name

    def update(self, old, upd, new, pfx_name):
        return explain_diffs(old, new, prefix="ip prefix-list %s " % pfx_name)

_cvts.append(_Cvt_IPPfxList)


class _Cvt_IPv6PfxList(DiffConvert):
    cmd = "ipv6-prefix-list", None

    def remove(self, old, pfx_name):
        return "no ipv6 prefix-list " + pfx_name

    def update(self, old, upd, new, pfx_name):
        return explain_diffs(
                   old, new, prefix="ipv6 prefix-list %s " % pfx_name)

_cvts.append(_Cvt_IPv6PfxList)



# IP[V6] ROUTE ...



class _Cvt_IPRoute(DiffConvert):
    cmd = "ip-route", None

    def remove(self, old, route):
        return "no ip route " + route

    def update(self, old, upd, new, route):
        return "ip route " + route

_cvts.append(_Cvt_IPRoute)


class _Cvt_IPv6Route(DiffConvert):
    cmd = "ipv6-route", None

    def remove(self, old, route):
        return "no ipv6 route " + route

    def update(self, old, upd, new, route):
        return "ipv6 route " + route

_cvts.append(_Cvt_IPv6Route)



# [NO] SPANNING-TREE ...



class _Cvt_NoSTP(DiffConvert):
    cmd = "no-spanning-tree-vlan", None

    def remove(self, old, tag):
        # removing 'no spanning-tree' enables spanning-tree
        return "spanning-tree vlan %d" % tag

    def update(self, old, upd, new, tag):
        # adding 'no spanning-tree' disables spanning-tree
        return "no spanning-tree vlan %d" % tag

_cvts.append(_Cvt_NoSTP)


class _Cvt_STPPri(DiffConvert):
    cmd = "spanning-tree-vlan-priority", None

    def remove(self, old, tag):
        return "no spanning-tree vlan %d priority" % tag

    def update(self, old, upd, new, tag):
        return "spanning-tree vlan %d priority %d" % (tag, upd)

_cvts.append(_Cvt_STPPri)



# TRACK ...



class _Cvt_Track(DiffConvert):
    cmd = "track", None
    ext = "criterion",

    def remove(self, old, obj):
        return "no track %d" % obj

    def update(self, old, upd, new, obj):
        return "track %d %s" % (obj, upd["criterion"])

_cvts.append(_Cvt_Track)


class _CvtContext_Track(DiffConvert):
    context = "track", None


class _Cvt_Track_Delay(_CvtContext_Track):
    cmd = "delay",

    def remove(self, old, obj):
        return "track %d" % obj, " no delay"

    def update(self, old, upd, new, obj):
        return "track %d" % obj, " delay " + upd

_cvts.append(_Cvt_Track_Delay)


class _Cvt_Track_IPVRF(_CvtContext_Track):
    cmd = "ip-vrf",

    def remove(self, old, obj):
        return "track %d" % obj, " no ip vrf"

    def update(self, old, upd, new, obj):
        return "track %d" % obj, " ip vrf " + upd

_cvts.append(_Cvt_Track_IPVRF)


class _Cvt_Track_IPv6VRF(_CvtContext_Track):
    cmd = "ipv6-vrf",

    def remove(self, old, obj):
        return "track %d" % obj, " no ipv6 vrf"

    def update(self, old, upd, new, obj):
        return "track %d" % obj, " ipv6 vrf " + upd

_cvts.append(_Cvt_Track_IPv6VRF)


class _Cvt_Track_Obj(_CvtContext_Track):
    context = "track", None
    cmd = "object", None

    def remove(self, old, obj, sub_obj):
        return "track %d" % obj, " no object " + sub_obj

    def update(self, old, upd, new, obj, sub_obj):
        return "track %d" % obj, " object " + sub_obj

_cvts.append(_Cvt_Track_Obj)



# VLAN ...



class _Cvt_VLAN(DiffConvert):
    cmd = "vlan", None

    def remove(self, old, tag):
        return "no vlan %d" % tag

    def add(self, new, tag):
        return "vlan %d" % tag

_cvts.append(_Cvt_VLAN)


class _Cvt_VLAN_Name(DiffConvert):
    context = "vlan", None
    cmd = "name",

    def remove(self, old, tag):
        return "vlan %d" % tag, " no name"

    def update(self, old, upd, new, tag):
        return "vlan %d" % tag, " name " + upd

_cvts.append(_Cvt_VLAN_Name)



# --- context parser ---



class CiscoIOSDiffConfig(DiffConfig):
    """This class is used to compare two IOS configuration files and
    generate a configuration file to transform one into the other.
    """


    def _add_converters(self):
        "This method adds the converters for Cisco IOS."

        for cvt_class in _cvts:
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

# ios.converters
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



"""Cisco IOS configuration converters module.

This module contains the converters to change individual configuration
elements of a Cisco IOS configuration into another.
"""



# --- imports ---



from .utils import is_int_physical, explain_diffs
from ..diff import DiffConvert
from ..misc import get_all_subclasses



# --- converter classes ---



# Cvt is created to be a shorthand for the DiffConvert class as we'll
# be using it a lot

Cvt = DiffConvert



# SYSTEM



class Cvt_Hostname(Cvt):
    cmd = "hostname",

    def remove(self, old):
        return "no hostname"

    def update(self, old, upd, new):
        return "hostname " + new



# INTERFACE ...



class Cvt_Int(Cvt):
    cmd = "interface", None

    def remove(self, old, int_name):
        # only remove the interface if it's not physical
        if is_int_physical(int_name):
            return

        return "no interface " + int_name

    def add(self, new, int_name):
        return "interface " + int_name


class CvtContext_Int(Cvt):
    context = "interface", None

    def enter(self, int_name):
        return "interface " + int_name,


# we put the 'interface / shutdown' at the start to shut it down before
# we do any [re]configuration

class Cvt_Int_Shutdown(CvtContext_Int):
    cmd = "shutdown",
    name = "shutdown"

    def update(self, old, upd, new, int_name):
        # we only 'shutdown' if we are disabling the port ('no shutdown'
        # happens at the end of interface configuration)
        if new:
            return [*self.enter(int_name), " shutdown"]


# we do VRF changes on an interface before we do any IP configuration,
# otherwise it will be removed

class Cvt_Int_VRFFwd(CvtContext_Int):
    cmd = "vrf-forwarding",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no vrf forwarding"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " vrf forwarding " + new]
        # TODO: need to find some way to trigger reapplication of IP
        # information (address, HSRP, etc.)


class Cvt_Int_ARPTime(CvtContext_Int):
    cmd = "arp-timeout",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no arp timeout"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " arp timeout " + str(new)]


class Cvt_Int_CDPEna(CvtContext_Int):
    cmd = "cdp-enable",

    def remove(self, old, int_name):
        # if the 'cdp enable' option is not present, that doesn't mean
        # it's disabled but just that it's not specified, so we assume
        # the default is for it to be enabled
        return [*self.enter(int_name), " cdp enable"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name),
                " " + ("" if upd else "no ") + "cdp enable"]


class Cvt_Int_ChnGrp(CvtContext_Int):
    cmd = "channel-group",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no channel-group"]

    def update(self, old, upd, new, int_name):
        id_, mode = new
        return [*self.enter(int_name),
                " channel-group %d%s" % (id_, mode if mode else "")]


class Cvt_Int_Desc(CvtContext_Int):
    cmd = "description",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no description"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " description " + new]


class Cvt_Int_Encap(CvtContext_Int):
    cmd = "encapsulation",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no encapsulation " + rem]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " encapsulation " + new]


class Cvt_Int_IPAccGrp(CvtContext_Int):
    cmd = "ip-access-group", None

    def remove(self, old, int_name, dir_):
        return [*self.enter(int_name), " no ip access-group " + dir_]

    def update(self, old, upd, new, int_name, dir_):
        return [*self.enter(int_name), " ip access-group %s %s" % (new, dir_)]


# ip-address ...


class Cvt_Int_IPAddr(CvtContext_Int):
    cmd = "ip-address",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip address"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip address " + new]


class Cvt_Int_IPAddrSec(CvtContext_Int):
    cmd = "ip-address-secondary", None

    def remove(self, old, int_name, addr):
        return [*self.enter(int_name), " no ip address %s secondary" % addr]

    def update(self, old, upd, new, int_name, addr):
        return [*self.enter(int_name), " ip address %s secondary" % addr]


# ...


class Cvt_Int_IPFlowMon(CvtContext_Int):
    cmd = "ip-flow-monitor", None

    def remove(self, old, int_name, dir_):
        return [*self.enter(int_name),
                " no ip flow monitor %s %s" % (old, dir_)]

    def update(self, old, upd, new, int_name, dir_):
        l = [*self.enter(int_name)]

        # we must remove the old flow monitor before setting a new one
        if old:
            l += [" no ip flow monitor %s %s" % (old, dir_)]

        l += [" ip flow monitor %s %s" % (new, dir_)]
        return l


class Cvt_Int_IPHlprAddr(CvtContext_Int):
    cmd = "ip-helper-address", None

    def remove(self, old, int_name, addr):
        return [*self.enter(int_name), " no ip helper-address " + addr]

    def update(self, old, upd, new, int_name, addr):
        return [*self.enter(int_name), " ip helper-address " + addr]


class Cvt_Int_IPIGMPVer(CvtContext_Int):
    cmd = "ip-igmp-version",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip igmp version"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip igmp version " + new]


class Cvt_Int_IPMcastBdry(CvtContext_Int):
    cmd = "ip-multicast-boundary",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip multicast boundary"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip multicast boundary " + new]


# ip-ospf ...


class Cvt_Int_IPOSPFArea(CvtContext_Int):
    cmd = "ip-ospf", "area"

    def remove(self, old, int_name):
        return [*self.enter(int_name),
                " no ip ospf %d area %s" % (old["process"], old["id"])]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name),
                " ip ospf %d area %s" % (new["process"], new["id"])]


class Cvt_Int_IPOSPFAuth(CvtContext_Int):
    cmd = "ip-ospf", "authentication"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip ospf authentication"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip ospf authentication " + new]


class Cvt_Int_IPOSPFCost(CvtContext_Int):
    cmd = "ip-ospf", "cost"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip ospf cost"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip ospf cost " + str(new)]


class Cvt_Int_IPOSPFDeadIvl(CvtContext_Int):
    cmd = "ip-ospf", "dead-interval"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip ospf dead-interval"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip ospf dead-interval " + str(new)]


class Cvt_Int_IPOSPFHelloIvl(CvtContext_Int):
    cmd = "ip-ospf", "hello-interval"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip ospf hello-interval"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip ospf hello-interval " + str(new)]


class Cvt_Int_IPOSPFMsgDigKey(CvtContext_Int):
    cmd = "ip-ospf", "message-digest-key", None

    def remove(self, old, int_name, id_):
        return [*self.enter(int_name),
                " no ip ospf message-digest-key " + str(id_)]

    def update(self, old, upd, new, int_name, id_):
        return [*self.enter(int_name),
                " ip ospf message-digest-key %d md5 %s" % (id_, new)]


class Cvt_Int_IPOSPFNet(CvtContext_Int):
    cmd = "ip-ospf", "network"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip ospf network"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip ospf network " + new]


# ip-pim ...


class Cvt_Int_IPPIMMode(CvtContext_Int):
    cmd = "ip-pim", "mode"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip pim " + old]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip pim " + new]


class Cvt_Int_IPPIMBSRBdr(CvtContext_Int):
    cmd = "ip-pim", "bsr-border"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip pim bsr-border"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip pim bsr-border"]


# ...


class Cvt_Int_IPProxyARP(CvtContext_Int):
    cmd = "ip-proxy-arp",

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name),
                " " + ("" if upd else "no ") + "ip proxy-arp"]


class Cvt_Int_IPVerifyUni(CvtContext_Int):
    cmd = "ip-verify-unicast",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ip verify unicast"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ip verify unicast " + new]


class Cvt_Int_IPv6Addr(CvtContext_Int):
    cmd = "ipv6-address", None

    def remove(self, old, int_name, addr):
        return [*self.enter(int_name), " no ipv6 address " + addr]

    def update(self, old, upd, new, int_name, addr):
        return [*self.enter(int_name), " ipv6 address " + addr]


class Cvt_Int_IPv6MultBdry(CvtContext_Int):
    cmd = "ipv6-multicast-boundary-scope",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ipv6 multicast boundary scope"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ipv6 multicast boundary scope " + new]


# ospfv3 ...


class Cvt_Int_OSPFv3Area(CvtContext_Int):
    cmd = "ospfv3", "area"

    def remove(self, old, int_name):
        return [*self.enter(int_name),
                " ospfv3 %d area %s" % (old["process"], old["id"])]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name),
                " ospfv3 %d area %s" % (new["process"], new["id"])]


class Cvt_Int_OSPFv3Cost(CvtContext_Int):
    cmd = "ospfv3", "cost"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ospfv3 cost"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ospfv3 cost " + str(new)]


class Cvt_Int_OSPFv3DeadIvl(CvtContext_Int):
    cmd = "ospfv3", "dead-interval"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ospfv3 dead-interval"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ospfv3 dead-interval " + str(new)]


class Cvt_Int_OSPFv3HelloIvl(CvtContext_Int):
    cmd = "ospfv3", "hello-interval"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ospfv3 hello-interval"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ospfv3 hello-interval " + str(new)]


class Cvt_Int_OSPFv3Net(CvtContext_Int):
    cmd = "ospfv3", "network"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ospfv3 network"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ospfv3 network " + new]


# ...


class Cvt_Int_IPv6PIMBSRBdr(CvtContext_Int):
    cmd = "ipv6-pim", "bsr-border"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ipv6 pim bsr border"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ipv6 pim bsr border"]


class Cvt_Int_IPv6TrafFilt(CvtContext_Int):
    cmd = "ipv6-traffic-filter", None

    def remove(self, old, int_name, dir_):
        return [*self.enter(int_name), " no ipv6 traffic-filter " + dir_]

    def update(self, old, upd, new, int_name, dir_):
        return [*self.enter(int_name),
               " ipv6 traffic-filter %s %s" % (new, dir_)]


class Cvt_Int_IPv6VerifyUni(CvtContext_Int):
    cmd = "ipv6-verify-unicast",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no ipv6 verify unicast"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " ipv6 verify unicast " + new]


class Cvt_Int_ServPol(CvtContext_Int):
    cmd = "service-policy", None, None

    def type_str(self, type_):
        # we only specify the 'type' if one is set (the default is a
        # policer)
        return " type %s" if type_ else ""

    def remove(self, old, int_name, dir_, type_):
        return [*self.enter(int_name),
                " no service-policy%s %s %s"
                    % (self.type_str(type_), dir_, old)]

    def update(self, old, upd, new, int_name, dir_, type_):
        l = [*self.enter(int_name)]

        # we cannot just replace a service-policy: we need to remove the
        # old one first
        if old:
            l.append(" no service-policy%s %s %s"
                         % (self.type_str(type_), dir_, old))

        l.append(" service-policy%s %s %s"
                     % (self.type_str(type_), dir_, new))

        return l


# standby ...


class Cvt_Int_StandbyIP(CvtContext_Int):
    cmd = "standby", "group", None, "ip"

    def remove(self, old, int_name, grp):
        return [*self.enter(int_name), " no standby %d ip" % grp]

    def update(self, old, upd, new, int_name, grp):
        return [*self.enter(int_name), " standby %d ip %s" % (grp, new)]


class Cvt_Int_StandbyIPSec(CvtContext_Int):
    cmd = "standby", "group", None, "ip-secondary", None

    def remove(self, old, int_name, grp, addr):
        return [*self.enter(int_name),
                " no standby %d ip %s secondary" % (grp, addr)]

    def update(self, old, upd, new, int_name, grp, addr):
        return [*self.enter(int_name),
                " standby %d ip %s secondary" % (grp, addr)]


class Cvt_Int_StandbyIPv6(CvtContext_Int):
    cmd = "standby", "group", None, "ipv6", None

    def remove(self, old, int_name, grp, addr):
        return [*self.enter(int_name),
                " no standby %d ipv6 %s" % (grp, addr)]

    def update(self, old, upd, new, int_name, grp, addr):
        return [*self.enter(int_name),
                " standby %d ipv6 %s" % (grp, addr)]


class Cvt_Int_StandbyPreempt(CvtContext_Int):
    cmd = "standby", "group", None, "preempt"

    def remove(self, old, int_name, grp):
        return [*self.enter(int_name), " no standby %d preempt" % grp]

    def update(self, old, upd, new, int_name, grp):
        return [*self.enter(int_name), " standby %d preempt" % grp]


class Cvt_Int_StandbyPri(CvtContext_Int):
    cmd = "standby", "group", None, "priority"

    def remove(self, old, int_name, grp):
        return [*self.enter(int_name), " no standby %d priority" % grp]

    def update(self, old, upd, new, int_name, grp):
        return [*self.enter(int_name), " standby %d priority %d" % (grp, new)]


class Cvt_Int_StandbyTimers(CvtContext_Int):
    cmd = "standby", "group", None, "timers"

    def remove(self, old, int_name, grp):
        return [*self.enter(int_name), " no standby %d timers" % grp]

    def update(self, old, upd, new, int_name, grp):
        return [*self.enter(int_name), " standby %d timers %s" % (grp, new)]


class Cvt_Int_StandbyTrk(CvtContext_Int):
    cmd = "standby", "group", None, "track", None

    def remove(self, old, int_name, grp, obj):
        return [*self.enter(int_name), " no standby %d track %s" % (grp, obj)]

    def update(self, old, upd, new, int_name, grp, obj):
        return [*self.enter(int_name),
                " standby %d track %s%s"
                    % (grp, obj, (" " + new) if new else "")]


class Cvt_Int_StandbyVer(CvtContext_Int):
    cmd = "standby", "version"

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no standby version"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " standby version " + str(new)]


# ...


class Cvt_Int_StormCtrl(CvtContext_Int):
    cmd = "storm-control", None

    def remove(self, old, int_name, traffic):
        return [*self.enter(int_name),
                " no storm-control %s level" % traffic]

    def update(self, old, upd, new, int_name, traffic):
        return [*self.enter(int_name),
                " storm-control %s level %.2f" % (traffic, new)]


# switchport ...


class Cvt_Int_SwPort(CvtContext_Int):
    cmd = "switchport",

    def remove(self, old, int_name):
        # if the 'switchport' option is not present, that doesn't mean
        # it's disabled but just that it's not specified, so we assume
        # the default is for it to be disabled
        #
        # TODO: this is the case for routers (which we're concerned
        # about here) but not switches: we'd probably need a separate
        # platform for this
        return [*self.enter(int_name), " no switchport"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name),
                " " + ("" if upd else "no ") + "switchport"]


class Cvt_Int_SwPortMode(CvtContext_Int):
    cmd = "switchport-mode",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no switchport mode"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " switchport mode " + new]


class Cvt_Int_SwPortNoNeg(CvtContext_Int):
    cmd = "switchport-nonegotiate",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no switchport nonegotiate"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " switchport nonegotiate"]


class Cvt_Int_SwPortTrkNtv(CvtContext_Int):
    # we just match the interface as we need to look inside it to see if
    # the interface is part of a channel group
    cmd = tuple()
    ext = "switchport-trunk-native",

    def remove(self, old, int_name):
        # if this interface is in a port-channel, we do all changes
        # there, so skip this
        if "channel-group" in old:
            return None

        return [*self.enter(int_name), " no switchport trunk native vlan"]

    def update(self, old, upd, new, int_name):
        # if this interface is in a port-channel, we do all changes
        # there, so skip this
        if "channel-group" in new:
            return None

        return [*self.enter(int_name),
                " switchport trunk native vlan " + str(self.get_ext(new))]


class Cvt_Int_SwPortTrkAlw(CvtContext_Int):
    # we just match the interface as we need to look inside it to see if
    # the interface is part of a channel group
    cmd = tuple()
    ext = "switchport-trunk-allow",

    def truncate(self, old, rem, int_name):
        # if this interface is in a port-channel, we do all changes
        # there, so skip this
        if "channel-group" in old:
            return None

        l = [*self.enter(int_name)]
        for tag in sorted(self.get_ext(rem)):
            l.append(" switchport trunk allowed vlan remove " + str(tag))
        return l

    def update(self, old, upd, new, int_name):
        # if this interface is in a port-channel, we do all changes
        # there, so skip this
        if "channel-group" in new:
            return None

        l = [*self.enter(int_name)]
        for tag in sorted(self.get_ext(upd)):
            l.append(" switchport trunk allowed vlan add " + str(tag))
        return l


# ...


class Cvt_Int_XConn(CvtContext_Int):
    cmd = "xconnect",

    def remove(self, old, int_name):
        return [*self.enter(int_name), " no xconnect"]

    def update(self, old, upd, new, int_name):
        return [*self.enter(int_name), " xconnect " + new]


# we put the 'interface / no shutdown' at the end to only enable the
# interface once it's been correctly [re]configured

class Cvt_Int_NoShutdown(CvtContext_Int):
    cmd = "shutdown",
    name = "no-shutdown"

    def update(self, old, upd, new, int_name):
        # we only 'no shutdown' if we are enabling the port ('shutdown'
        # happens at the start of interface configuration)
        if not new:
            return [*self.enter(int_name), " no shutdown"]



# IP[V6] ACCESS-LIST ...



class Cvt_IPACL_Std(Cvt):
    cmd = "ip-access-list-standard", None

    def remove(self, old, acl_name):
        return "no ip access-list standard " + acl_name

    def update(self, old, upd, new, acl_name):
        return ["no ip access-list standard " + acl_name,
                "ip access-list standard " + acl_name,
                *explain_diffs(old, new, indent=" ")]


class Cvt_IPACL_Ext(Cvt):
    cmd = "ip-access-list-extended", None

    def remove(self, old, acl_name):
        return "no ip access-list extended " + acl_name

    def update(self, old, upd, new, acl_name):
        return ["no ip access-list extended " + acl_name,
                "ip access-list extended " + acl_name,
                *explain_diffs(old, new, indent=" ")]


class Cvt_IPv6ACL_Ext(Cvt):
    cmd = "ipv6-access-list", None

    def remove(self, old, acl_name):
        return "no ipv6 access-list " + acl_name

    def update(self, old, upd, new, acl_name):
        return ["no ipv6 access-list " + acl_name,
                "ipv6 access-list " + acl_name,
                *explain_diffs(old, new, indent=" ")]



# IP AS-PATH ACCESS-LIST ...



class Cvt_IPASPathACL(Cvt):
    cmd = "ip-as-path-access-list", None

    def to_str(self, rule):
        action, re = rule
        return action + " " + re

    def remove(self, old, num):
        return "no ip as-path access-list " + str(num)

    def update(self, old, upd, new, num):
        r = []
        if old:
            r += ["no ip as-path access-list " + str(num)]
        r += explain_diffs(old, new, prefix="ip as-path access-list %d " % num,
                           to_str_func=self.to_str)
        return r



# IP[V6] PREFIX-LIST ...



class Cvt_IPPfxList(Cvt):
    cmd = "ip-prefix-list", None

    def remove(self, old, pfx_name):
        return "no ip prefix-list " + pfx_name

    def update(self, old, upd, new, pfx_name):
        return ["no ip prefix-list " + pfx_name,
                *explain_diffs(
                    old, new, prefix="ip prefix-list %s " % pfx_name)]


class Cvt_IPv6PfxList(Cvt):
    cmd = "ipv6-prefix-list", None

    def remove(self, old, pfx_name):
        return "no ipv6 prefix-list " + pfx_name

    def update(self, old, upd, new, pfx_name):
        return ["no ipv6 prefix-list " + pfx_name,
                *explain_diffs(
                    old, new, prefix="ipv6 prefix-list %s " % pfx_name)]



# IP[V6] ROUTE ...



class Cvt_IPRoute(Cvt):
    cmd = "ip-route", None

    def remove(self, old, route):
        return "no ip route " + route

    def update(self, old, upd, new, route):
        return "ip route " + route


class Cvt_IPv6Route(Cvt):
    cmd = "ipv6-route", None

    def remove(self, old, route):
        return "no ipv6 route " + route

    def update(self, old, upd, new, route):
        return "ipv6 route " + route



# ROUTER OSPF ...



class Cvt_RtrOSPF(Cvt):
    cmd = "router", "ospf", None

    def remove(self, old, proc):
        return "no router ospf " + str(proc)

    def add(self, new, proc):
        return "router ospf " + str(proc)


class CvtContext_RtrOSPF(Cvt):
    context = "router", "ospf", None

    def enter(self, proc):
        return "router ospf " + str(proc),


class Cvt_RtrOSPF_Id(CvtContext_RtrOSPF):
    cmd = "id",

    def remove(self, old, proc):
        return [*self.enter(proc), " no router-id"]

    def update(self, old, upd, new, proc):
        return [*self.enter(proc), " router-id " + new]


class Cvt_RtrOSPF_AreaNSSA(CvtContext_RtrOSPF):
    cmd = "area", None, "nssa"

    def remove(self, old, proc, area):
        return [*self.enter(proc), " no area %s nssa" % area]

    def update(self, old, upd, new, proc, area):
        s = ""
        if "no-redistribution" in new: s += " no-redistribution"
        if "no-summary" in new: s += " no-summary"
        return [*self.enter(proc), " area %s nssa%s" % (area, s)]


class Cvt_RtrOSPF_PasvInt_Dflt(CvtContext_RtrOSPF):
    cmd = "passive-interface", "default"

    def remove(self, old, proc):
        return [*self.enter(proc),
                " %spassive-interface default" % ("no " if old else "")]

    def update(self, old, upd, new, proc):
        return [*self.enter(proc),
                " %spassive-interface default" % ("" if new else "no ")]


class Cvt_RtrOSPF_PasvInt_Int(CvtContext_RtrOSPF):
    cmd = "passive-interface", "interface", None

    def remove(self, old, proc, int_name):
        return [*self.enter(proc),
                " %spassive-interface %s" % ("no " if old else "", int_name)]

    def update(self, old, upd, new, proc, int_name):
        return [*self.enter(proc),
                " %spassive-interface %s" % ("" if new else "no ", int_name)]



# ROUTER OSPFV3 ...



class Cvt_RtrOSPFv3(Cvt):
    cmd = "router", "ospfv3", None

    def remove(self, old, proc):
        return "no router ospfv3 " + str(proc)

    def add(self, new, proc):
        return "router ospfv3 " + str(proc)


class CvtContext_RtrOSPFv3(Cvt):
    context = "router", "ospfv3", None

    def enter(self, proc):
        return "router ospfv3 " + str(proc),


class Cvt_RtrOSPFv3_Id(CvtContext_RtrOSPFv3):
    cmd = "id",

    def remove(self, old, proc):
        return [*self.enter(proc), " no router-id"]

    def update(self, old, upd, new, proc):
        return [*self.enter(proc), " router-id " + new]


class Cvt_RtrOSPFv3_AreaNSSA(CvtContext_RtrOSPFv3):
    cmd = "area", None, "nssa"

    def remove(self, old, proc, area):
        return [*self.enter(proc), " no area %s nssa" % area]

    def update(self, old, upd, new, proc, area):
        s = ""
        if "no-redistribution" in new: s += " no-redistribution"
        if "no-summary" in new: s += " no-summary"
        return [*self.enter(proc), " area %s nssa%s" % (area, s)]


class Cvt_RtrOSPFv3_AF(CvtContext_RtrOSPFv3):
    cmd = "address-family", None

    def remove(self, old, vrf, af):
        return [*self.enter(vrf), " no address-family " + af]

    def add(self, new, vrf, af):
        return [*self.enter(vrf), " address-family " + af]


class CvtContext_RtrOSPFv3_AF(CvtContext_RtrOSPFv3):
    context = "router", "ospfv3", None, "address-family", None

    def enter(self, vrf, af):
        return [*super().enter(vrf), " address-family " + af]


class Cvt_RtrOSPFv3_AF_PasvInt_Dflt(CvtContext_RtrOSPFv3_AF):
    cmd = "passive-interface", "default"

    def remove(self, old, proc, af):
        return [*self.enter(proc, af),
                " %spassive-interface default" % ("no " if old else "")]

    def update(self, old, upd, new, proc, af):
        return [*self.enter(proc, af),
                "  %spassive-interface default" % ("" if new else "no ")]


class Cvt_RtrOSPFv3_AF_PasvInt_Int(CvtContext_RtrOSPFv3_AF):
    cmd = "passive-interface", "interface", None

    def remove(self, old, proc, af, int_name):
        return [*self.enter(proc, af),
                "  %spassive-interface %s" % ("no " if old else "", int_name)]

    def update(self, old, upd, new, proc, af, int_name):
        return [*self.enter(proc, af),
                "  %spassive-interface %s" % ("" if new else "no ", int_name)]



# [NO] SPANNING-TREE ...



class Cvt_NoSTP(Cvt):
    cmd = "no-spanning-tree-vlan", None

    def remove(self, old, tag):
        # removing 'no spanning-tree' enables spanning-tree
        return "spanning-tree vlan %d" % tag

    def update(self, old, upd, new, tag):
        # adding 'no spanning-tree' disables spanning-tree
        return "no spanning-tree vlan %d" % tag


class Cvt_STPPri(Cvt):
    cmd = "spanning-tree-vlan-priority", None

    def remove(self, old, tag):
        return "no spanning-tree vlan %d priority" % tag

    def update(self, old, upd, new, tag):
        return "spanning-tree vlan %d priority %d" % (tag, new)



# TRACK ...



class Cvt_Track(Cvt):
    cmd = "track", None
    ext = "criterion",

    def remove(self, old, obj):
        return "no track %d" % obj

    def update(self, old, upd, new, obj):
        return "track %d %s" % (obj, new["criterion"])


class CvtContext_Track(Cvt):
    context = "track", None

    def enter(self, obj):
        return "track " + str(obj),


class Cvt_Track_Delay(CvtContext_Track):
    cmd = "delay",

    def remove(self, old, obj):
        return [*self.enter(obj), " no delay"]

    def update(self, old, upd, new, obj):
        return [*self.enter(obj), " delay " + new]


class Cvt_Track_IPVRF(CvtContext_Track):
    cmd = "ip-vrf",

    def remove(self, old, obj):
        return [*self.enter(obj), " no ip vrf"]

    def update(self, old, upd, new, obj):
        return [*self.enter(obj), " ip vrf " + new]


class Cvt_Track_IPv6VRF(CvtContext_Track):
    cmd = "ipv6-vrf",

    def remove(self, old, obj):
        return [*self.enter(obj), " no ipv6 vrf"]

    def update(self, old, upd, new, obj):
        return [*self.enter(obj), " ipv6 vrf " + new]


class Cvt_Track_Obj(CvtContext_Track):
    context = "track", None
    cmd = "object", None

    def remove(self, old, obj, sub_obj):
        return [*self.enter(obj), " no object " + sub_obj]

    def update(self, old, upd, new, obj, sub_obj):
        return [*self.enter(obj), " object " + sub_obj]



# VLAN ...



class Cvt_VLAN(Cvt):
    cmd = "vlan", None

    def remove(self, old, tag):
        return "no vlan %d" % tag

    def add(self, new, tag):
        return "vlan %d" % tag


class Cvt_VLAN_Name(Cvt):
    context = "vlan", None
    cmd = "name",

    def remove(self, old, tag):
        return "vlan " + str(tag), " no name"

    def update(self, old, upd, new, tag):
        return "vlan " + str(tag), " name " + new



# VRF ...



class Cvt_VRF(Cvt):
    cmd = "vrf", None

    def remove(self, old, name):
        return "no vrf definition " + name

    def add(self, new,  name):
        return "vrf definition " + name


class CvtContext_VRF(Cvt):
    context = "vrf", None

    def enter(self, vrf):
        return "vrf definition " + vrf,


class Cvt_VRF_RD(CvtContext_VRF):
    cmd = "rd",

    def remove(self, old, vrf):
        return [*self.enter(vrf), " no rd " + old]

    def update(self, old, upd, new, vrf):
        l = list(super().enter(vrf))
        if old:
            l.append(" no rd " + old)
        l.append(" rd " + new)
        return l


class Cvt_VRF_RT(CvtContext_VRF):
    cmd = "route-target", None, None

    def truncate(self, old, rem, vrf, dir_, rt):
        return [*self.enter(vrf), " no route-target %s %s" % (dir_, rt)]

    def update(self, old, upd, new, vrf, dir_, rt):
        return [*self.enter(vrf), " route-target %s %s" % (dir_, rt)]


class Cvt_VRF_AF(CvtContext_VRF):
    cmd = "address-family", None

    def remove(self, old, vrf, af):
        return [*self.enter(vrf), " no address-family " + af]

    def add(self, new, vrf, af):
        return [*self.enter(vrf), " address-family " + af]


class CvtContext_VRF_AF(CvtContext_VRF):
    context = "vrf", None, "address-family", None

    def enter(self, vrf, af):
        return [*super().enter(vrf), " address-family " + af]


class Cvt_VRF_AF_RT(CvtContext_VRF_AF):
    cmd = "route-target", None, None

    def truncate(self, old, rem, vrf, af, dir_, rt):
        return [*self.enter(vrf, af), "  no route-target %s %s" % (dir_, rt)]

    def update(self, old, upd, new, vrf, af, dir_, rt):
        return [*self.enter(vrf, af), "  route-target %s %s" % (dir_, rt)]



# the converters are all subclasses of Cvt (DiffConvert) which have the
# 'command' attribute defined
#
# CiscoIOSDiffConfig._add_converters() (below) adds these into the list
# of converter classes

converters = [ c for c in get_all_subclasses(Cvt) if c.cmd is not None ]

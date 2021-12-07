from .types import *


class NetsplashGetInterfaces(NCSInstance):

    _path = "/action/services/netsplash-get-interfaces"

    _nsmap = {
        "action":"urn:ietf:params:xml:ns:yang:1",
        "services":"http://tail-f.com/ns/ncs",
        "netsplash-get-interfaces":"http://umnet.umich.edu/netsplash",
        }

    def __init__(self):

        self.ip_or_name = Choice(['device-hostname','device-ip'])
        self.ip_or_name.device_ip = Leaf(str)
        self.ip_or_name.device_hostname = Leaf(str)

class NetsplashGetSwitchesByZone(NCSInstance):

    _path = "/action/services/netsplash-get-switches-by-zone"

    _nsmap = {
        "action":"urn:ietf:params:xml:ns:yang:1",
        "services":"http://tail-f.com/ns/ncs",
        "netsplash-get-switches-by-zone":"http://umnet.umich.edu/netsplash",
        }

    def __init__(self):

        self.zone = Leaf(str)


class NetsplashUpdateInterfaces(NCSInstance):

    _path = "/action/services/netsplash-update-interfaces"

    _nsmap = {
        "action":"urn:ietf:params:xml:ns:yang:1",
        "services":"http://tail-f.com/ns/ncs",
        "netsplash-update-interfaces":"http://umnet.umich.edu/netsplash",
        }

    def __init__(self):

        self.switch = Leaf(str)
        self.zone = Leaf(str)
        self.switchport = List(NetsplashSwitchport)


class NetsplashSwitchport(Choice):
    
    def __init__(self, choice=None):

        # the choice initializer creates empty containers
        # for 'access' and 'default' for us
        super().__init__(['access','default'])
        
        # now we need to fill in everything else
        self.name = Leaf(str)
        self.access.description = Leaf(str)
        self.access.vlan_name = Leaf(str)
        self.access.admin_status = Leaf(str)
        self.access.voip_enabled = Leaf(bool)

        # can't apply choice until after we've initialized
        # all options!
        if choice:
            self.choose(choice)

class Devices(NCSInstance):

    _path = "/config/devices"

    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "devices":"http://tail-f.com/ns/ncs",
            }

    _xml_munge = {
        r'<ned-id>(.+)</ned-id>':'<ned-id xmlns:\g<1>="http://tail-f.com/ns/ned-id/\g<1>">\g<1></ned-id>'
    }

    def __init__(self):
        self.device = List(Device)

class Device(NCSInstance):

    _path = "/config/devices/device"

    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "devices":"http://tail-f.com/ns/ncs",
            }

    _xml_munge = {
        r'<ned-id>(.+)</ned-id>':'<ned-id xmlns:\g<1>="http://tail-f.com/ns/ned-id/\g<1>">\g<1></ned-id>'
    }

    def __init__(self):

        self.name = Leaf(str)
        self.address = Leaf(str)
        self.authgroup = Leaf(str, value="default")
        self.state = Container()
        self.state.admin_state = Leaf(str, value="unlocked")
        self.device_type = Choice(['cli','netconf'])
        self.device_type.cli = Container()
        self.device_type.netconf = Container()
        self.device_type.cli.ned_id = Leaf(str)
        self.device_type.netconf.ned_id = Leaf(str)
        self.in_band_mgmt = Container()
        self.in_band_mgmt.set_ns("http://umnet.umich.edu/umnetcommon")
        self.in_band_mgmt.ip_address = Leaf(str)
        self.in_band_mgmt.interface = Leaf(str)



class Switchport(Container):

    def __init__(self):

        self.enabled = Leaf(bool)
        self.description = Leaf(str)
        self.mode = Container()

        self.mode.mode_choice = Choice(['access','trunk'])
        self.mode.mode_choice.access.vlan = Leaf(int)
        self.mode.mode_choice.access.voip_enabled = Leaf(bool, value=False)
        self.mode.mode_choice.trunk = Container()
        self.mode.mode_choice.trunk.native_vlan_id = Leaf(int, value=1000)
        self.mode.mode_choice.trunk.vlan_list = LeafList(int)

class Network(NCSInstance):

    _path = "/config/services/network"
    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "services":"http://tail-f.com/ns/ncs",
            "network":"http://example.com/umnet-network",
            }

    def __init__(self):

        self.name = Leaf(str)
        self.role = Leaf(str)
        self.description = Leaf(str)
        self.layer2 = Container()
        self.layer2.vlan_id = Leaf(int)

        self.layer3 = Container()
        self.layer3.vrf = Leaf(str)
        self.layer3.primary_ipv4_subnet = Leaf(str)
        self.layer3.secondary_ipv4_subnets = LeafList(str)
        self.layer3.ipv6_subnet = LeafList(str)
        self.layer3.ingress_acl = Leaf(str)
        self.layer3.egress_acl = Leaf(str)


class Networks(NCSInstance):

    _path = "/config/services"
    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "services":"http://tail-f.com/ns/ncs",
            }

    def __init__(self):

        self.network = List(Network)
        self.network.set_ns("http://example.com/umnet-network")

class NGFWVsys(NCSInstance):

    _path = "/config/services/ngfw-vsys"
    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "services":"http://tail-f.com/ns/ncs",
            "ngfw-vsys":"http://umnet.umich.edu/umnet-vrf",
            }

        
class Vrf(Container):

    def __init__(self):

        self.name = Leaf('str')
        self.ngfw_vsys_or_vrf_asn = Choice(['ngfw-vsys', 'vrf-asn'])
        self.ngfw_vsys_or_vrf_asn.ngfw_vsys = Leaf(str)
        self.ngfw_vsys_or_vrf_asn.vrf_asn = Leaf(int)

        self.vrf_no = Leaf(int)

class Vrfs(NCSInstance):

    _path = "/config/services/vrf"
    _nsmap = {
            "config":"http://tail-f.com/ns/config/1.0",
            "services":"http://tail-f.com/ns/ncs",
            "vrf":"http://umnet.umich.edu/umnet-vrf",
            }

    def __init__(self):
        self.vrf = List(Vrf) 

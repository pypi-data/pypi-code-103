"""
Our KVM solution, clulstered and self hosted
"""
import json
from argparse import ArgumentParser
from .lib.exceptions import RequirementError, NamespaceError, NamespaceNotFound, UnsupportedHardware, InterfaceNotFound, ResourceNotFound, ResourceError
from .storage import storage
from .lib.dupedict import DupeDict, JSON

__author__ = 'Anton Hvornum'
__version__ = '0.0.6'
__description__ = "Our KVM solution, clulstered and self hosted"

# Parse arguments early, so that following imports can
# gain access to the arguments without parsing on their own.
parser = ArgumentParser()
# API arguments
parser.add_argument("--api", default=False, action="store_true", help="Enable API functionality")
parser.add_argument("--auth-server", default="127.0.0.1", nargs="?", help="Which authentication server to use", type=str)
parser.add_argument("--auth-realm", default="home", nargs="?", help="Which authentication realm to use", type=str)
parser.add_argument("--auth-schema", default="Keycloak", nargs="?", help="Which authentication realm to use", type=str)

# Cluster arguments
parser.add_argument("--cluster", default=False, action="store_true", help="Enable API functionality")
parser.add_argument("--cluster-nodes", default="[]", nargs="?", help="A JSON list of known nodes (node sharing will occur, so one is minimum to enable) using the format: [{\"ip\": port}, {\"ip\": port}]", type=str)

# KVM helper arguments for creating machines
parser.add_argument("--machine-name", default="", nargs="?", help="Creates a new virtual machine with the given name", type=str)
parser.add_argument("--cpu", default="host", nargs="?", help="Which CPU type/parameters to give the new machine", type=str)
parser.add_argument("--bios", default=False, action="store_true", help="Disables UEFI and enables legacy BIOS for the machine")
parser.add_argument("--memory", default=8192, nargs="?", help="Defines the amount of memory to allocate to the new machine", type=str)
parser.add_argument("--harddrives", default=None, nargs="?", help="A comma-separated list of harddrives using the format 'image.qcow2:10G[,image2.qcow2:40G]'", type=str)
parser.add_argument("--cdroms", default=None, nargs="?", help="A comma-separated list of ISO/cdrom images using the format 'image.iso[,image2.iso]'", type=str)
parser.add_argument("--no-namespace", default=False, action="store_true", help="This will disable namespace-creation for the machine and by default for network intrastructure")
parser.add_argument("--graphics", default=False, action="store_true", help="This will turn on default graphics output (gtk) for qemu, the oposit of headless (default)")
parser.add_argument("--serial", default=False, action="store_true", help="This will turn on serial console graphics (will override --graphics if used together)")
parser.add_argument("--namespace", default=None, nargs="?", help="Defaults to using the machine name", type=str)
parser.add_argument("--network", default=None, nargs="?", help="Defaults to using NAT. The syntax is a bit complex, refer to the man pages for information.", type=str)
parser.add_argument("--uefi-vars", default='/usr/share/ovmf/x64/OVMF_VARS.fd', nargs="?", help="Defines the path to the EFI variables (defaults to using find -iname for the vars)", type=str)
parser.add_argument("--uefi-code", default='/usr/share/ovmf/x64/OVMF_CODE.fd', nargs="?", help="Defines the path to the EFI code (defaults to using find -iname for the code)", type=str)
parser.add_argument("--service", default=None, nargs="?", help="Tells ourkvm to create a service script for the newly created machine at the given location. For instance --service ./machine.service", type=str)
parser.add_argument("--config", default='/etc/qemu.d', nargs="?", help="Tells ourkvm where to store the environment configuration for the newly created machine. Default is /etc/qemu.d/", type=str)
parser.add_argument("--force", default=False, action="store_true", help="Will overwrite any existing service file or images")
parser.add_argument("--stop", default=False, action="store_true", help="Will gracefully stop the given machine if it's running (a helper flag for usage with systemd)")

# Store the arguments in a "global" storage variable
args, unknowns = parser.parse_known_args()
storage['arguments'] = args
storage['arguments'].cluster_nodes = json.loads(storage['arguments'].cluster_nodes)

# Expose API calls for when the user does `import ourkvm`:
if args.api:
	from .lib.api import app, User, get_current_user, read_current_user, list_all_clusters

from .lib.logger import log
from .lib.syscalls import SysCommand, SysCommandWorker
from .lib.networking import load_network_info, get_interface_info, get_namespace_info, del_namespace, add_namespace, ip
from .lib.qemu import qemu, qemu_img, create_qemu_string, verify_qemu_resources, write_qemu_service_file
from .lib.environment import load_environment, dismantle_environment

# --dluster-nodes implicitly enables --cluster
if storage['arguments'].cluster_nodes:
	args.cluster = True

if args.cluster:
	from .lib.cluster import ClusterServer
	handle = ClusterServer()
	while handle.poll() is True:
		pass
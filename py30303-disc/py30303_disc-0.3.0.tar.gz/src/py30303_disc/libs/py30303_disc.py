"""
py30303_disc library

Contains:
    - d30303
    - run_d30303_discovery
"""
import asyncio
import logging
import socket
from collections import deque

DTYPE_BASIC_30303 = "basic_30303"
DTYPE_SIMPLE_30303 = "simple_30303"
DTYPE_WIZNET = "wiznet"
DTYPE_ECOWITT = "ecowitt"


class run_d30303_discovery:
    """Discovery oneshot class."""
    def __init__(self, server, loop, timeout=5, d_type=DTYPE_BASIC_30303,
                 host_match=None, mac_prefix=None):
        """Initialize the discovery."""
        self.server = server
        self.loop = loop
        self.timeout = timeout
        self.d_type = d_type
        self.host_match = host_match
        self.mac_prefix = mac_prefix
        self.devices = []
        self.discovery_finished = False
        # Subscribe for incoming udp packet event
        self.server.subscribe(self.on_datagram_received)
        asyncio.ensure_future(self.do_send(), loop=self.loop)

    async def on_datagram_received(self, data, addr):
        self.devices.append(
            self.server.discovery_map[self.d_type]["parser"](
                data,
                addr,
                mac_prefix=self.mac_prefix,
                hostname=self.host_match))
        
    async def do_send(self):
        self.server.send_discovery(self.d_type)
        await asyncio.sleep(self.timeout)
        self.server.end_discovery()
        self.discovery_finished = True

    async def get_found_devices(self):
        while not self.discovery_finished:
            await asyncio.sleep(1)

        return self.devices


class d30303:
    """Documentation of d30303."""
    
    def __init__(self):
        """Initiatlizes d30303 class."""
        self.log = logging.getLogger(__name__)

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._sock.setblocking(False)

        self._send_event = asyncio.Event()
        self._send_queue = deque()

        self._subscribers = {}

        self.discovery_map = {
            DTYPE_BASIC_30303: {
                "send_port": 30303,
                "msg": bytes("Discovery: Who is out there?", 'utf-8'),
                "parser": self.d30303_parse,
                "bind_port": 0,
            }, DTYPE_SIMPLE_30303: {
                "send_port": 30303,
                "msg": bytes("D", 'utf-8'),
                "parser": self.d30303_parse,
                "bind_port": 0,
            }, DTYPE_WIZNET: {
                "send_port": 1460,  # 5001 ?
                "msg": bytes("FIND", 'utf-8'),
                "parser": self.wiznet_parse,
                "bind_port": 5001,
            }, DTYPE_ECOWITT: {
                "send_port": 46000,
                "msg": bytes([0xFF, 0xFF, 0x12, 0x03, 0x15]),
                "parser": self.ecowitt_parse,
                "bind_port": 59387,
            }
        }

    def end_discovery(self):
        """End the discovery."""
        self.log.debug("Closing socket and ending discovery.")
        self._sock.close()
        
    def bind_d30303_recv(self, loop, d_type=DTYPE_BASIC_30303):
        """Bind to a port to recieve replies."""

        self.loop = loop
        
        self._sock.bind(('', self.discovery_map[d_type]["bind_port"]))
        addr, port = self._sock.getsockname()
        self.log.info("Listening on port %d:udp for discovery events", port)

        self._connection_made()

        self._run_future(self._send_periodically(), self._recv_periodically())

    def subscribe(self, fut):
        """Subscribe to be notified on discovery."""
        self._subscribers[id(fut)] = fut

    def unsubscribe(self, fut):
        """Unsubscribe from notifications."""
        self._subscribers.pop(id(fut), None)

    def send_discovery(self, msg_type=DTYPE_BASIC_30303):
        """Initiate a 30303 discovery of type X."""
        self.log.debug("Initiating type %s discovery.", msg_type)
        self._send_queue.append((
            self.discovery_map[msg_type]["msg"],
            ('<broadcast>', self.discovery_map[msg_type]["send_port"])))
        self._send_event.set()

    def _run_future(self, *args):
        """Kick it off."""
        for fut in args:
            asyncio.ensure_future(fut, loop=self.loop)

    def _sock_recv(self, fut=None, registered=False):
        """Recieve data on the listen socket."""
        fd = self._sock.fileno()

        if fut is None:
            fut = self.loop.create_future()

        if registered:
            self.loop.remove_reader(fd)

        try:
            data, addr = self._sock.recvfrom(1024)
        except (BlockingIOError, InterruptedError):
            self.loop.add_reader(fd, self._sock_recv, fut, True)
        except Exception as e:
            fut.set_exception(e)
            self._socket_error(e)
        else:
            fut.set_result((data, addr))

        return fut

    def _sock_send(self, data, addr, fut=None, registered=False):
        """Send data to the broadcast addr."""
        fd = self._sock.fileno()

        if fut is None:
            fut = self.loop.create_future()

        if registered:
            self.loop.remove_writer(fd)

        if not data:
            return

        try:
            bytes_sent = self._sock.sendto(data, addr)
        except (BlockingIOError, InterruptedError):
            self.loop.add_writer(fd, self._sock_send, data, addr, fut, True)
        except Exception as e:
            fut.set_exception(e)
            self._socket_error(e)
        else:
            fut.set_result(bytes_sent)

        return fut

    async def _send_periodically(self):
        """If we have data, send it."""
        while True:
            await self._send_event.wait()
            try:
                while self._send_queue:
                    data, addr = self._send_queue.popleft()
                    await self._sock_send(data, addr)
            finally:
                self._send_event.clear()

    async def _recv_periodically(self):
        """Check for new data, get it."""
        while True:
            data, addr = await self._sock_recv()
            self.log.debug("Got Data: %s", data)
            self.log.debug("From ADDR: %s", addr)
            self._notify_subscribers(*self._datagram_received(data, addr))

    def _connection_made(self):
        pass

    def _socket_error(self, e):
        pass

    def _datagram_received(self, data, addr):
        """Internal: Got some data."""
        return data, addr

    def _notify_subscribers(self, data, addr):
        self._run_future(
            *(fut(data, addr) for fut in self._subscribers.values()))

    def d30303_parse(self, data, addr, mac_prefix=None, hostname=None):
        """Parse a d30303 message.

        Returns a dict of ip, hostname, macaddr
        Hostname is as reported by device, not DNS
        macaddr is in the form XX-XX-XX-XX-XX-XX
        """

        ip_addr = addr[0]
        data_string = data.decode("utf-8").split('\r\n')
        self.log.info("Hostname: %s", data_string[0])

        message = {"ip_addr": ip_addr,
                   "hostname": data_string[0].strip(),
                   "mac_addr": data_string[1]}
        
        if mac_prefix is None and hostname is None:
            return message

        if mac_prefix is not None:
            if data_string[1].startswith(mac_prefix):
                if hostname is not None:
                    if hostname == data_string[0]:
                        return message
                    return None
                return message
            return None

        if hostname is not None:
            if hostname == data_string[0]:
                return message
            return None
        return None

    def wiznet_parse(self, data, addr, mac_prefix=None, hostname=None):
        """Parse a wiznet message."""

        # Does not have a hostname function
        # first 4 bytes are IWIN

        ip_addr = addr[0]
        mac = data[4:10].hex().upper()
        mac_addr = '-'.join(mac[i:i + 2] for i in range(0, len(mac), 2))
        op = data[10]
        rport = int.from_bytes(data[29:31], byteorder='big')
        
        message = {"ip_addr": ip_addr, "mac_addr": mac_addr,
                   "op_mode": op, "remote_port": rport}

        if mac_prefix is None:
            return message

        if mac_prefix is not None:
            if mac_addr.startswith(mac_prefix):
                return message

        return None

    def ecowitt_parse(self, data, addr, mac_prefix=None, hostname=None):
        """Parse an ecowitt message."""

        # first 5 bytes are FF-FF-12-00-2C (CMD)

        ip_addr = addr[0]
        mac = data[5:11].hex().upper()
        mac_addr = '-'.join(mac[i:i + 2] for i in range(0, len(mac), 2))
        # ip 11:15
        # port 15:16
        port = int.from_bytes(data[15:17], byteorder='big')
        ssid = data[18:-1].decode('utf-8')

        message = {"ip_addr": ip_addr, "mac_addr": mac_addr,
                   "port": port, "ssid": ssid}

        if mac_prefix is None and hostname is None:
            return message

        if mac_prefix is not None:
            if mac_addr.startswith(mac_prefix):
                if hostname is not None:
                    if hostname.startswith(ssid):
                        return message
                    return None
                return message
            return None

        if hostname is not None:
            if hostname.startswith(ssid):
                return message
            return None
        return None

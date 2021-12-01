import os

class ClientSSHInfo():
    def __init__(self, ip, port, server_ip, server_port):
        self.ip = ip
        self.port = port
        self.server_ip = server_ip
        self.server_port = server_port

    def to_dict(self) -> dict:
        return {
            'client_ip': self.ip,
            'client_port': self.port,
            'server_ip': self.server_ip,
            'server_port': self.server_port
        }

def get_ssh_info() -> ClientSSHInfo:
    info = os.getenv('SSH_CONNECTION', None)
    if info is None:
        raise Exception('No SSH session found')
    client_ip, client_port, server_ip, server_port = info.split(' ')
    return ClientSSHInfo(client_ip, client_port, server_ip, server_port)
import cryptography.fernet
import dict_tools.utils
import msgpack


def generate_key(hub):
    return cryptography.fernet.Fernet.generate_key().decode()


def encrypt(hub, data, key):
    fernet = cryptography.fernet.Fernet(key)
    raw = msgpack.dumps(data)
    return fernet.encrypt(raw)


def decrypt(hub, data, key):
    fernet = cryptography.fernet.Fernet(key)
    raw = fernet.decrypt(data)
    serialized = msgpack.loads(raw)
    decoded = dict_tools.utils.decode_dict(serialized)
    return decoded

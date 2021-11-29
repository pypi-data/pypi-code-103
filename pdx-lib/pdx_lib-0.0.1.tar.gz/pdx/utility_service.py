from pdx import Console
from pdx import Session
from pdx import Encryptor
import socket
import datetime
import os

out = Console.get()


def is_on_psu_network(require_twelve_subnet=False):
    """Is this computer on the PSU network (or VPN)?"""
    ip = get_ip_address()

    # Return True/False based on IP address
    if ip is None:
        return False
    elif require_twelve_subnet:
        return ip.startswith('131.252.12.')

    else:
        return ip.startswith('131.252.')


def get_ip_address():
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ss.connect(("8.8.8.8", 80))
        ip = ss.getsockname()[0]
        ss.close()
        del ss
        return ip
    except Exception as ee:
        Console.get().put_error(ee)


def max_length_in_list(given_list):
    """Return the length of the longest string in the list"""
    Console.get().trace('max_length_in_list', ["List with {0} items".format(len(given_list) if given_list is not None else 0)])

    max_length = 0

    if given_list is not None:
        for item in given_list:
            length = len(str(item))
            max_length = length if length > max_length else max_length

    return max_length


def get_timestamp_string():
    """Get the standard-format timestamp string used for backup tables and branches"""
    return '{:%Y%m%d%H%M%S}'.format(datetime.datetime.now())


def get_encrypted_content(content_name, prompt_text):
    value = read_encrypted_file(content_name)
    if value is None:
        value = out.prompt_secret(prompt_text)
        if value is not None:
            # Encrypt and save
            write_encrypted_file(content_name, value)
    return value


def read_encrypted_file(file_name):
    """Get something from an encrypted file, if present"""
    file_path = os.path.join(Session.pdx_home, 'config', Encryptor.getHash(file_name) + '.dat')
    if os.path.exists(file_path):
        return Encryptor.Encryptor().decrypt_from_file(file_path)
    else:
        return None


def write_encrypted_file(file_name, content):
    """Save something to an encrypted file"""
    file_path = os.path.join(Session.pdx_home, 'config', Encryptor.getHash(file_name) + '.dat')
    return Encryptor.Encryptor().encrypt_to_file(content, file_path)


def remove_encrypted_file(file_name):
    file_path = os.path.join(Session.pdx_home, 'config', Encryptor.getHash(file_name) + '.dat')
    if os.path.exists(file_path):
        os.unlink(file_path)


# Functions for working with encrypted pw
def get_odin_pw(save_response=True):
    # Get Odin password (used with BitBucket APIs, and more in the future)
    odin_file_path = os.path.join(Session.pdx_home, 'config', Encryptor.getHash(f"odin-{Session.username}") + '.dat')
    password = read_encrypted_file(odin_file_path)
    if password is None:
        password = out.prompt_secret("BitBucket password for {0}".format(Session.username))
        if save_response and password is not None:
            # Encrypt and save for future API calls
            write_encrypted_file(odin_file_path, password)

    return password

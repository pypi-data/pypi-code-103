from pathlib import Path

from aos_keys.actions import new_token_user, UserType
from aos_prov.actions import create_new_unit
import random


def do_oem_user(domain: str, user_token: str):
    try:
        new_token_user(domain, str(Path.home() / '.aos' / 'security'), user_token, UserType.OEM.value, False)
    except Exception:
        print('User certificate already exists... skipping')
    vm_name = 'My first Aos Unit'
    if (Path.home() / '.aos' / 'virtual-units' / vm_name).exists():
        vm_name = vm_name + ' ' + str(random.randint(100, 999))
    create_new_unit(vm_name, do_provision=True)

    print('First unit successfully created')

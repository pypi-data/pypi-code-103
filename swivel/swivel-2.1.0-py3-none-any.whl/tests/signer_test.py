import pytest
from py_eth_sig_utils.signing import recover_typed_data, signature_to_v_r_s
from swivel.constants import DOMAIN_NAME, DOMAIN_VERSION, HEX_PREFIX

@pytest.fixture(scope='module')
def key(vendor):
    return vendor.instance.toBytes(hexstr='0xfb28b03032bbb105e1199e496b23a6435a077375cbea9c6c4998b971a672873c')

@pytest.fixture(scope='module')
def order(key):
    return {
        'key': key,
        'maker': '0x7111F9Aeb2C1b9344EC274780dc9e3806bdc60Ef',
        'underlying': '0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa',
        'vault': False,
        'exit': False,
        'principal': 1000,
        'premium': 60,
        'maturity': 1655255622,
        'expiry': 1625173101,
    }

def test_prepare_data(vendor):
    data = vendor.signer.prepare_data()
    assert len(data['types']['EIP712Domain']) == 4
    assert len(data['types']['Order']) == 9
    assert data['primaryType'] == 'Order'

def test_prepare_domain(vendor):
    data = vendor.signer.prepare_data()
    vendor.signer.prepare_domain(data, 4, '0xSp1M3gG5')
    assert data['domain']['name'] == DOMAIN_NAME
    assert data['domain']['version'] == DOMAIN_VERSION
    assert data['domain']['chainId'] == 4
    assert data['domain']['verifyingContract'] == '0xSp1M3gG5'
    # peek at the others to see if they are there...
    assert len(data['types']['Order']) == 9

def test_prepare_message(vendor):
    data = vendor.signer.prepare_data()
    key = '0xK3y123'
    principal = '1000000000000000'
    order = { 'key': key, 'vault': True, 'exit': False, 'principal': principal }
    vendor.signer.prepare_message(data, order)
    assert data['message']['key'] == key
    assert data['message']['vault'] == True
    assert data['message']['exit'] == False
    assert data['message']['principal'] == principal
    # peek at the others to see if they are there...
    assert len(data['types']['EIP712Domain']) == 4

def test_sign_order(vendor, order):
    verifier = '0x25b71690A99A692707f6F4933A76a58ECDD0b9Ac'
    sig = vendor.sign_order(order, 4, verifier)
    assert len(sig) > 0
    assert sig.startswith(HEX_PREFIX)

    # recover it
    data = vendor.signer.prepare_data()
    vendor.signer.prepare_message(data, order)
    vendor.signer.prepare_domain(data, 4, verifier)
    sig_bytes = vendor.instance.toBytes(hexstr=sig)
    address = recover_typed_data(data, *signature_to_v_r_s(sig_bytes))
    assert address == order['maker']


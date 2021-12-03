import pytest
from swivel.contracts.bin import VAULT_TRACKER
from swivel.helpers import call
from swivel.contracts import VaultTracker
from swivel.mocks.bin import CERC20
from swivel.mocks import CErc20

@pytest.fixture(scope='module')
def c_token(vendor):
    cerc20 = CErc20(vendor)
    deployed = vendor.instance.eth.contract(abi=cerc20.abi, bytecode=CERC20)
    tx_hash = deployed.constructor().transact({ 'from': vendor.account })
    tx_rcpt = vendor.instance.eth.wait_for_transaction_receipt(tx_hash)
    cerc20.at(tx_rcpt['contractAddress'])
    return cerc20

@pytest.fixture(scope='module')
def vault_tracker(vendor, c_token):
    # the HOC has it's abi available
    tracker = VaultTracker(vendor)
    # our W3 vendor .contract method is not for deployment, use the primitive here
    deployed = vendor.instance.eth.contract(abi=tracker.abi, bytecode=VAULT_TRACKER)

    # web3 will complain about a non-checksum address like the ctoken...
    # c_token_addr = vendor.instance.toChecksumAddress('0x6d7f0754ffeb405d23c51ce938289d4835be3b14')

    tx_hash = deployed.constructor(123456789, c_token.address, '0x8e7bFA3106c0544b6468833c0EB41c350b50A5CA').transact({ 'from': vendor.account })
    tx_rcpt = vendor.instance.eth.wait_for_transaction_receipt(tx_hash)
    tracker.at(tx_rcpt['contractAddress'])
    return tracker

@pytest.fixture
def vault():
    return { 'notional': 1000, 'redeemable': 500, 'exchangeRate': 10 }

def test_admin(vault_tracker):
    addr = call(vault_tracker.admin())
    # the vendor will normalize .account...
    assert addr == vault_tracker.vendor.account

def test_c_token_addr(vault_tracker, c_token):
    addr = call(vault_tracker.c_token_address())
    # assert addr == vault_tracker.vendor.instance.toChecksumAddress('0x6d7f0754ffeb405d23c51ce938289d4835be3b14')
    assert addr == c_token.address

def test_swivel_addr(vault_tracker):
    addr = call(vault_tracker.swivel())
    assert addr == '0x8e7bFA3106c0544b6468833c0EB41c350b50A5CA'

def test_maturity(vault_tracker):
    mty = call(vault_tracker.maturity())
    assert mty == 123456789

def test_maturity_rate(vault_tracker):
    rate = call(vault_tracker.maturity_rate())
    assert rate == 0

def test_vaults(vault_tracker, vault):
    called, opts = vault_tracker.vaults('0xG1mM3mYVaU1t')

    assert callable(called)
    assert opts == None

def test_balances_of(vault_tracker, vault):
    called, opts = vault_tracker.balances_of('0xG1mM3mYBa1anC35')

    assert callable(called)
    assert opts == None

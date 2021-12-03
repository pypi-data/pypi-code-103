import os
import pytest
import logging
from web3 import Web3, EthereumTesterProvider
from eth_tester import PyEVMBackend, EthereumTester
from swivel.vendors import W3
from swivel.contracts.bin import MARKET_PLACE, SWIVEL
from swivel.helpers import transact
from swivel.contracts import MarketPlace, Swivel

@pytest.fixture(scope='module')
def logger():
    return logging.getLogger(__name__)

@pytest.fixture(scope='module')
def eth_tester():
    override = {'gas_limit': 6700000}
    params = PyEVMBackend._generate_genesis_params(overrides=override)
    backend = PyEVMBackend(params)
    return EthereumTester(backend)

@pytest.fixture(scope='module')
def provider(eth_tester):
    return EthereumTesterProvider(eth_tester)

@pytest.fixture(scope='module')
def vendor(provider):
    return W3(provider)

@pytest.fixture(scope='module')
def market_place(vendor):
    # the HOC has it's abi available
    m_place = MarketPlace(vendor)
    # our W3 vendor .contract method is not for deployment, use the primitive here
    deployed = vendor.instance.eth.contract(abi=m_place.abi, bytecode=MARKET_PLACE)
    # market place needs much gas to deploy...
    tx_opts = { 'from': vendor.account, 'gas': 6000000 }
    tx_hash = deployed.constructor().transact(tx_opts)
    tx_rcpt = vendor.instance.eth.wait_for_transaction_receipt(tx_hash)
    m_place.at(tx_rcpt['contractAddress'])
    # NOTE that the swivel address is not set as of yet...
    return m_place

@pytest.fixture(scope='module')
def swivel(vendor, market_place):
    swiv = Swivel(vendor)
    deployed = vendor.instance.eth.contract(abi=swiv.abi, bytecode=SWIVEL)
    # likely does not need 6M, but doesn't matter...
    tx_opts = {'from': vendor.account, 'gas': 6000000 }
    tx_hash = deployed.constructor(market_place.address).transact(tx_opts)
    tx_rcpt = vendor.instance.eth.wait_for_transaction_receipt(tx_hash)
    swiv.at(tx_rcpt['contractAddress'])
    return swiv

@pytest.fixture(scope='module')
def market_place_with_swivel(market_place, swivel):
    tx_hash = transact(market_place.set_swivel_address(swivel.address))
    vendor.instance.eth.wait_for_transaction_receipt(tx_hash)
    return market_place

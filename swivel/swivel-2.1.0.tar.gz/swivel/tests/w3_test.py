import pytest

def test_account(vendor):
    assert len(vendor.account) == 42
    # the fixture does not pass an account, so it should be accounts[0]
    assert vendor.account == vendor.instance.eth.accounts[0]

def test_estimate_gas(vendor, swivel):
    args = swivel.split_underlying('0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa',
        1234567890, 1000, opts={ 'gas': 25000, 'chainId': 1 })

    gas, price = vendor.estimate_gas(args)

    assert gas != None
    assert price != None

def test_build_transaction(vendor, swivel):
    # build up the tx, opts args first
    args = swivel.split_underlying('0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa',
        1234567890, 1000, opts={ 'gas': 25000, 'chainId': 1 })
    
    built = vendor.build_transaction(args)
    # as long as 'data' is present we'll assume success
    assert len(built['data']) > 0

def test_sign_transaction(vendor, swivel):
    # we need to include from in this one or the random accounts[0] will cause it to fail...
    args = swivel.split_underlying('0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa',
        1234567890, 1000, opts={ 'from': '0x7111F9Aeb2C1b9344EC274780dc9e3806bdc60Ef', 'gas': 25000, 'chainId': 1 })
    
    built = vendor.build_transaction(args)
    signed = vendor.sign_transaction(built)

    assert signed != None

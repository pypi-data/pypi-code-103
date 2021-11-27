#!/usr/bin/env python
# coding: utf-8
from tronpytool import Tron
from tronpytool.common.account import Address

address = 'TB54izbgpde54ZmY6F6aFWxSNwtQ9yWvYd'
private_key = 'b2aa4c066a139e770c7c9faf1b8acad04f86adb90feedaef3ef7e255261abec9'
tx = "76354771dd34bd9dce1787b2f8ef23c724629462719b51da234404f904594dee"
tron = Tron().setNetwork("nile")

tron.private_key = private_key
tron.default_address = address
newky = dict(
    Base58='TDGdS7grJ9da3qdqZXvCGjvQo8B9MEcvWx',
    Hex='412433d7f134eceffe1dbc218422f57c7f06cce66a'
)
go = Address().to_hex(address)
contract_address = Address().from_hex("4170a49feb57515f5ac758933409b6b75dda43fcfa")
print("to hex address:{}".format(go))
#TR3TEXGWZvY5DZryrQx6bkmCK6whBr7SE4
print("contract address:{}".format(contract_address))

sample_meta = dict(
    {'contract_address': 'TLEotsGxyfFyVUcjWw2PPgKkz7YM7fsE4K', 'function_selector': 'name()',
     'issuer_address': dict(
         {'hex': '41A5576E55542477CE999F2D3A8C242697B0FCF416', 'base58': 'TR3TEXGWZvY5DZryrQx6bkmCK6whBr7SE4'}),
     'fee_limit': 30000,
     'call_value': 0
     }
)

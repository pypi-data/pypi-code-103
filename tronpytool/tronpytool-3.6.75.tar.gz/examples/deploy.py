#!/usr/bin/env python
# coding: utf-8
from tronpytool import Tron

tron = Tron().setNetwork('nile')

tron.private_key = 'private_key'
tron.default_address = 'default address'

deployed_contract_address = 'TrxOnchainContractAddress'

interact_contract = tron.Chain.contract(address=deployed_contract_address, abi=_abi, bytecode=_bytecode)

# create transaction
create_tx = tron.transaction_builder.send_transaction('to', 1, 'from')

# offline sign
offline_sign = tron.Chain.sign(create_tx)

# online sign (Not recommended)
online_sign = tron.Chain.online_sign(create_tx)

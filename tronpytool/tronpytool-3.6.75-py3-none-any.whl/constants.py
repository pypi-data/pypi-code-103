#!/usr/bin/env python
# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

# Here you can specify links to sites of different types.
# The default is verified links.
# If you do not know what links are used for, it is recommended not to change

from .providers.http import HttpProvider

DEFAULT_NODES = {
    "full_node": "https://api.trongrid.io",
    "solidity_node": "https://api.trongrid.io",
    "event_server": "https://api.trongrid.io"
}

CONF_MAINNET = {
    "full_node": "https://api.trongrid.io",
    "event_server": "https://api.trongrid.io",
    "solidity_node": "https://api.trongrid.io",
}

# The long running, maintained by the tron-us community
CONF_SHASTA = {
    "full_node": "https://api.shasta.trongrid.io",
    "event_server": "https://api.shasta.trongrid.io",
    "solidity_node": "https://api.shasta.trongrid.io",
    "faucet": "https://www.trongrid.io/faucet",
}

# Maintained by the official team
CONF_NILE = {
    "full_node": "https://api.nileex.io",
    "event_server": "https://event.nileex.io",
    "solidity_node": "https://api.nileex.io",
    "faucet": "http://nileex.io/join/getJoinPage",
}

# Maintained by the official team
CONF_TRONEX = {
    "full_node": "https://testhttpapi.tronex.io",
    "event_server": "https://testapi.tronex.io",
    "solidity_node": "https://testapi.tronex.io",
    "faucet": "http://testnet.tronex.io/join/getJoinPage",
}

ALL = {
    "default": CONF_MAINNET,
    "mainnet": CONF_MAINNET,
    "nile": CONF_NILE,
    "shasta": CONF_SHASTA,
    "tronex": CONF_TRONEX
}


class Bolors:
    OK = '\033[92m'  # GREEN
    WARNING = '\033[93m'  # YELLOW
    FAIL = '\033[91m'  # RED
    RESET = '\033[0m'  # RESET COLOR


# EVM history: https://en.wikipedia.org/wiki/Ethereum
class Evm:
    TANGERINEWHISTLE = "tangerineWhistle"
    """
    18 October 2016
    Gas cost for access to other accounts increased, relevant for gas estimation and the optimizer.
    All gas sent by default for external calls, previously a certain amount had to be retained.
    """
    SPURIOUSDRAGON = "spuriousDragon"
    """
    23 November 2016
    Gas cost for the exp opcode increased, relevant for gas estimation and the optimizer.
    """
    BYZANTIUM = "byzantium"
    """
    16 October 2017
    Opcodes `returndatacopy`, `returndatasize` and `staticcall` are available in assembly.
    The `staticcall` opcode is used when calling non-library view or pure functions, which prevents the functions from modifying state at the EVM level, i.e., even applies when you use invalid type conversions.
    It is possible to access dynamic data returned from function calls.
    revert opcode introduced, which means that `revert()` will not waste gas.
    """
    CONSTANTINOPLE = "constantinople"
    """
    28 February 2019
    Opcodes `create2`, `extcodehash`, `shl`, `shr` and `sar` are available in assembly.
    Shifting operators use shifting opcodes and thus need less gas.
    """
    PETERSBURG = "petersburg"
    """
    28 February 2019
    The compiler behaves the same way as with constantinople.
    """
    ISTANBUL = "istanbul"
    """
    8 December 2019
    Opcodes `chainid` and `selfbalance` are available in assembly.
    """
    BERLIN = "berlin"
    """
    15 April 2021
    Gas costs for `SLOAD`, `*CALL`, `BALANCE`, `EXT*` and `SELFDESTRUCT` increased. The compiler assumes cold gas costs for such operations. This is relevant for gas estimation and the optimizer.
    """
    LONDON = "london"
    """
    5 August 2021
    The block’s base fee (EIP-3198 and EIP-1559) can be accessed via the global block.basefee or basefee() in inline assembly.
    """


def conf_for_name(name: str) -> dict:
    return ALL.get(name, None)


def to_providers_set(d: dict) -> dict:
    return dict(
        full_node=HttpProvider(d["full_node"]),
        solidity_node=HttpProvider(d["solidity_node"]),
        event_server=HttpProvider(d["event_server"])
    )

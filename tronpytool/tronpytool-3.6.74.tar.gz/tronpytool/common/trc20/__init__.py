#!/usr/bin/env python
# coding: utf-8

"""Generated wrapper for TokenLv Solidity contract."""

# pylint: disable=too-many-arguments
import json

from tronpytool import Tron
from tronpytool.compile.basecore import ContractMethod, Validator, EventTracker
from tronpytool.contract import Contract

# Try to import a custom validator class definition; if there isn't one,
# declare one that we can instantiate for the default argument to the
# constructor for TokenLv below.
try:
    # both mypy and pylint complain about what we're doing here, but this
    # works just fine, so their messages have been disabled here.
    from . import (  # type: ignore # pylint: disable=import-self
        TokenLvValidator,
    )
except ImportError:

    class TokenLvValidator(  # type: ignore
        Validator
    ):
        """No-op input validator."""

try:
    from .middleware import MIDDLEWARE  # type: ignore
except ImportError:
    pass


class AddMinterMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the addMinter method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str, validator: Validator = None):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address, validator)

    def call(self, account: str) -> None:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters
        :returns: the return value of the underlying method.
        ()
        """
        super().__call__(account)

    def send_call(self, account: str, trx=0, fee=900000, debug=False) -> None:
        """Execute underlying contract method via eth_sendTransaction.

        :param tx_params: transaction parameters
        """
        super().setContractFee(fee).setContractDebug(debug).sendTrx(trx)
        return self.call(account)

    def validate_and_normalize_inputs(self, account: str):
        """Validate the inputs to the addMinter method."""
        self.validator.assert_valid(
            method_name='addMinter',
            parameter_name='account',
            argument_value=account,
        )
        account = self.validate_and_checksum_address(account)
        return (account)


class AllowanceMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the allowance method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str, validator: Validator = None):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address, validator)

    def call(self, owner: str, spender: str) -> int:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters

        """
        returned = super().__call__(owner, spender)

        return returned

    def validate_and_normalize_inputs(self, owner: str, spender: str):
        """Validate the inputs to the allowance method."""
        self.validator.assert_valid(
            method_name='allowance',
            parameter_name='owner',
            argument_value=owner,
        )
        owner = self.validate_and_checksum_address(owner)
        self.validator.assert_valid(
            method_name='allowance',
            parameter_name='spender',
            argument_value=spender,
        )
        spender = self.validate_and_checksum_address(spender)
        return (owner, spender)


class ApproveMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the approve method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str, validator: Validator = None):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address, validator)

    def call(self, spender: str, amount: int) -> bool:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters
        :returns: the return value of the underlying method.
        bool(returned)
        """
        returned = super().__call__(spender, amount)

        return returned

    def send_call(self, spender: str, amount: int, trx=0, fee=900000, debug=False) -> bool:
        """Execute underlying contract method via eth_sendTransaction.

        :param tx_params: transaction parameters
        """
        super().setContractFee(fee).setContractDebug(debug).sendTrx(trx)
        return self.call(spender, amount)

    def validate_and_normalize_inputs(self, spender: str, amount: int):
        """Validate the inputs to the approve method."""
        self.validator.assert_valid(
            method_name='approve',
            parameter_name='spender',
            argument_value=spender,
        )
        spender = self.validate_and_checksum_address(spender)
        self.validator.assert_valid(
            method_name='approve',
            parameter_name='amount',
            argument_value=amount,
        )
        # safeguard against fractional inputs
        amount = int(amount)
        return (spender, amount)


class BalanceOfMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the balanceOf method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str, validator: Validator = None):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address, validator)

    def call(self, account: str) -> int:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters

        """
        returned = super().__call__(account)

        return returned

    def validate_and_normalize_inputs(self, account: str):
        """Validate the inputs to the balanceOf method."""
        self.validator.assert_valid(
            method_name='balanceOf',
            parameter_name='account',
            argument_value=account,
        )
        account = self.validate_and_checksum_address(account)
        return (account)


class BurnMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the burn method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str, validator: Validator = None):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address, validator)

    def call(self, amount: int) -> None:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters
        :returns: the return value of the underlying method.
        ()
        """
        super().__call__(amount)

    def send_call(self, amount: int, trx=0, fee=900000, debug=False) -> None:
        """Execute underlying contract method via eth_sendTransaction.

        :param tx_params: transaction parameters
        """
        super().setContractFee(fee).setContractDebug(debug).sendTrx(trx)
        return self.call(amount)

    def validate_and_normalize_inputs(self, amount: int):
        """Validate the inputs to the burn method."""
        self.validator.assert_valid(
            method_name='burn',
            parameter_name='amount',
            argument_value=amount,
        )
        # safeguard against fractional inputs
        amount = int(amount)
        return (amount)


class BurnFromMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the burnFrom method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str, validator: Validator = None):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address, validator)

    def call(self, account: str, amount: int) -> None:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters
        :returns: the return value of the underlying method.
        ()
        """
        super().__call__(account, amount)

    def send_call(self, account: str, amount: int, trx=0, fee=900000, debug=False) -> None:
        """Execute underlying contract method via eth_sendTransaction.

        :param tx_params: transaction parameters
        """
        super().setContractFee(fee).setContractDebug(debug).sendTrx(trx)
        return self.call(account, amount)

    def validate_and_normalize_inputs(self, account: str, amount: int):
        """Validate the inputs to the burnFrom method."""
        self.validator.assert_valid(
            method_name='burnFrom',
            parameter_name='account',
            argument_value=account,
        )
        account = self.validate_and_checksum_address(account)
        self.validator.assert_valid(
            method_name='burnFrom',
            parameter_name='amount',
            argument_value=amount,
        )
        # safeguard against fractional inputs
        amount = int(amount)
        return (account, amount)


class CapMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the cap method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address)

    def call(self) -> int:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters

        """
        returned = super().__call__()

        return returned


class DecimalsMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the decimals method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address)

    def call(self) -> int:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters

        """
        returned = super().__call__()

        return returned


class DecreaseAllowanceMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the decreaseAllowance method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str, validator: Validator = None):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address, validator)

    def call(self, spender: str, subtracted_value: int) -> bool:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters
        :returns: the return value of the underlying method.
        bool(returned)
        """
        returned = super().__call__(spender, subtracted_value)

        return returned

    def send_call(self, spender: str, subtracted_value: int, trx=0, fee=900000, debug=False) -> bool:
        """Execute underlying contract method via eth_sendTransaction.

        :param tx_params: transaction parameters
        """
        super().setContractFee(fee).setContractDebug(debug).sendTrx(trx)
        return self.call(spender, subtracted_value)

    def validate_and_normalize_inputs(self, spender: str, subtracted_value: int):
        """Validate the inputs to the decreaseAllowance method."""
        self.validator.assert_valid(
            method_name='decreaseAllowance',
            parameter_name='spender',
            argument_value=spender,
        )
        spender = self.validate_and_checksum_address(spender)
        self.validator.assert_valid(
            method_name='decreaseAllowance',
            parameter_name='subtractedValue',
            argument_value=subtracted_value,
        )
        # safeguard against fractional inputs
        subtracted_value = int(subtracted_value)
        return (spender, subtracted_value)


class GetDecimalsMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the getDecimals method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address)

    def call(self) -> int:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters

        """
        returned = super().__call__()

        return returned


class IncreaseAllowanceMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the increaseAllowance method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str, validator: Validator = None):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address, validator)

    def call(self, spender: str, added_value: int) -> bool:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters
        :returns: the return value of the underlying method.
        bool(returned)
        """
        returned = super().__call__(spender, added_value)

        return returned

    def send_call(self, spender: str, added_value: int, trx=0, fee=900000, debug=False) -> bool:
        """Execute underlying contract method via eth_sendTransaction.

        :param tx_params: transaction parameters
        """
        super().setContractFee(fee).setContractDebug(debug).sendTrx(trx)
        return self.call(spender, added_value)

    def validate_and_normalize_inputs(self, spender: str, added_value: int):
        """Validate the inputs to the increaseAllowance method."""
        self.validator.assert_valid(
            method_name='increaseAllowance',
            parameter_name='spender',
            argument_value=spender,
        )
        spender = self.validate_and_checksum_address(spender)
        self.validator.assert_valid(
            method_name='increaseAllowance',
            parameter_name='addedValue',
            argument_value=added_value,
        )
        # safeguard against fractional inputs
        added_value = int(added_value)
        return (spender, added_value)


class IsMinterMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the isMinter method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str, validator: Validator = None):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address, validator)

    def call(self, account: str) -> bool:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters

        """
        returned = super().__call__(account)

        return returned

    def validate_and_normalize_inputs(self, account: str):
        """Validate the inputs to the isMinter method."""
        self.validator.assert_valid(
            method_name='isMinter',
            parameter_name='account',
            argument_value=account,
        )
        account = self.validate_and_checksum_address(account)
        return (account)


class MintMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the mint method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str, validator: Validator = None):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address, validator)

    def call(self, account: str, amount: int) -> bool:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters
        :returns: the return value of the underlying method.
        bool(returned)
        """
        returned = super().__call__(account, amount)

        return returned

    def send_call(self, account: str, amount: int, trx=0, fee=900000, debug=False) -> bool:
        """Execute underlying contract method via eth_sendTransaction.

        :param tx_params: transaction parameters
        """
        super().setContractFee(fee).setContractDebug(debug).sendTrx(trx)
        return self.call(account, amount)

    def validate_and_normalize_inputs(self, account: str, amount: int):
        """Validate the inputs to the mint method."""
        self.validator.assert_valid(
            method_name='mint',
            parameter_name='account',
            argument_value=account,
        )
        account = self.validate_and_checksum_address(account)
        self.validator.assert_valid(
            method_name='mint',
            parameter_name='amount',
            argument_value=amount,
        )
        # safeguard against fractional inputs
        amount = int(amount)
        return (account, amount)


class NameMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the name method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address)

    def call(self) -> str:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters

        """
        returned = super().__call__()

        return returned


class RenounceMinterMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the renounceMinter method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address)

    def call(self) -> None:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters
        :returns: the return value of the underlying method.
        ()
        """
        super().__call__()

    def send_call(self, trx=0, fee=900000, debug=False) -> None:
        """Execute underlying contract method via eth_sendTransaction.

        :param tx_params: transaction parameters
        """
        super().setContractFee(fee).setContractDebug(debug).sendTrx(trx)
        return self.call()


class SymbolMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the symbol method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address)

    def call(self) -> str:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters

        """
        returned = super().__call__()

        return returned


class TokenNameMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the tokenName method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address)

    def call(self) -> str:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters

        """
        returned = super().__call__()

        return returned


class TokenSymbolMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the tokenSymbol method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address)

    def call(self) -> str:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters

        """
        returned = super().__call__()

        return returned


class TotalSupplyMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the totalSupply method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address)

    def call(self) -> int:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters

        """
        returned = super().__call__()

        return returned


class TransferMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the transfer method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str, validator: Validator = None):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address, validator)

    def call(self, recipient: str, amount: int) -> bool:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters
        :returns: the return value of the underlying method.
        bool(returned)
        """
        returned = super().__call__(recipient, amount)

        return returned

    def send_call(self, recipient: str, amount: int, trx=0, fee=900000, debug=False) -> bool:
        """Execute underlying contract method via eth_sendTransaction.

        :param tx_params: transaction parameters
        """
        super().setContractFee(fee).setContractDebug(debug).sendTrx(trx)
        return self.call(recipient, amount)

    def validate_and_normalize_inputs(self, recipient: str, amount: int):
        """Validate the inputs to the transfer method."""
        self.validator.assert_valid(
            method_name='transfer',
            parameter_name='recipient',
            argument_value=recipient,
        )
        recipient = self.validate_and_checksum_address(recipient)
        self.validator.assert_valid(
            method_name='transfer',
            parameter_name='amount',
            argument_value=amount,
        )
        # safeguard against fractional inputs
        amount = int(amount)
        return (recipient, amount)


class TransferFromMethod(ContractMethod):  # pylint: disable=invalid-name
    """Various interfaces to the transferFrom method."""

    def __init__(self, abi: dict, contract: Contract, owner_address: str, contract_address: str, validator: Validator = None):
        """Persist instance data."""
        super().__init__(abi, contract, owner_address, contract_address, validator)

    def call(self, sender: str, recipient: str, amount: int) -> bool:
        """Execute underlying contract method via __call__.

        :param tx_params: transaction parameters
        :returns: the return value of the underlying method.
        bool(returned)
        """
        returned = super().__call__(sender, recipient, amount)

        return returned

    def send_call(self, sender: str, recipient: str, amount: int, trx=0, fee=900000, debug=False) -> bool:
        """Execute underlying contract method via eth_sendTransaction.

        :param tx_params: transaction parameters
        """
        super().setContractFee(fee).setContractDebug(debug).sendTrx(trx)
        return self.call(sender, recipient, amount)

    def validate_and_normalize_inputs(self, sender: str, recipient: str, amount: int):
        """Validate the inputs to the transferFrom method."""
        self.validator.assert_valid(
            method_name='transferFrom',
            parameter_name='sender',
            argument_value=sender,
        )
        sender = self.validate_and_checksum_address(sender)
        self.validator.assert_valid(
            method_name='transferFrom',
            parameter_name='recipient',
            argument_value=recipient,
        )
        recipient = self.validate_and_checksum_address(recipient)
        self.validator.assert_valid(
            method_name='transferFrom',
            parameter_name='amount',
            argument_value=amount,
        )
        # safeguard against fractional inputs
        amount = int(amount)
        return (sender, recipient, amount)


class ApprovalTracker(EventTracker):  # pylint: disable=invalid-name

    def __init__(self, forceStart: any = False, debug: bool = False):
        """Persist instance data."""
        self.tron = None
        self.contract_address = None
        super().__init__(forceStart, debug)

    def setTronInstance(self, _tron: any, _contract_address: str) -> None:
        self.tron = _tron
        self.contract_address = _contract_address

    def trackOnce(self) -> None:
        events = self.trackEvent(self.tron, "Approval", self.contract_address)
        if len(events) > 0:
            for c in events:
                if "transaction_id" in c and "result" in c and self.isCallBackReady():
                    self.callback_event_found(c["result"]["owner"], c["result"]["spender"], c["result"]["value"], c["block_number"], c["block_timestamp"])


class MinterAddedTracker(EventTracker):  # pylint: disable=invalid-name

    def __init__(self, forceStart: any = False, debug: bool = False):
        """Persist instance data."""
        self.tron = None
        self.contract_address = None
        super().__init__(forceStart, debug)

    def setTronInstance(self, _tron: any, _contract_address: str) -> None:
        self.tron = _tron
        self.contract_address = _contract_address

    def trackOnce(self) -> None:
        events = self.trackEvent(self.tron, "MinterAdded", self.contract_address)
        if len(events) > 0:
            for c in events:
                if "transaction_id" in c and "result" in c and self.isCallBackReady():
                    self.callback_event_found(c["result"]["account"], c["block_number"], c["block_timestamp"])


class MinterRemovedTracker(EventTracker):  # pylint: disable=invalid-name

    def __init__(self, forceStart: any = False, debug: bool = False):
        """Persist instance data."""
        self.tron = None
        self.contract_address = None
        super().__init__(forceStart, debug)

    def setTronInstance(self, _tron: any, _contract_address: str) -> None:
        self.tron = _tron
        self.contract_address = _contract_address

    def trackOnce(self) -> None:
        events = self.trackEvent(self.tron, "MinterRemoved", self.contract_address)
        if len(events) > 0:
            for c in events:
                if "transaction_id" in c and "result" in c and self.isCallBackReady():
                    self.callback_event_found(c["result"]["account"], c["block_number"], c["block_timestamp"])


class TransferTracker(EventTracker):  # pylint: disable=invalid-name

    def __init__(self, forceStart: any = False, debug: bool = False):
        """Persist instance data."""
        self.tron = None
        self.contract_address = None
        super().__init__(forceStart, debug)

    def setTronInstance(self, _tron: any, _contract_address: str) -> None:
        self.tron = _tron
        self.contract_address = _contract_address

    def trackOnce(self) -> None:
        events = self.trackEvent(self.tron, "Transfer", self.contract_address)
        if len(events) > 0:
            for c in events:
                if "transaction_id" in c and "result" in c and self.isCallBackReady():
                    self.callback_event_found(c["result"]["from"], c["result"]["to"], c["result"]["value"], c["block_number"], c["block_timestamp"])


# pylint: disable=too-many-public-methods,too-many-instance-attributes
class TokenLv:
    """Wrapper class for TokenLv Solidity contract."""
    _fn_add_minter: AddMinterMethod
    """Constructor-initialized instance of
    :class:`AddMinterMethod`.
    """
    _fn_allowance: AllowanceMethod
    """Constructor-initialized instance of
    :class:`AllowanceMethod`.
    """
    _fn_approve: ApproveMethod
    """Constructor-initialized instance of
    :class:`ApproveMethod`.
    """
    _fn_balance_of: BalanceOfMethod
    """Constructor-initialized instance of
    :class:`BalanceOfMethod`.
    """
    _fn_burn: BurnMethod
    """Constructor-initialized instance of
    :class:`BurnMethod`.
    """
    _fn_burn_from: BurnFromMethod
    """Constructor-initialized instance of
    :class:`BurnFromMethod`.
    """
    _fn_cap: CapMethod
    """Constructor-initialized instance of
    :class:`CapMethod`.
    """
    _fn_decimals: DecimalsMethod
    """Constructor-initialized instance of
    :class:`DecimalsMethod`.
    """
    _fn_decrease_allowance: DecreaseAllowanceMethod
    """Constructor-initialized instance of
    :class:`DecreaseAllowanceMethod`.
    """
    _fn_get_decimals: GetDecimalsMethod
    """Constructor-initialized instance of
    :class:`GetDecimalsMethod`.
    """
    _fn_increase_allowance: IncreaseAllowanceMethod
    """Constructor-initialized instance of
    :class:`IncreaseAllowanceMethod`.
    """
    _fn_is_minter: IsMinterMethod
    """Constructor-initialized instance of
    :class:`IsMinterMethod`.
    """
    _fn_mint: MintMethod
    """Constructor-initialized instance of
    :class:`MintMethod`.
    """
    _fn_name: NameMethod
    """Constructor-initialized instance of
    :class:`NameMethod`.
    """
    _fn_renounce_minter: RenounceMinterMethod
    """Constructor-initialized instance of
    :class:`RenounceMinterMethod`.
    """
    _fn_symbol: SymbolMethod
    """Constructor-initialized instance of
    :class:`SymbolMethod`.
    """
    _fn_token_name: TokenNameMethod
    """Constructor-initialized instance of
    :class:`TokenNameMethod`.
    """
    _fn_token_symbol: TokenSymbolMethod
    """Constructor-initialized instance of
    :class:`TokenSymbolMethod`.
    """
    _fn_total_supply: TotalSupplyMethod
    """Constructor-initialized instance of
    :class:`TotalSupplyMethod`.
    """
    _fn_transfer: TransferMethod
    """Constructor-initialized instance of
    :class:`TransferMethod`.
    """
    _fn_transfer_from: TransferFromMethod
    """Constructor-initialized instance of
    :class:`TransferFromMethod`.
    """

    _ev_approval: ApprovalTracker
    """Constructor-initialized instance of
    :class:`ApprovalTracker`.
    """
    _ev_minter_added: MinterAddedTracker
    """Constructor-initialized instance of
    :class:`MinterAddedTracker`.
    """
    _ev_minter_removed: MinterRemovedTracker
    """Constructor-initialized instance of
    :class:`MinterRemovedTracker`.
    """
    _ev_transfer: TransferTracker
    """Constructor-initialized instance of
    :class:`TransferTracker`.
    """

    call_contract_fee_amount: int

    call_contract_debug_flag: bool

    def __init__(
            self,
            tron_provider: Tron,
            contract_address: str,
            validator: TokenLvValidator = None,
    ):
        """Get an instance of wrapper for smart contract.

        :param tron_provider: Either an instance of `web3.Web3`:code: or
            `web3.providers.base.BaseProvider`:code:
        :param contract_address: where the contract has been deployed
        :param validator: for validation of method inputs.
        """
        # pylint: disable=too-many-statements

        self.contract_address = contract_address

        if not validator:
            validator = TokenLvValidator(tron_provider, contract_address)

        # if any middleware was imported, inject it
        try:
            MIDDLEWARE
        except NameError:
            pass
        else:
            pass

        self._tron_trx = tron_provider.trx

        abi_dict = TokenLv.abi()
        contract = self._tron_trx.contract(address=contract_address, abi=abi_dict)
        owner = self._tron_trx.tron.default_address
        fn = contract.functions

        self._fn_add_minter = AddMinterMethod(fn.get_abi_by_name('addMinter'), contract, owner, contract_address, validator)
        self._fn_allowance = AllowanceMethod(fn.get_abi_by_name('allowance'), contract, owner, contract_address, validator)
        self._fn_approve = ApproveMethod(fn.get_abi_by_name('approve'), contract, owner, contract_address, validator)
        self._fn_balance_of = BalanceOfMethod(fn.get_abi_by_name('balanceOf'), contract, owner, contract_address, validator)
        self._fn_burn = BurnMethod(fn.get_abi_by_name('burn'), contract, owner, contract_address, validator)
        self._fn_burn_from = BurnFromMethod(fn.get_abi_by_name('burnFrom'), contract, owner, contract_address, validator)
        self._fn_cap = CapMethod(fn.get_abi_by_name('cap'), contract, owner, contract_address)
        self._fn_decimals = DecimalsMethod(fn.get_abi_by_name('decimals'), contract, owner, contract_address)
        self._fn_decrease_allowance = DecreaseAllowanceMethod(fn.get_abi_by_name('decreaseAllowance'), contract, owner, contract_address, validator)
        self._fn_get_decimals = GetDecimalsMethod(fn.get_abi_by_name('getDecimals'), contract, owner, contract_address)
        self._fn_increase_allowance = IncreaseAllowanceMethod(fn.get_abi_by_name('increaseAllowance'), contract, owner, contract_address, validator)
        self._fn_is_minter = IsMinterMethod(fn.get_abi_by_name('isMinter'), contract, owner, contract_address, validator)
        self._fn_mint = MintMethod(fn.get_abi_by_name('mint'), contract, owner, contract_address, validator)
        self._fn_name = NameMethod(fn.get_abi_by_name('name'), contract, owner, contract_address)
        self._fn_renounce_minter = RenounceMinterMethod(fn.get_abi_by_name('renounceMinter'), contract, owner, contract_address)
        self._fn_symbol = SymbolMethod(fn.get_abi_by_name('symbol'), contract, owner, contract_address)
        self._fn_token_name = TokenNameMethod(fn.get_abi_by_name('tokenName'), contract, owner, contract_address)
        self._fn_token_symbol = TokenSymbolMethod(fn.get_abi_by_name('tokenSymbol'), contract, owner, contract_address)
        self._fn_total_supply = TotalSupplyMethod(fn.get_abi_by_name('totalSupply'), contract, owner, contract_address)
        self._fn_transfer = TransferMethod(fn.get_abi_by_name('transfer'), contract, owner, contract_address, validator)
        self._fn_transfer_from = TransferFromMethod(fn.get_abi_by_name('transferFrom'), contract, owner, contract_address, validator)
        self._ev_approval = ApprovalTracker(False, False)
        self._ev_minter_added = MinterAddedTracker(False, False)
        self._ev_minter_removed = MinterRemovedTracker(False, False)
        self._ev_transfer = TransferTracker(False, False)

    """
    Implementation of event approval in contract TokenLv
    Get log entry for Approval event.
            :param tx_hash: hash of transaction emitting Approval event
    """

    def event_approval(self) -> "ApprovalTracker":
        self._ev_approval.setTronInstance(self._tron_trx.tron, self.contract_address)
        return self._ev_approval

    """
    Implementation of event minter_added in contract TokenLv
    Get log entry for MinterAdded event.
            :param tx_hash: hash of transaction emitting MinterAdded event
    """

    def event_minter_added(self) -> "MinterAddedTracker":
        self._ev_minter_added.setTronInstance(self._tron_trx.tron, self.contract_address)
        return self._ev_minter_added

    """
    Implementation of event minter_removed in contract TokenLv
    Get log entry for MinterRemoved event.
            :param tx_hash: hash of transaction emitting MinterRemoved event
    """

    def event_minter_removed(self) -> "MinterRemovedTracker":
        self._ev_minter_removed.setTronInstance(self._tron_trx.tron, self.contract_address)
        return self._ev_minter_removed

    """
    Implementation of event transfer in contract TokenLv
    Get log entry for Transfer event.
            :param tx_hash: hash of transaction emitting Transfer event
    """

    def event_transfer(self) -> "TransferTracker":
        self._ev_transfer.setTronInstance(self._tron_trx.tron, self.contract_address)
        return self._ev_transfer

    """
    implementation of add_minter in contract TokenLv
    
    """

    def add_minter(self, account: str) -> None:
        return self._fn_add_minter.send_call(account, 0, self.call_contract_fee_amount, self.call_contract_debug_flag)

    """
    implementation of allowance in contract TokenLv
    
    """

    def allowance(self, owner: str, spender: str) -> int:
        return self._fn_allowance.call(owner, spender)

    """
    implementation of approve in contract TokenLv
    
    """

    def approve(self, spender: str, amount: int) -> bool:
        return self._fn_approve.send_call(spender, amount, 0, self.call_contract_fee_amount, self.call_contract_debug_flag)

    """
    implementation of balance_of in contract TokenLv
    
    """

    def balance_of(self, account: str) -> int:
        return self._fn_balance_of.call(account)

    """
    implementation of burn in contract TokenLv
    
    """

    def burn(self, amount: int) -> BurnMethod:
        self._fn_burn.send_call(amount, 0, self.call_contract_fee_amount, self.call_contract_debug_flag)
        return self._fn_burn

    """
    implementation of burn_from in contract TokenLv
    
    """

    def burn_from(self, account: str, amount: int) -> None:
        return self._fn_burn_from.send_call(account, amount, 0, self.call_contract_fee_amount, self.call_contract_debug_flag)

    """
    implementation of cap in contract TokenLv
    
    """

    def cap(self) -> int:
        return self._fn_cap.call()

    """
    implementation of decimals in contract TokenLv
    
    """

    def decimals(self) -> int:
        return self._fn_decimals.call()

    """
    implementation of decrease_allowance in contract TokenLv
    
    """

    def decrease_allowance(self, spender: str, subtracted_value: int) -> bool:
        return self._fn_decrease_allowance.send_call(spender, subtracted_value, 0, self.call_contract_fee_amount, self.call_contract_debug_flag)

    """
    implementation of get_decimals in contract TokenLv
    
    """

    def get_decimals(self) -> int:
        return self._fn_get_decimals.call()

    """
    implementation of increase_allowance in contract TokenLv
    
    """

    def increase_allowance(self, spender: str, added_value: int) -> bool:
        return self._fn_increase_allowance.send_call(spender, added_value, 0, self.call_contract_fee_amount, self.call_contract_debug_flag)

    """
    implementation of is_minter in contract TokenLv
    
    """

    def is_minter(self, account: str) -> bool:
        return self._fn_is_minter.call(account)

    """
    implementation of mint in contract TokenLv
    
    """

    def mint(self, account: str, amount: int) -> bool:
        return self._fn_mint.send_call(account, amount, 0, self.call_contract_fee_amount, self.call_contract_debug_flag)

    """
    implementation of name in contract TokenLv
    
    """

    def name(self) -> str:
        return self._fn_name.call()

    """
    implementation of renounce_minter in contract TokenLv
    
    """

    def renounce_minter(self) -> None:
        return self._fn_renounce_minter.send_call(0, self.call_contract_fee_amount, self.call_contract_debug_flag)

    """
    implementation of symbol in contract TokenLv
    
    """

    def symbol(self) -> str:
        return self._fn_symbol.call()

    """
    implementation of token_name in contract TokenLv
    
    """

    def token_name(self) -> str:
        return self._fn_token_name.call()

    """
    implementation of token_symbol in contract TokenLv
    
    """

    def token_symbol(self) -> str:
        return self._fn_token_symbol.call()

    """
    implementation of total_supply in contract TokenLv
    
    """

    def total_supply(self) -> int:
        return self._fn_total_supply.call()

    """
    implementation of transfer in contract TokenLv
    
    """

    def transfer(self, recipient: str, amount: int) -> bool:
        return self._fn_transfer.send_call(recipient, amount, 0, self.call_contract_fee_amount, self.call_contract_debug_flag)

    """
    implementation of transfer_from in contract TokenLv
    
    """

    def transfer_from(self, sender: str, recipient: str, amount: int) -> bool:
        return self._fn_transfer_from.send_call(sender, recipient, amount, 0, self.call_contract_fee_amount, self.call_contract_debug_flag)

    def CallContractFee(self, amount: int) -> "TokenLv":
        self.call_contract_fee_amount = amount
        return self

    def CallDebug(self, yesno: bool) -> "TokenLv":
        self.call_contract_debug_flag = yesno
        return self

    @staticmethod
    def abi() -> dict:
        """Return the ABI to the underlying contract."""
        return json.loads(
            '[{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"account","type":"address"}],"name":"MinterAdded","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"account","type":"address"}],"name":"MinterRemoved","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":false,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"addMinter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burn","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burnFrom","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"cap","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getDecimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"isMinter","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"renounceMinter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"tokenName","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"tokenSymbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]'
            # noqa: E501 (line-too-long)
        )

# pylint: disable=too-many-lines

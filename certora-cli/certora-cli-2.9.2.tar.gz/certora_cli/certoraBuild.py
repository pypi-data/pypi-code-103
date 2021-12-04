import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from sly import Lexer  # type: ignore
from sly import Parser  # type: ignore
from sly.lex import Token  # type: ignore
from sly.yacc import YaccProduction  # type: ignore
import traceback
from collections import OrderedDict
from typing import Any, Dict, List, Tuple, Optional, Set

from Crypto.Hash import keccak

from certora_cli.certoraUtils import print_completion_message, run_local_spec_check
from certora_cli.certoraUtils import debug_print_, read_json_file, replace_file_name, print_warning
from certora_cli.certoraUtils import CERTORA_CONFIG_DIR, CERTORA_BUILD_FILE, CERTORA_VERIFY_FILE, SolcCompilationException, \
    abs_posix_path_relative_to_root_file
from certora_cli.certoraUtils import OPTION_OUTPUT_VERIFY, fatal_error, is_windows, remove_and_recreate_dir, getcwd, as_posix, \
    abs_posix_path
from certora_cli.certoraUtils import get_file_basename, get_file_extension, safe_create_dir, \
    prepare_call_args, remove_file
from certora_cli.certoraUtils import is_hex, decimal_str_to_cvt_compatible, hex_str_to_cvt_compatible, mode_has_spec_file
from certora_cli.certoraUtils import get_closest_strings, flatten_set_list

BUILD_IS_LIBRARY = False
DEBUG = False


def exit_if_not_library(code: int) -> None:
    if BUILD_IS_LIBRARY:
        return
    else:
        sys.exit(code)


def fatal_error_if_not_library(msg: str) -> None:
    if BUILD_IS_LIBRARY:
        print(msg)
        raise Exception(msg)
    else:
        fatal_error(msg)


def print_failed_to_run(cmd: str) -> None:
    print()
    print(f"Failed to run {cmd}")
    if is_windows() and cmd.find('solc') != -1 and cmd.find('exe') == -1:
        print("did you forget the .exe extension for solcXX.exe??")
    print()


def run_cmd(cmd: str, name: str, config_path: str, input: bytes = None, shell: bool = False, debug: bool = False) \
        -> None:
    debug_print_(f"Running cmd {cmd}", debug)

    stdout_name = f"{config_path}/{name}.stdout"
    stderr_name = f"{config_path}/{name}.stderr"
    debug_print_(f"stdout, stderr = {stdout_name}, {stderr_name}", debug)

    with open(stdout_name, 'w+') as stdout:
        with open(stderr_name, 'w+') as stderr:
            try:
                args = prepare_call_args(cmd)
                if shell:
                    shell_args = ' '.join(args)
                    exitcode = subprocess.run(shell_args, stdout=stdout, stderr=stderr,
                                              input=input, shell=shell).returncode
                else:
                    exitcode = subprocess.run(args, stdout=stdout, stderr=stderr, input=input, shell=shell).returncode
                if exitcode:
                    msg = f"Failed to run {cmd}, exit code {exitcode}"
                    with open(stderr_name, 'r') as stderr_read:
                        for line in stderr_read:
                            print(line)
                    raise Exception(msg)
                else:
                    debug_print_(f"Exitcode {exitcode}", debug)
            except Exception as e:
                print(f"Error: {e}")
                print_failed_to_run(cmd)
                raise


def debug_print(s: str) -> None:
    debug_print_(s, DEBUG)


class Instrumentation:
    def __init__(self, expected: bytes, before: bool, to_ins: str) -> None:
        self.expected = expected
        self.before = before
        self.to_ins = to_ins


class InputConfig:
    def __init__(self, args: argparse.Namespace) -> None:
        """
        A class holding relevant attributes for the build string.
        :param args: command line input argument in an argparse.Namespace
        """

        self.parsed_options = args  # type: argparse.Namespace

        # populate fields relevant for build, handle defaults
        self.files = args.file_paths
        self.solc = args.solc
        self.solc_args = args.solc_args
        self.packages = args.packages
        self.verify = args.verify
        self.assert_contracts = args.assert_contracts
        self.path = args.path
        self.debug = args.debug
        self.link = args.link
        self.struct_link = args.struct_link
        self.function_finders = args.internal_funcs

        if args.solc_map is not None:
            self.solc_mappings = args.solc_map  # type: Dict[str, str]
        else:
            self.solc_mappings = {}

        if args.address is not None:
            self.address = args.address  # type: Dict[str, int]
        else:
            self.address = dict()

        self.fileToContractName = args.file_to_contract


class SolidityType:
    def __init__(self,
                 base_type: str,  # The source code representation of the base type (e.g., the base type of A[][] is A)
                 components: List[Any],  # List[SolidityType]
                 array_dims: List[int],
                 # If this is an array, the i-th element is its i-th dimension size; -1 denotes a dynamic array
                 is_storage: bool,  # Whether it's a storage pointer (only applicable to library functions)
                 is_tuple: bool,  # Whether it's a tuple or a user-defined struct
                 # TODO: since this is a disjunction of is_contract and is_payable, we should have those two as params
                 #       and then calculate is_address_alias (same for is_uint8_alias maybe)
                 is_address_alias: bool,  # Whether it's an alias of address type (e.g., contract, 'address payable')
                 is_uint8_alias: bool,  # Whether it's an alias of uint8 type (e.g., enum)
                 is_mapping: bool,
                 is_function: bool,
                 is_enum: bool,
                 is_contract: bool,
                 is_calldata: bool,
                 solidity_type_declaration: str = None,
                 lib_canonical_signature: str = None
                 # If this is a library function param, this signature used to compute the sighash of the function
                 ):
        self.base_type = base_type
        self.components = components
        self.array_dims = array_dims
        self.is_storage = is_storage
        self.is_tuple = is_tuple
        self.is_address_alias = is_address_alias
        self.is_uint8_alias = is_uint8_alias
        self.is_mapping = is_mapping
        self.is_function = is_function
        self.is_enum = is_enum
        self.is_contract = is_contract
        self.is_calldata = is_calldata
        self.lib_canonical_signature = lib_canonical_signature
        self.solidity_type_declaration = solidity_type_declaration

    def as_dict(self) -> Dict[str, Any]:
        return {
            "baseType": self.base_type,
            "components": [x.as_dict() for x in self.components],
            "arrayDims": self.array_dims,
            "isStorage": self.is_storage,
            "isTuple": self.is_tuple,
            "isAddressAlias": self.is_address_alias,
            "isUint8Alias": self.is_uint8_alias
        }

    def __repr__(self) -> str:
        return repr(self.as_dict())

    def array_dims_signature(self) -> str:
        return "".join([(lambda x: "[]" if (x == -1) else f"[{x}]")(dim_size) for dim_size in self.array_dims[::-1]])

    def canonical_tuple_signature(self) -> str:
        return "(" + ",".join([x.signature() for x in self.components]) + ")"

    # Returns a signature in a "canonical form", namely without user-defined types and with decomposed struct members
    def signature(self) -> str:
        base_type_str = self.lib_canonical_signature if self.lib_canonical_signature is not None else (
            "uint8" if self.is_uint8_alias else (self.canonical_tuple_signature() if self.is_tuple else (
                "address" if self.is_address_alias else self.base_type)))
        return base_type_str + self.array_dims_signature() + (" storage" if self.is_storage else "")

    # Returns a signature with user-defined types
    def source_code_signature(self) -> str:
        return self.base_type + self.array_dims_signature() + (" storage" if self.is_storage else "")


class Func:
    def __init__(self,
                 name: str,
                 fullArgs: List[SolidityType],
                 argNames: List[str],
                 returns: List[SolidityType],
                 sighash: str,
                 notpayable: bool,
                 isABI: bool,
                 fromLib: bool,  # not serialized
                 isConstructor: bool,  # not serialized
                 stateMutability: Dict[str, str],
                 visibility: str,
                 implemented: bool,  # does this function have a body? (false for interface functions)
                 ast_id: Optional[int],
                 where: Optional[Tuple[str, str]] = None  # 1st element: source file name, 2nd element: location string
                 ):
        self.name = name
        self.fullArgs = fullArgs
        self.argNames = argNames
        self.returns = returns
        self.sighash = sighash
        self.notpayable = notpayable
        self.isABI = isABI
        self.fromLib = fromLib
        self.isConstructor = isConstructor
        self.stateMutability = stateMutability
        self.visibility = visibility
        self.sighashIsFromOtherName = any([a.lib_canonical_signature is not None for a in fullArgs])
        self.where = where
        self.implemented = implemented
        self.ast_id = ast_id

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "fullArgs": list(map(lambda x: x.as_dict(), self.fullArgs)),
            "returns": list(map(lambda x: x.as_dict(), self.returns)),
            "sighash": self.sighash,
            "notpayable": self.notpayable,
            "isABI": self.isABI,
            "stateMutability": self.stateMutability,
            "visibility": self.visibility,
            "sighashIsFromOtherName": self.sighashIsFromOtherName
        }

    def __repr__(self) -> str:
        return repr(self.as_dict())

    def __lt__(self, other: Any) -> bool:
        return self.source_code_signature() < other.source_code_signature()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Func):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.signature() == other.signature()

    def __hash__(self) -> int:
        return int(self.sighash, 16)

    def signature(self) -> str:
        return Func.compute_signature(self.name, self.fullArgs, lambda x: x.signature())

    def source_code_signature(self) -> str:
        return Func.compute_signature(self.name, self.fullArgs, lambda x: x.source_code_signature())

    @staticmethod
    def compute_signature(name: str, args: List[SolidityType], signature_getter: Any) -> str:
        return name + "(" + ",".join([signature_getter(x) for x in args]) + ")"


class ImmutableReference:
    def __init__(self, offset: str, length: str, varname: str):
        self.offset = offset
        self.length = length
        self.varname = varname

    def as_dict(self) -> Dict[str, Any]:
        return {
            "offset": self.offset,
            "length": self.length,
            "varname": self.varname
        }

    def __repr__(self) -> str:
        return repr(self.as_dict())


class PresetImmutableReference(ImmutableReference):
    def __init__(self,
                 offset: str,
                 length: str,
                 varname: str,
                 value: str
                 ):
        ImmutableReference.__init__(self, offset, length, varname)
        self.value = value

    def as_dict(self) -> Dict[str, Any]:
        _dict = ImmutableReference.as_dict(self)
        _dict["value"] = self.value
        return _dict

    def __repr__(self) -> str:
        return repr(self.as_dict())


# Python3.5 to which we maintain backward-compatibility due to CI's docker image, does not support @dataclass
class ContractInSDC:
    def __init__(self, name: str, source_file: str,
                 report_source_file: str, address: str,
                 methods: Set[Func], bytecode: str,
                 constructor_bytecode: str,
                 srcmap: str, varmap: Any, constructor_srcmap: str,
                 storageLayout: Any, immutables: List[ImmutableReference],
                 function_finders: Dict[str, str], internal_funcs: Set[Func], public_funcs: Set[Func],
                 source_bytes: Tuple[int, int] = (0, 0)):
        self.name = name
        self.original_file = source_file
        self.report_source_file = report_source_file
        self.address = address
        self.methods = methods
        self.bytecode = bytecode
        self.constructor_bytecode = constructor_bytecode
        self.srcmap = srcmap
        self.varmap = varmap
        self.constructorSrcmap = constructor_srcmap
        self.storageLayout = storageLayout
        self.immutables = immutables
        # function finder: a mapping from external function ids to
        # the ids of the internal functions they are "finding" for us
        self.function_finders = function_finders
        # the internal functions of the contract NOT including imported library functions
        self.internal_funcs = internal_funcs
        # the public functions of the contract (this EXCLUDES external functions)
        self.public_funcs = public_funcs
        # the start and end source bytes of the contract
        self.source_bytes = source_bytes

    def as_dict(self) -> Dict[str, Any]:
        """
        :return: A dictionary representation of this SDC, including all attributes and their values
        """
        return {
            "name": self.name,
            "original_file": self.original_file,
            "file": self.report_source_file,
            "address": self.address,
            "methods": list(map(lambda x: x.as_dict(), self.methods)),
            "bytecode": self.bytecode,
            "constructorBytecode": self.constructor_bytecode,
            "srcmap": self.srcmap,
            "varmap": self.varmap,
            "constructorSrcmap": self.constructorSrcmap,
            "storageLayout": self.storageLayout,
            "immutables": list(map(lambda x: x.as_dict(), self.immutables)),
            "internalFunctions": self.function_finders
        }

    def as_printable_dict(self) -> Dict[str, Any]:
        """
        :return: A dictionary representation of this SDC meant for printing to logs.
        It does not include long, hard-to-read attributes: bytecodes and srcmaps of the contract and the constructor.
        """
        return {
            "name": self.name,
            "original_file": self.original_file,
            "file": self.report_source_file,
            "address": self.address,
            "methods": list(map(lambda x: x.as_dict(), self.methods)),
            "storageLayout": self.storageLayout,
            "immutables": list(map(lambda x: x.as_dict(), self.immutables)),
            "internalFunctions": self.function_finders
        }

    def __repr__(self) -> str:
        return repr(self.as_printable_dict())


class SDC:
    def __init__(self, primary_contract: str, primary_contract_address: str, sdc_origin_file: str,
                 original_srclist: Dict[Any, Any], report_srclist: Dict[Any, Any], sdc_name: str,
                 contracts: List[ContractInSDC], library_addresses: List[str], generated_with: str,
                 state: Dict[str, str], struct_linking_info: Dict[str, str]):
        self.primary_contract = primary_contract
        self.primary_contract_address = primary_contract_address
        self.sdc_origin_file = sdc_origin_file
        self.original_srclist = original_srclist
        self.report_srclist = report_srclist
        self.sdc_name = sdc_name
        self.contracts = contracts
        self.library_addresses = library_addresses
        self.generated_with = generated_with
        self.state = state
        self.structLinkingInfo = struct_linking_info

    def as_dict(self) -> Dict[str, Any]:
        return {
            "primary_contract": self.primary_contract,
            "primary_contract_address": self.primary_contract_address,
            "sdc_origin_file": self.sdc_origin_file,
            "original_srclist": self.original_srclist,
            "srclist": self.report_srclist,
            "sdc_name": self.sdc_name,
            "contracts": list(map(lambda x: x.as_dict(), self.contracts)),
            "library_addresses": self.library_addresses,
            "generated_with": self.generated_with,
            "state": self.state,
            "structLinkingInfo": self.structLinkingInfo,
        }


class CertoraBuildGenerator:
    def __init__(self, input_config: InputConfig) -> None:
        self.input_config = input_config
        # SDCs describes the set of all 'Single Deployed Contracts' the solidity file whose contracts comprise a single
        # bytecode of interest. Which one it is - we don't know yet, but we make a guess based on the base filename.
        # An SDC corresponds to a single solidity file.
        self.SDCs = {}  # type: Dict[str, SDC]

        # Note that the the last '/' in config_path is important for solc to succeed, so it should be added
        self.config_path = f"{getcwd()}/{CERTORA_CONFIG_DIR}"
        self.library_addresses = []  # type: List[str]

        # ASTs will be lazily loaded
        # original source file -> contract file -> nodeid -> node
        self.asts = {}  # type: Dict[str, Dict[str, Dict[int, Any]]]
        remove_and_recreate_dir(self.config_path)

        self.address_generator_idx = 0
        self.function_finder_generator_idx = 0
        self.generated_files: List[str] = list()

    @staticmethod
    def CERTORA_CONTRACT_NAME() -> str:
        return "certora_contract_name"

    def is_library_def_node(self, contract_file: str, node_ref: int, build_arg_contract_file: str) -> bool:
        contract_def_node = self.asts[build_arg_contract_file][contract_file][node_ref]
        return "contractKind" in contract_def_node and contract_def_node["contractKind"] == "library"

    def get_contract_file_of(self, build_arg_contract_file: str, reference: int) -> str:
        original_file_asts = self.asts[build_arg_contract_file]
        for contract in original_file_asts:
            if reference in original_file_asts[contract]:
                return contract
        # error if got here
        fatal_error_if_not_library(f"Could not find reference AST node {reference}")
        return ""

    def collect_funcs(self, data: Dict[str, Any], contract_file: str,
                      contract_name: str, build_arg_contract_file: str) -> Set[Func]:

        constructor_string = "constructor"

        def is_imported_abi_entry(x: Dict[str, Any]) -> bool:
            return x["type"] == "function" or x["type"] == constructor_string

        def get_abi_entry_name(x: Dict[str, Any]) -> str:
            if x["type"] == "function":
                return x["name"]
            elif x["type"] == constructor_string:
                return constructor_string
            else:
                return ""  # Should be unreachable

        def collect_func_source_code_signatures_from_abi() -> List[str]:
            func_signatures = []
            abi = data["abi"]  # ["contracts"][contract_file][contract_name]["abi"]
            debug_print(f"abi is: \n{abi}")
            for f in filter(lambda x: is_imported_abi_entry(x), abi):
                inputs = f["inputs"]
                name = get_abi_entry_name(f)
                func_inputs = [input["internalType"] if "internalType" in input else input["type"] for input in inputs]
                func_signature = f"{name}({','.join(func_inputs)})"
                debug_print(f"Collected function signature {func_signature} from ABI")
                func_signatures.append(func_signature)
            return func_signatures

        def get_getter_func_node_from_abi(state_var_name: str) -> Dict[str, Any]:
            abi = data["abi"]  # ["contracts"][contract_file][contract_name]["abi"]
            abi_getter_nodes = [g for g in
                                filter(lambda x: x["type"] == "function" and x["name"] == state_var_name, abi)]

            assert len(abi_getter_nodes) != 0, \
                f"Failed to find a getter function of the state variable {state_var_name} in the ABI"
            assert len(abi_getter_nodes) == 1, \
                f"Found multiple candidates for a getter function of the state variable {state_var_name} in the ABI"

            return abi_getter_nodes[0]

        def collect_array_type_from_abi_rec(type_str: str, dims: List[int]) -> str:
            outer_dim = re.findall(r"\[\d*]$", type_str)
            if outer_dim:
                type_rstrip_dim = re.sub(r"\[\d*]$", '', type_str)
                if len(outer_dim[0]) == 2:
                    dims.append(-1)  # dynamic array
                else:
                    assert len(outer_dim[0]) > 2, f"Expected to find a fixed-size array, but found {type_str}"
                    dims.append(int(re.findall(r"\d+", outer_dim[0])[0]))
                return collect_array_type_from_abi_rec(type_rstrip_dim, dims)
            return type_str

        # Returns (list of array dimensions' lengths, the base type of the array)
        def collect_array_type_from_abi(type_str: str) -> Tuple[List[int], str]:
            dims = []  # type: List[int]
            base_type = collect_array_type_from_abi_rec(type_str, dims)
            return dims, base_type

        # Gets the SolidityType of a function parameter (either input or output) from the ABI
        def get_solidity_type_from_abi(abi_param_entry: Dict[str, Any]) -> SolidityType:
            assert "type" in abi_param_entry, f"Invalid ABI function parameter entry: {abi_param_entry}"

            is_tuple = "components" in abi_param_entry and len(abi_param_entry["components"]) > 0
            if is_tuple:
                components = [get_solidity_type_from_abi(x) for x in abi_param_entry["components"]]
            else:
                components = []

            array_dims, base_type = collect_array_type_from_abi(abi_param_entry["type"])

            internal_type_exists = "internalType" in abi_param_entry
            if internal_type_exists:
                array_dims_internal, internal_base_type = collect_array_type_from_abi(abi_param_entry["internalType"])
                assert array_dims_internal == array_dims
                is_address_alias = base_type == "address" and internal_base_type != base_type
                is_uint8_alias = base_type == "uint8" and internal_base_type != base_type
            else:
                internal_base_type = ""
                is_address_alias = False
                is_uint8_alias = False

            return SolidityType(
                internal_base_type if internal_type_exists else base_type,
                components,
                array_dims,
                False,  # ABI functions cannot have storage references as parameters,
                is_tuple,
                is_address_alias,
                is_uint8_alias,
                # ABI functions never have memory or calldata mappings (only storage pointers)
                False,
                # ABI functions never have function types as arguments/returns
                False,
                # TODO: Do ABI functions ever have enums as arguments?
                False,
                # TODO: Do ABI functions ever have "contracts" as arguments?
                False,
                is_calldata=False,
                solidity_type_declaration=None,
                lib_canonical_signature=None
            )

        def get_func_def_nodes_by_visibility(contract_file_ast: Dict[int, Any], visibility_modifiers: List[str]) -> \
                List[Dict[str, Any]]:
            fun_defs_in_file = [contract_file_ast[node_id] for node_id in filter(
                lambda node_id: "nodeType" in contract_file_ast[node_id] and
                                contract_file_ast[node_id]["nodeType"] == "FunctionDefinition" and
                                (("kind" in contract_file_ast[node_id] and
                                  (contract_file_ast[node_id]["kind"] == "function" or contract_file_ast[node_id][
                                      "kind"] == constructor_string)) or
                                 ("isConstructor" in contract_file_ast[node_id] and
                                  contract_file_ast[node_id]["isConstructor"] is False and
                                  "name" in contract_file_ast[node_id] and
                                  contract_file_ast[node_id]["name"] != "")) and  # Not the fallback function (< solc6)
                                "visibility" in contract_file_ast[node_id] and
                                contract_file_ast[node_id]["visibility"] in visibility_modifiers, contract_file_ast)]

            assert all(self.CERTORA_CONTRACT_NAME() in fd for fd in fun_defs_in_file)

            fun_defs_in_given_contract = [fd for fd in fun_defs_in_file if fd[self.CERTORA_CONTRACT_NAME()] == c_name]
            return fun_defs_in_given_contract

        def get_internal_private_func_def_nodes(contract_file_ast: Dict[int, Any]) -> List[Dict[str, Any]]:
            return get_func_def_nodes_by_visibility(contract_file_ast, ["private", "internal"])

        def get_external_public_func_def_nodes(contract_file_ast: Dict[int, Any]) -> List[Dict[str, Any]]:
            return get_func_def_nodes_by_visibility(contract_file_ast, ["public", "external"])

        def get_func_def_nodes(contract_file_ast: Dict[int, Any]) -> List[Dict[str, Any]]:
            return get_func_def_nodes_by_visibility(contract_file_ast, ["public", "external", "private", "internal"])

        def get_public_state_var_def_nodes(contract_file_ast: Dict[int, Any]) -> List[Dict[str, Any]]:
            public_var_defs_in_file = [contract_file_ast[node_id] for node_id in filter(
                lambda node_id: "nodeType" in contract_file_ast[node_id] and
                                contract_file_ast[node_id]["nodeType"] == "VariableDeclaration" and
                                "visibility" in contract_file_ast[node_id] and
                                contract_file_ast[node_id]["visibility"] == "public" and
                                "stateVariable" in contract_file_ast[node_id] and
                                contract_file_ast[node_id]["stateVariable"] is True, contract_file_ast)]

            assert all(self.CERTORA_CONTRACT_NAME() in vd for vd in public_var_defs_in_file)

            var_defs_in_given_contract = [vd for vd in public_var_defs_in_file if
                                          vd[self.CERTORA_CONTRACT_NAME()] == c_name]
            return var_defs_in_given_contract

        def get_contract_def_node_ref() -> int:
            return self.get_contract_def_node_ref(build_arg_contract_file, contract_file, contract_name)

        def get_original_def_node(reference: int) -> Dict[str, Any]:
            return self.asts[build_arg_contract_file][get_contract_file_of(reference)][reference]

        def get_contract_file_of(reference: int) -> str:
            return self.get_contract_file_of(build_arg_contract_file, reference)

        def get_function_selector(f_entry: Dict[str, Any], f_name: str,
                                  input_types: List[SolidityType]) -> str:
            if "functionSelector" in f_entry:
                return f_entry["functionSelector"]

            f_base = Func.compute_signature(f_name, input_types, lambda x: x.signature())

            assert f_base in data["evm"]["methodIdentifiers"], \
                f"Was about to compute the sighash of {f_name} based on the signature {f_base}.\n" \
                f"Expected this signature to appear in \"methodIdentifiers\"."

            f_hash = keccak.new(digest_bits=256)
            f_hash.update(str.encode(f_base))

            result = f_hash.hexdigest()[0:8]
            expected_result = data["evm"]["methodIdentifiers"][f_base]

            assert expected_result == result, \
                f"Computed the sighash {result} of {f_name} based on a (presumably) correct signature ({f_base}), " \
                f"but got an incorrect result. Expected result: {expected_result}"

            return result

        def collect_array_type_from_type_name_rec(type_name: Dict[str, Any], dims: List[int]) -> Dict[str, Any]:
            """
            Returns the base type (node) of the specified array type, e.g., returns A for A[][3][]
            @param type_name:
            @param dims:
            @return:
            """
            assert "nodeType" in type_name, f"Expected a \"nodeType\" key, but got {type_name}"
            if type_name["nodeType"] == "ArrayTypeName":
                if "length" in type_name:
                    length = type_name["length"]
                    if type(length) is dict and "value" in length:
                        dims.append(int(length["value"]))  # Fixed-size array
                    else:
                        dims.append(-1)  # Dynamic array
                else:  # Dynamic array (in solc7)
                    dims.append(-1)
                assert "baseType" in type_name, f"Expected an array type with a \"baseType\" key, but got {type_name}"
                return collect_array_type_from_type_name_rec(type_name["baseType"], dims)

            return type_name

        def collect_array_type_from_type_name(type_name: Dict[str, Any]) -> Tuple[List[int], Dict[str, Any]]:
            """
            Returns (list of array type dimensions, ast node of the array's base type).
            E.g., Returns ([-1, 3, -1], A) for A[][3][].
            If given a non-array type A, returns ([],A)
            @param type_name:
            @return:
            """
            assert "nodeType" in type_name, f"Expected a \"nodeType\" key, but got {type_name}"
            dims = []  # type: List[int]
            if type_name["nodeType"] == "ArrayTypeName":
                base_type_node = collect_array_type_from_type_name_rec(type_name, dims)
            else:
                base_type_node = type_name
            return dims, base_type_node

        def is_payable_parameter_type(base_type_node: Dict[str, Any]) -> bool:
            if "stateMutability" in base_type_node:
                base_type_node_type = base_type_node.get("nodeType", None)
                assert "name" in base_type_node and base_type_node["name"] == "address" or \
                       base_type_node_type == "FunctionTypeName", \
                    f"Expected an address type, but got {base_type_node}"
                # added this ^, but maybe we should just not process internal functions since they won't have
                # function types in their signature?

                # notably, some fields could have the type of internal function types. we allow it, consider those
                # non payable (it doesn't matter because it inherits from the caller function)
                state_mutability = base_type_node["stateMutability"]
                assert state_mutability == "nonpayable" or \
                       state_mutability == "payable" or \
                       (base_type_node_type == "FunctionTypeName" and
                        base_type_node.get("visibility", None) == "internal"), \
                       f"got state mutability {state_mutability}"

                return state_mutability == "payable"

            return False

        def get_solidity_type_from_ast_param(p: Dict[str, Any]) -> SolidityType:
            assert "typeName" in p, f"Expected a \"typeName\" key, but got {p}"
            (array_dims, base_type_node) = collect_array_type_from_type_name(p["typeName"])

            base_type_is_user_defined = base_type_node["nodeType"] == "UserDefinedTypeName"

            base_type_is_function = base_type_node["nodeType"] == "FunctionTypeName"

            lib_canonical_base_type_str = None  # Used to compute the function sighash in case of a library function
            if base_type_is_user_defined:
                orig_user_defined_type = get_original_def_node(base_type_node["referencedDeclaration"])
                is_valid_node = orig_user_defined_type is not None and "nodeType" in orig_user_defined_type
                is_struct = is_valid_node and orig_user_defined_type["nodeType"] == "StructDefinition"
                is_contract = is_valid_node and orig_user_defined_type["nodeType"] == "ContractDefinition"
                is_enum = is_valid_node and orig_user_defined_type["nodeType"] == "EnumDefinition"
                if c_is_lib:
                    if "canonicalName" in orig_user_defined_type:  # prefer the "canonicalName", if available
                        lib_canonical_base_type_str = orig_user_defined_type["canonicalName"]
                    elif "name" in orig_user_defined_type:
                        lib_canonical_base_type_str = orig_user_defined_type["name"]
            else:
                is_struct = False
                is_contract = False
                is_enum = False

            is_mapping = base_type_node["nodeType"] == "Mapping"
            is_payable_address = is_payable_parameter_type(base_type_node)

            # For a struct parameter, recursively add a solidity type to its components list for each of its members.
            def collect_struct_member_types() -> List[SolidityType]:
                components = []
                if is_struct:
                    struct_def_node_id = base_type_node["referencedDeclaration"]
                    struct_def_node = get_original_def_node(struct_def_node_id)  # type: Dict[str, Any]
                    assert ("nodeType" in struct_def_node and struct_def_node["nodeType"] == "StructDefinition")

                    if not struct_def_node:
                        fatal_error(f"Expected to find a definition of {base_type_str} in the contracts asts")

                    # Proceed recursively on each member of the struct
                    components.extend(
                        [get_solidity_type_from_ast_param(struct_member) for struct_member in
                         struct_def_node["members"]])

                return components

            base_type_str = base_type_node["typeDescriptions"]["typeString"]
            is_storage_ref = p["storageLocation"] == "storage"
            is_calldata_ref = p["storageLocation"] == "calldata"
            solidity_decl = None
            if "pathNode" in base_type_node:
                solidity_decl = base_type_node["pathNode"].get("name", None)
            elif "name" in base_type_node:
                solidity_decl = base_type_node["name"]
            if solidity_decl is not None and type(solidity_decl) == str:
                solidity_decl += "".join(["[]" if dim == -1 else f"[{str(dim)}]" for dim in array_dims])
                if p["storageLocation"] != "default":
                    solidity_decl += f' {p["storageLocation"]}'
            # @Or when we pass is_enum as an argument for the parameter is_uint8 alias, what if it's actually a uint8?
            return SolidityType(base_type_str, collect_struct_member_types(), array_dims, is_storage_ref,
                                is_struct, is_contract or is_payable_address, is_enum, is_mapping,
                                base_type_is_function, is_enum, is_contract,
                                is_calldata=is_calldata_ref,
                                solidity_type_declaration=solidity_decl,
                                lib_canonical_signature=lib_canonical_base_type_str)

        def is_constructor_func(name: str) -> bool:
            # Turns out constructor is a function with no name
            return name == ""

        def is_abi_func(name: str, input_arg_types: List[SolidityType],
                        out_arg_types: List[SolidityType]) -> bool:
            return (is_constructor_func(name) or Func.compute_signature(
                name, input_arg_types, lambda x: x.source_code_signature()
            ) in abi_func_signatures or Func.compute_signature(
                name, input_arg_types, lambda x: x.signature()
            ) in abi_func_signatures) and not (
                # if a function is in library and any argument is of storage, then it's not ABI.
                any([arg.is_storage for arg in input_arg_types]) or any([arg.is_storage for arg in out_arg_types])
            )

        abi_func_signatures = collect_func_source_code_signatures_from_abi()
        funcs = set()
        collected_func_selectors = set()
        # contract_def_node_ref = self.get_contract_def_node_ref(build_arg_contract_file, contract_file, contract_name)
        base_contract_files = self.retrieve_base_contracts_list(
            build_arg_contract_file,
            contract_file,
            contract_name)  # type: List[Tuple[str, str, bool]]
        for c_file, c_name, c_is_lib in base_contract_files:
            if c_is_lib:
                debug_print(f"{c_name} is a library")
            for func_def in get_func_def_nodes(self.asts[build_arg_contract_file][c_file]):
                func_name = func_def["name"]
                func_visibility = func_def["visibility"]
                params = [p for p in func_def["parameters"]["parameters"]]
                solidity_type_args = [get_solidity_type_from_ast_param(p) for p in params]
                is_constructor = is_constructor_func(func_name)

                if not is_constructor and func_visibility in ["public", "external"]:
                    func_selector = get_function_selector(func_def, func_name, solidity_type_args)
                    if func_selector in collected_func_selectors:
                        continue
                    collected_func_selectors.add(func_selector)
                else:
                    # TODO: calculate func_selector for internal functions?
                    func_selector = "0"  # constructor doesn't have calldata (!!) so it doesn't really matter what we
                    # put here

                if is_constructor:
                    func_name = constructor_string

                # Refer to https://github.com/OpenZeppelin/solidity-ast/blob/master/schema.json for more info
                return_params = func_def["returnParameters"]["parameters"]
                solidity_type_outs = [get_solidity_type_from_ast_param(p) for p in return_params]

                is_abi = is_abi_func(func_name, solidity_type_args, solidity_type_outs)
                if func_name == constructor_string and not is_abi:
                    continue  # Skip constructor if it's not part of the ABI.
                    # Solidity does that when inheriting - it adds the parents' constructors to the AST
                    # In principle Solidity allows only 1 constructor function

                body_node = func_def.get("body")
                where_tuple: Optional[Tuple[str, str]] = None
                if body_node is not None and body_node["nodeType"] == "Block":
                    debug_print(f'Found location of body of {func_name} at {body_node["src"]} in {c_file}')
                    where_tuple = (c_file, body_node["src"])
                elif body_node is None and func_def["implemented"]:
                    debug_print(f"No body for {func_def} but ast claims it is implemented")

                func = Func(
                    func_name,
                    solidity_type_args,
                    [p["name"] for p in params],
                    solidity_type_outs,
                    func_selector,
                    func_def["stateMutability"] in ["nonpayable", "view", "pure"],
                    is_abi,
                    c_is_lib,
                    is_constructor,
                    {"keyword": func_def["stateMutability"]},
                    func_visibility,
                    func_def["implemented"],
                    ast_id=func_def.get("id", None),
                    where=where_tuple
                )

                debug_print(f"Looking at Function {func}")

                # TODO: make some notion of contract equality (it *is* possible that two contracts with the same name
                #       but used separately could exist right?
                # Private functions of base contracts/libraries are *not* visible to the current contract
                if func_visibility != "private" or (c_name == contract_name):
                    funcs.add(func)
                    debug_print(f"Function {func.source_code_signature()} added")

                    if not is_abi:
                        debug_print(
                            f"Added an instance of the function {func.source_code_signature()} that is not part of the "
                            f"ABI")

            # Add automatically generated getter functions for public state variables.
            for public_state_var in get_public_state_var_def_nodes(self.asts[build_arg_contract_file][c_file]):
                getter_name = public_state_var["name"]
                debug_print(f"Getter {getter_name} automatically generated")
                getter_abi_data = get_getter_func_node_from_abi(getter_name)

                params = [p for p in getter_abi_data["inputs"]]
                solidity_type_args = [get_solidity_type_from_abi(p) for p in params]

                getter_selector = get_function_selector(public_state_var, getter_name, solidity_type_args)
                if getter_selector in collected_func_selectors:
                    continue
                collected_func_selectors.add(getter_selector)

                return_params = [p for p in getter_abi_data["outputs"]]
                solidity_type_outs = [get_solidity_type_from_abi(p) for p in return_params]

                if "payable" not in getter_abi_data:
                    is_not_payable = False
                else:  # Only if something is definitely non-payable, we treat it as such
                    is_not_payable = not getter_abi_data["payable"]

                if "stateMutability" not in getter_abi_data:
                    state_mutability = "nonpayable"
                else:
                    state_mutability = getter_abi_data["stateMutability"]
                    # in solc6 there is no json field "payable", so we infer that if state_mutability is view or pure,
                    # then we're also non-payable by definition
                    # (state_mutability is also a newer field)
                    if not is_not_payable and state_mutability in ["view", "pure", "nonpayable"]:
                        is_not_payable = True  # definitely not payable

                is_abi = is_abi_func(getter_name, solidity_type_args, solidity_type_outs)

                funcs.add(
                    Func(
                        getter_name,
                        solidity_type_args,
                        [],
                        solidity_type_outs,
                        getter_selector,
                        is_not_payable,
                        is_abi,
                        c_is_lib,
                        isConstructor=False,
                        stateMutability={"keyword": state_mutability},
                        implemented=True,
                        # according to Solidity docs, getter functions have external visibility
                        visibility="external",
                        ast_id=None
                    )
                )
                debug_print(f"Added an automatically generated getter function for {getter_name}")

        collected = [f.source_code_signature() for f in funcs if f.isABI and f.name != constructor_string]
        abi_funcs_cnt = len(collected)
        assert abi_funcs_cnt == len([f for f in abi_func_signatures if not f.startswith(constructor_string)]), \
            f"There are functions in the ABI that were not added. Added functions ({abi_funcs_cnt}): " \
            f"{collected}\n. Functions in ABI ({len(abi_func_signatures)}): {abi_func_signatures}"
        return funcs

    #
    def retrieve_base_contracts_list(self, build_arg_contract_file: str, contract_file: str, contract_name: str) \
            -> List[Tuple[str, str, bool]]:
        """
        For each base contract, returns (base_contract_file, base_contract_name, is_library)
        :param build_arg_contract_file:
        :param contract_file:
        :param contract_name:
        :return: List of (base_contract_file, base_contract_name, is_library)
        """

        def retrieve_base_contracts_list_rec(base_contracts_queue: List[Any],
                                             base_contracts_lst: List[Tuple[str, str, bool]]) -> None:
            (curr_contract_file, curr_contract_def_node_ref) = base_contracts_queue.pop()
            curr_contract_def = self.asts[build_arg_contract_file][curr_contract_file][curr_contract_def_node_ref]
            assert "baseContracts" in curr_contract_def, \
                f'Got a "ContractDefinition" ast node without a "baseContracts" key: {curr_contract_def}'
            for bc in curr_contract_def["baseContracts"]:
                assert "nodeType" in bc and bc["nodeType"] == "InheritanceSpecifier"
                assert "baseName" in bc and "referencedDeclaration" in bc["baseName"]
                next_bc_ref = bc["baseName"]["referencedDeclaration"]
                next_bc = self.get_contract_file_of(build_arg_contract_file, next_bc_ref)
                if next_bc not in base_contracts_lst:
                    base_contracts_lst.append(
                        (next_bc, self.asts[build_arg_contract_file][next_bc][next_bc_ref]["name"],
                         self.is_library_def_node(next_bc, next_bc_ref, build_arg_contract_file)))
                    base_contracts_queue.insert(0, (next_bc, bc["baseName"]["referencedDeclaration"]))

            if base_contracts_queue:
                retrieve_base_contracts_list_rec(base_contracts_queue, base_contracts_lst)

        contract_def_node_ref = self.get_contract_def_node_ref(build_arg_contract_file, contract_file, contract_name)
        base_contracts_queue = [(contract_file, contract_def_node_ref)]
        base_contracts_lst = [
            (contract_file, contract_name,
             self.is_library_def_node(contract_file, contract_def_node_ref, build_arg_contract_file))]
        retrieve_base_contracts_list_rec(base_contracts_queue, base_contracts_lst)
        return base_contracts_lst

    @staticmethod
    def collect_srcmap(data: Dict[str, Any]) -> Any:
        return (data["evm"]["deployedBytecode"]["sourceMap"],
                data["evm"]["bytecode"]["sourceMap"])  # data["contracts"][contract]["srcmap-runtime"]

    @staticmethod
    def collect_varmap(contract: str, data: Dict[str, Any]) -> Any:
        return data["contracts"][contract]["local-mappings"]

    @staticmethod
    def collect_storage_layout(data: Dict[str, Any]) -> Any:
        return data.get("storageLayout", None)

    def get_contract_def_node_ref(self, build_arg_contract_file: str, contract_file: str, contract_name: str) -> int:
        contract_file_ast = self.asts[build_arg_contract_file][contract_file]
        contract_def_refs = [node_id for node_id in filter(
            lambda node_id: "nodeType" in contract_file_ast[node_id] and
                            contract_file_ast[node_id]["nodeType"] == "ContractDefinition" and
                            "name" in contract_file_ast[node_id] and
                            contract_file_ast[node_id]["name"] == contract_name, contract_file_ast)]
        assert len(contract_def_refs) != 0, \
            f'Failed to find a "ContractDefinition" ast node id for the contract {contract_name}'
        assert len(
            contract_def_refs) == 1, f'Found multiple "ContractDefinition" ast node ids for the same contract ' \
                                     f'{contract_name}: {contract_def_refs}'
        return contract_def_refs[0]

    def collect_contract_bytes(self, contract_file: str, contract_name: str, build_arg_contract_file: str) -> \
            Tuple[int, int]:
        ref = self.get_contract_def_node_ref(build_arg_contract_file, contract_file, contract_name)
        node = self.asts[build_arg_contract_file][contract_file][ref]
        src_info = node["src"]
        start, length = src_info.split(":")[0:2]
        return (int(start), int(length))

    def get_standard_json_data(self, sdc_name: str) -> Dict[str, Any]:
        json_file = f"{self.config_path}/{sdc_name}.standard.json.stdout"
        debug_print(f"reading standard json data from {json_file}")
        return read_json_file(json_file)

    @staticmethod
    def address_as_str(address: int) -> str:
        return "%0.40x" % address
        # ^ A 40 digits long hexadecimal string representation of address, filled by leading zeros

    def find_contract_address_str(self, contract_file: str, contract_name: str,
                                  contracts_with_chosen_addresses: List[Tuple[int, Any]]) -> str:
        address_and_contracts = [e for e in contracts_with_chosen_addresses
                                 if e[1] == f"{contract_file}:{contract_name}"]
        if len(address_and_contracts) == 0:
            msg = f"Failed to find a contract named {contract_name} in file {contract_file}. " \
                  f"Please make sure there is a file named like the contract, " \
                  f"or a file containing a contract with this name. Available contracts: " \
                  f"{','.join(map(lambda x: x[1], contracts_with_chosen_addresses))}"
            fatal_error_if_not_library(msg)
        address_and_contract = address_and_contracts[0]
        address = address_and_contract[0]
        contract = address_and_contract[1].split(":")[1]

        debug_print(f"Custom addresses: {self.input_config.address}, looking for a match of "
                    f"{address_and_contract} from {contract_name} in {self.input_config.address.keys()}")
        if contract_name in self.input_config.address.keys():
            address = self.input_config.address[contract_name]
            address = int(str(address), 0)
        debug_print(f"Candidate address for {contract} is {address}")
        # Can't have more than one! Otherwise we will have conflicting same address for different contracts
        assert len(set(address_and_contracts)) == 1
        return self.address_as_str(address)

    def collect_and_link_bytecode(self,
                                  contract_name: str,
                                  contracts_with_chosen_addresses: List[Tuple[int, Any]],
                                  bytecode: str,
                                  links: Dict[str, Any]
                                  ) -> str:
        debug_print(f"Working on contract {contract_name}")
        for address, _contract_name in contracts_with_chosen_addresses:
            if _contract_name == contract_name:
                debug_print("Chosen address for %s is 0x%X" % (contract_name, address))
                break

        if links:
            # links are provided by solc as a map file -> contract -> (length, start)
            # flip the links from the "where" to the chosen contract address (based on file:contract).
            linked_bytecode = bytecode
            replacements = {}
            for link_file in links:
                for link_contract in links[link_file]:
                    for where in links[link_file][link_contract]:
                        replacements[where["start"]] = {"length": where["length"],
                                                        "address": self.find_contract_address_str(
                                                            link_file,
                                                            link_contract,
                                                            contracts_with_chosen_addresses)
                                                        }
            debug_print(f"Replacements= {replacements}")
            where_list = list(replacements.keys())
            where_list.sort()
            where_list.reverse()
            for where in where_list:
                offset = where * 2
                length = replacements[where]["length"] * 2
                addr = replacements[where]["address"]
                debug_print(f"replacing in {offset} of len {length} with {addr}")
                linked_bytecode = f"{linked_bytecode[0:offset]}{addr}{linked_bytecode[(offset + length):]}"
                self.library_addresses.append(addr)
            return linked_bytecode

        return bytecode

    def get_relevant_solc(self, contract: str) -> str:
        if contract in self.input_config.solc_mappings:
            base = self.input_config.solc_mappings[contract]
        else:
            base = self.input_config.solc
        if is_windows() and not base.endswith(".exe"):
            base = base + ".exe"
        debug_print(f"relevant solc is {base}")
        return base

    def get_extra_solc_args(self) -> str:
        if self.input_config.solc_args is not None:
            extra_solc_args = ' '.join(self.input_config.solc_args)
            return extra_solc_args
        return ""

    def standard_json(self, contract_file: str, remappings: List[str]) -> Dict[str, Any]:
        """
        when calling solc with the standard_json api, instead of passing it flags, we pass it json to request what we
        want -- currently we only use this to retrieve storage layout as this is the only way to do that,
        it would probably be good to migrate entirely to this API.
        @param contract_file:
        @param remappings:
        @return:
        """
        sources_dict = {contract_file: {"urls": [contract_file]}}
        solc_args = self.get_extra_solc_args()
        settings_dict = \
            {
                "remappings": remappings,
                "outputSelection": {
                    "*": {
                        "*": ["storageLayout", "abi", "evm.bytecode", "evm.deployedBytecode", "evm.methodIdentifiers",
                              "evm.assembly"],
                        "": ["id", "ast"]
                    }
                }
            }

        def split_arg_hack(arg_name: str, args_: str) -> str:
            return args_.split(arg_name)[1].strip().split(" ")[0].strip()  # String-ops FTW

        EVM_VERSION = "--evm-version"
        OPTIMIZE = "--optimize"
        OPTIMIZE_RUNS = "--optimize-runs"

        if EVM_VERSION in solc_args:
            evmVersion = split_arg_hack(EVM_VERSION, solc_args)
            settings_dict["evmVersion"] = evmVersion
        if OPTIMIZE in solc_args or OPTIMIZE_RUNS in solc_args:
            enabled = OPTIMIZE in solc_args
            if OPTIMIZE_RUNS in solc_args:
                runs = int(split_arg_hack(OPTIMIZE_RUNS, solc_args))
                settings_dict["optimizer"] = {"enabled": enabled, "runs": runs}
            else:
                settings_dict["optimizer"] = {"enabled": enabled}

        result_dict = {"language": "Solidity", "sources": sources_dict, "settings": settings_dict}
        # debug_print("Standard json input")
        # debug_print(json.dumps(result_dict, indent=4))
        return result_dict

    def get_compilation_path(self, sdc_name: str) -> str:
        return "%s/%s" % (self.config_path, sdc_name)

    def build_srclist(self, data: Dict[str, Any], sdc_name: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Generates lists of sources for the given Single Deployed Contract.
        :param data: data from the json produced by the solidity compiler
        :param sdc_name: name of the "Single Deployed Contract" whose sources we are gathering
        :return: Two versions of the source list. The first version is the source list as seen by solc. The second is
                 modified: the path except for the name of the file is removed, and an index is prepended to make later
                 use in managing report source mappings easier
        """
        # srclist - important for parsing source maps
        srclist = {data["sources"][k]["id"]: k for k in data["sources"]}
        debug_print(f"Source list= {srclist}")

        report_srclist = {}

        map_idx_in_src_list_to_orig_file = {v: k for k, v in srclist.items()}
        for orig_file in map_idx_in_src_list_to_orig_file:
            idx_in_src_list = map_idx_in_src_list_to_orig_file[orig_file]

            # Copy contract_file to compilation path directory
            new_name = f"{idx_in_src_list}_{get_file_basename(orig_file)}.{get_file_extension(orig_file)}"
            shutil.copy2(orig_file,
                         f'{self.get_compilation_path(sdc_name)}/{new_name}')
            fetched_source = f'{sdc_name}/{new_name}'

            report_srclist[idx_in_src_list] = fetched_source

        return srclist, report_srclist

    def collect_asts(self, original_file: str, contract_sources: Dict[str, Dict[str, Any]]) -> None:
        """
        This function fetches the AST provided by solc and flattens it so that each node_id is mapped to a dict object,
        representing the node's contents.

        @param original_file: Path to a file
        @param contract_sources: represents the AST. Every sub-object with an "id" key is an AST node.
                                 The ast object is keyed by the original file for which we invoked solc.
        """

        def stamp_value_with_contract_name(popped_dict: Dict[str, Any], curr_value: Any) -> None:
            if isinstance(curr_value, dict):
                if popped_dict["nodeType"] == "ContractDefinition":
                    assert "name" in popped_dict
                    curr_value[self.CERTORA_CONTRACT_NAME()] = popped_dict["name"]
                elif self.CERTORA_CONTRACT_NAME() in popped_dict:
                    curr_value[self.CERTORA_CONTRACT_NAME()] = popped_dict[self.CERTORA_CONTRACT_NAME()]
            elif isinstance(curr_value, list):
                for node in curr_value:
                    stamp_value_with_contract_name(popped_dict, node)

        self.asts[original_file] = {}
        for c in contract_sources:
            debug_print(f"Adding ast of {original_file} for {c}")
            container = {}  # type: Dict[int, Any]
            self.asts[original_file][c] = container
            if "ast" not in contract_sources[c]:
                fatal_error_if_not_library(
                    f"Invalid AST format for original file {original_file} - "
                    f"got object that does not contain an \"ast\" {contract_sources[c]}")
            queue = [contract_sources[c]["ast"]]
            while queue:
                pop = queue.pop(0)
                if isinstance(pop, dict) and "id" in pop:
                    container[int(pop["id"])] = pop
                    for key, value in pop.items():
                        if "nodeType" in pop and pop["nodeType"] == "InlineAssembly" and key == "externalReferences":
                            continue
                        stamp_value_with_contract_name(pop, value)
                        if isinstance(value, dict):
                            queue.append(value)
                        if isinstance(value, list):
                            queue.extend(value)

    @staticmethod
    def get_node_from_asts(asts: Dict[str, Dict[str, Dict[int, Any]]], original_file: str, node_id: int) -> Any:
        debug_print(f"Available keys in ASTs: {asts.keys()}")
        debug_print(f"Available keys in AST of original file: {asts[original_file].keys()}")
        for contract_file in asts[original_file]:
            node = asts[original_file].get(contract_file, {}).get(node_id)
            if node is not None:
                debug_print(f"In original file {original_file} in contract file {contract_file}, found for node id "
                            f"{node_id}")
                return node  # Found the ast node of the given node_id
        return {}  # an ast node with the given node_id was not found

    def collect_immutables(self,
                           contract_data: Dict[str, Any],
                           build_arg_contract_file: str
                           ) -> List[ImmutableReference]:
        out = []
        immutable_references = contract_data["evm"]["deployedBytecode"].get("immutableReferences", [])
        # Collect and cache the AST(s). We collect the ASTs of ALL contracts' files that appear in
        # contract_sources; the reason is that a key of an item in immutableReferences
        # is an id of an ast node that may belong to any of those contracts.
        debug_print(f"Got immutable references in {build_arg_contract_file}: {immutable_references}")
        for astnode_id in immutable_references:
            astnode = self.get_node_from_asts(self.asts, build_arg_contract_file, int(astnode_id))
            name = astnode.get("name", None)
            if name is None:
                fatal_error_if_not_library(
                    f"immutable reference does not point to a valid ast node {astnode} in {build_arg_contract_file}, "
                    f"node id {astnode_id}"
                )

            debug_print(f"Name of immutable reference is {name}")
            for elem in immutable_references[astnode_id]:
                out.append(ImmutableReference(elem["start"], elem["length"], name))
        return out

    def address_generator(self) -> int:
        # 12,14,04,06,00,04,10 is 0xce4604a aka certora.
        const = (12 * 2 ** 24 + 14 * 2 ** 20 + 4 * 2 ** 16 + 6 * 2 ** 12 + 0 + 4 * 2 ** 4 + 10 * 2 ** 0)
        address = const * 2 ** 100 + self.address_generator_idx
        # Don't forget for addresses there are only 160 bits
        self.address_generator_idx += 1
        return address

    @staticmethod
    def check_for_errors_and_warnings(data: Dict[str, Any]) -> None:
        severe_compiler_warnings = ["6321"]
        """ 6321 - "Unnamed return variable can remain unassigned"
              - emitted by solc versions 0.7 and up """
        if "errors" in data:
            errors_list = data["errors"]
            severe_errors = [e for e in errors_list if "errorCode" in e and e["errorCode"] in severe_compiler_warnings]
            for e in severe_errors:
                msg = e["formattedMessage"]
                print(f"Severe compiler warning: {msg}\nPlease fix this warning before running the Certora prover")
            if len(severe_errors) > 0:
                exit_if_not_library(1)

    def collect_for_file(self, build_arg_contract_file: str,
                         file_index: int,
                         provided_remappings: Optional[List[str]] = None,
                         debug: bool = False,
                         fail_on_compilation_error: bool = True) -> SDC:
        if provided_remappings is None:
            provided_remappings = []
        primary_contract = self.input_config.fileToContractName[build_arg_contract_file]
        sdc_name = f"{build_arg_contract_file.split('/')[-1]}_{file_index}"
        compilation_path = self.get_compilation_path(sdc_name)
        safe_create_dir(compilation_path, debug=debug)

        solc_ver_to_run = self.get_relevant_solc(primary_contract)
        file_abs_path = abs_posix_path(build_arg_contract_file)

        # ABI and bin-runtime cmds preparation
        if self.input_config.packages is not None:
            remappings = self.input_config.packages
            debug_print(f"remappings={remappings}")
            paths_for_remappings = list(map(lambda remap: remap.split("=")[1], remappings))
            debug_print(f"paths_for_remappings={paths_for_remappings}\n")

            join_remappings = ','.join(paths_for_remappings)

            debug_print(f"Join remappings: {join_remappings}\n")
            collect_cmd = f"{solc_ver_to_run} -o {compilation_path}/ --overwrite " \
                          f"--allow-paths {self.input_config.path},{join_remappings},. --standard-json"
        else:
            remappings = []
            collect_cmd = f"{solc_ver_to_run} -o {compilation_path}/ --overwrite " \
                          f"--allow-paths {self.input_config.path},. --standard-json"

        remappings = remappings + provided_remappings

        # Standard JSON
        input_for_solc = self.standard_json(file_abs_path, remappings)
        standard_json_input = json.dumps(input_for_solc).encode("utf-8")
        debug_print(f"about to run {collect_cmd}")
        debug_print(f"solc input = {json.dumps(input_for_solc, indent=4)}")
        run_cmd(collect_cmd, f"{sdc_name}.standard.json", self.config_path, input=standard_json_input,
                shell=False, debug=DEBUG)

        debug_print(f"Collecting standard json: {collect_cmd}")
        standard_json_data = self.get_standard_json_data(sdc_name)

        for error in standard_json_data.get("errors", []):
            # is an error not a warning
            if error.get("severity", None) == "error":
                debug_print(f"Error: standard-json invocation of solc encountered an error: {error}")
                friendly_message = f"Got error from {solc_ver_to_run} of type {error['type']}:\n" \
                                   f"{error['formattedMessage']}"
                if fail_on_compilation_error:
                    fatal_error_if_not_library(friendly_message)
                else:
                    raise SolcCompilationException(friendly_message)

        # load data
        data = standard_json_data  # Note we collected for just ONE file
        self.check_for_errors_and_warnings(data)
        self.collect_asts(build_arg_contract_file, data["sources"])
        contracts_with_libraries = {}
        # Need to add all library dependencies that are in a different file:
        seen_link_refs = {file_abs_path}
        contract_work_list = [file_abs_path]
        while contract_work_list:
            contract_file = contract_work_list.pop()
            contract_list = sorted([c for c in data["contracts"][contract_file]])
            contracts_with_libraries[contract_file] = contract_list

            for contract_name in contract_list:
                base_contracts = self.retrieve_base_contracts_list(build_arg_contract_file, contract_file,
                                                                   contract_name)
                for c_file, _, _ in base_contracts:
                    if c_file not in seen_link_refs:
                        contract_work_list.append(c_file)
                        seen_link_refs.add(c_file)

                contract_object = data["contracts"][contract_file][contract_name]
                link_refs = contract_object["evm"]["deployedBytecode"]["linkReferences"]
                for link_ref in link_refs:
                    if link_ref not in seen_link_refs:
                        contract_work_list.append(link_ref)
                        seen_link_refs.add(link_ref)
                internal_refs = self.get_libraries_referenced_with_internal_functions(build_arg_contract_file,
                                                                                      contract_file, contract_name)
                for ref in internal_refs:
                    contract_files = [c_file for c_file in data["contracts"].keys() if
                                      ref in data["contracts"][c_file].keys()]
                    assert len(set(contract_files)) == 1, f'{ref}, {contract_files}'
                    link_ref = contract_files[0]
                    if link_ref not in seen_link_refs:
                        contract_work_list.append(link_ref)
                        seen_link_refs.add(link_ref)

        debug_print(
            f"Contracts in {sdc_name} (file {build_arg_contract_file}): {contracts_with_libraries[file_abs_path]}")
        contracts_with_chosen_addresses = \
            [(self.address_generator(), f"{contract_file}:{contract_name}") for contract_file, contract_list in
             sorted(contracts_with_libraries.items(), key=lambda entry: entry[0]) for contract_name in
             contract_list]  # type: List[Tuple[int, Any]]

        debug_print(f"Contracts with their chosen addresses: {contracts_with_chosen_addresses}")

        srclist, report_srclist = self.build_srclist(data, sdc_name)
        report_source_file = report_srclist[[idx for idx in srclist if srclist[idx] == contract_file][0]]
        contracts_in_sdc = []
        debug_print(f"finding primary contract address of {file_abs_path}:{primary_contract} in "
                    f"{contracts_with_chosen_addresses}")
        primary_contract_address = \
            self.find_contract_address_str(file_abs_path,
                                           primary_contract,
                                           contracts_with_chosen_addresses)
        debug_print(f"For contracts of primary {primary_contract}")

        for contract_file, contract_list in contracts_with_libraries.items():
            for contract_name in contract_list:
                contract_in_sdc = self.get_contract_in_sdc(
                    contract_file,
                    contract_name,
                    contracts_with_chosen_addresses,
                    data,
                    report_source_file,
                    primary_contract,
                    build_arg_contract_file
                )
                contracts_in_sdc.append(contract_in_sdc)

        debug_print(f"Contracts in SDC {sdc_name}: {[contract.name for contract in contracts_in_sdc]}")

        # Need to deduplicate the library_addresses list without changing the order
        deduplicated_library_addresses = list(OrderedDict.fromkeys(self.library_addresses))
        sdc = SDC(primary_contract,
                  primary_contract_address,
                  build_arg_contract_file,
                  srclist,
                  report_srclist,
                  sdc_name,
                  contracts_in_sdc,
                  deduplicated_library_addresses,
                  ' '.join(sys.argv),
                  {},
                  {})
        self.library_addresses.clear()  # Reset library addresses
        return sdc

    def get_bytecode(self,
                     bytecode_object: Dict[str, Any],
                     contract_name: str,
                     primary_contract: str,
                     contracts_with_chosen_addresses: List[Tuple[int, Any]],
                     fail_if_no_bytecode: bool
                     ) -> str:
        """
        Computes the linked bytecode object from the Solidity compiler output.
        First fetches the bytecode objects and then uses link references to replace library addresses.

        @param bytecode_object - the output from the Solidity compiler
        @param contract_name - the contract that we are working on
        @param contracts_with_chosen_addresses - a list of tuples of addresses and the
            associated contract identifier
        @param fail_if_no_bytecode - true if the function should fail if bytecode object is missing,
            false otherwise
        @returns linked bytecode object
        """
        # TODO: Only contract_name should be necessary. This requires a lot more test cases to make sure we're not
        # missing any weird solidity outputs.
        bytecode_ = bytecode_object["object"]
        bytecode = self.collect_and_link_bytecode(contract_name, contracts_with_chosen_addresses,
                                                  bytecode_, bytecode_object["linkReferences"])
        if contract_name == primary_contract and len(bytecode) == 0:
            msg = f"Contract {contract_name} has no bytecode. " \
                  f"It may be caused because the contract is abstract, " \
                  f"or is missing constructor code. Please check the output of the Solidity compiler."
            if fail_if_no_bytecode:
                fatal_error_if_not_library(f"Error: {msg}")
            else:
                debug_print(f"Warning: {msg}")

        return bytecode

    def get_contract_in_sdc(self,
                            contract_file: str,
                            contract_name: str,
                            contracts_with_chosen_addresses: List[Tuple[int, Any]],
                            data: Dict[str, Any],
                            report_source_file: str,
                            primary_contract: str,
                            build_arg_contract_file: str
                            ) -> ContractInSDC:
        contract_data = data["contracts"][contract_file][contract_name]
        debug_print(f"Contract {contract_name} is in file {contract_file}")
        funcs = self.collect_funcs(contract_data, contract_file, contract_name, build_arg_contract_file)
        external_funcs = {f for f in funcs if f.visibility in ['external', 'public']}
        public_funcs = {f for f in funcs if f.visibility in ['public']}
        internal_funcs = {f for f in funcs if f.visibility in ['private', 'internal']}

        source_size = self.collect_contract_bytes(contract_file, contract_name, build_arg_contract_file)
        debug_print(f"Source bytes of {contract_name}: {source_size}")

        debug_print(f"Internal Functions of {contract_name}: {[fun.name for fun in internal_funcs]}")
        debug_print(f"Functions of {contract_name}: {[fun.name for fun in funcs]}")
        (srcmap, constructor_srcmap) = self.collect_srcmap(contract_data)

        varmap = ""
        deployed_bytecode = self.get_bytecode(contract_data["evm"]["deployedBytecode"], contract_name, primary_contract,
                                              contracts_with_chosen_addresses, True)
        constructor_bytecode = self.get_bytecode(contract_data["evm"]["bytecode"], contract_name, primary_contract,
                                                 contracts_with_chosen_addresses, False)
        address = self.find_contract_address_str(contract_file,
                                                 contract_name,
                                                 contracts_with_chosen_addresses)
        storage_layout = \
            self.collect_storage_layout(contract_data)
        immutables = self.collect_immutables(contract_data, build_arg_contract_file)

        if self.input_config.function_finders is not None:
            all_internal_functions: Dict[str, Any] = \
                read_json_file(self.input_config.function_finders)
            debug_print_(f"Found all internal functions {all_internal_functions}")
            if contract_name in all_internal_functions:
                function_finders = all_internal_functions[contract_name]
            else:
                function_finders = {}
        else:
            function_finders = {}

        debug_print(f"Found internal functions for contract {contract_name}: {function_finders}")

        return ContractInSDC(contract_name,
                             contract_file,
                             report_source_file,
                             address,
                             external_funcs,
                             deployed_bytecode,
                             constructor_bytecode,
                             srcmap,
                             varmap,
                             constructor_srcmap,
                             storage_layout,
                             immutables,
                             function_finders,
                             internal_funcs=internal_funcs,
                             public_funcs=public_funcs,
                             source_bytes=source_size
                             )

    @staticmethod
    def get_sdc_key(contract: str, address: str) -> str:
        return f"{contract}_{address}"

    @staticmethod
    def get_primary_contract_from_sdc(contracts: List[ContractInSDC], primary: str) -> List[ContractInSDC]:
        return [x for x in contracts if x.name == primary]

    @staticmethod
    def generate_library_import(file_absolute_path: str, library_name: str) -> str:
        return f"\nimport {'{'}{library_name}{'}'} from '{file_absolute_path}';"

    def generate_assembly_finder(self, f: Func, internal_id: int, sym: int, version: Tuple[int, int, int]) -> \
            Optional[str]:
        def gen_key(flag: int) -> str:
            return f'0xffffff6e4604afefe123321beef1b01fffffffffffffffffffffffff{"%0.4x" % internal_id}{"%0.4x" % flag}'

        def is_opcode(v_name: str) -> bool:
            return v_name in {"stop", "add", "sub", "mul", "div", "sdiv", "mod", "smod", "exp", "not", "lt", "gt",
                              "slt", "sgt", "eq", "iszero", "and", "or", "xor", "byte", "shl", "shr", "sar", "addmod",
                              "mulmod", "signextend", "keccak256", "pc", "pop", "mload", "mstore", "mstore8", "sload",
                              "sstore", "msize", "gas", "address", "balance", "selfbalance", "caller", "callvalue",
                              "calldataload", "calldatasize", "calldatacopy", "codesize", "codecopy", "extcodesize",
                              "extcodecopy", "returndatasize", "returndatacopy", "extcodehash", "create", "create2",
                              "call", "callcode", "delegatecall", "staticcall", "return", "revert", "selfdestruct",
                              "invalid", "log0", "log1", "log2", "log3", "log4", "chainid", "basefee", "origin",
                              "gasprice", "blockhash", "coinbase", "timestamp", "number", "difficulty", "gaslimit"}

        alpha_renaming = ""
        to_ret = "\nassembly {\n"
        to_ret += f"mstore({gen_key(0)}, {sym})\n"
        num_arg_symbols = 0
        for arg_ty in f.fullArgs:
            num_arg_symbols += 1
            if arg_ty.is_calldata and (arg_ty.array_dims[0:1] == [-1] or arg_ty.base_type in {"string", "bytes"}):
                num_arg_symbols += 1
        to_ret += f"mstore({gen_key(1)}, {num_arg_symbols})\n"
        for i in range(0, len(f.fullArgs)):
            arg_name = f.argNames[i]
            ty = f.fullArgs[i]
            if is_opcode(arg_name):
                if ty.solidity_type_declaration is None:
                    debug_print(f"Need to rename {arg_name} with type {ty}, but it doesn't have a type declaration")
                    return None
                renamed = f"certoraRename{internal_id}_{i}"
                alpha_renaming += f"{ty.solidity_type_declaration} {renamed} = {arg_name};\n"
                arg_name = renamed

            if ty.is_calldata and (ty.array_dims[0:1] == [-1] or ty.base_type in {"string", "bytes"}):
                if (version[1] > 7 or (version[1] == 7 and version[2] >= 5)) and arg_name != "":
                    len_flag = 0x2000 + i
                    offset_flag = 0x3000 + i
                    # special encoding
                    to_ret += f"mstore({gen_key(len_flag)}, {arg_name}.length)\n"
                    to_ret += f"mstore({gen_key(offset_flag)}, {arg_name}.offset)\n"
                    continue
                else:
                    # place holder
                    to_ret += f"mstore({gen_key(0x4000 + i)}, 0)\n"
                    continue
            if len(arg_name) == 0:
                to_ret += f"mstore({gen_key(0x5000 + i)}, 0)\n"
                continue
            flag = 0x1000 + i
            if ty.is_storage:
                if version[0] == 0 and version[1] < 7:
                    suff = "_slot"
                else:
                    suff = ".slot"
                arg = f"{arg_name}{suff}"
            else:
                arg = f"{arg_name}"
            to_ret += f"mstore({gen_key(flag)}, {arg})\n"
        to_ret += "}"
        return alpha_renaming + to_ret

    def add_auto_finders(self, contract_file: str, sdc: SDC) -> \
            Optional[Tuple[Dict[str, str], Dict[str, Dict[int, Instrumentation]]]]:
        function_finder_by_contract: Dict[str, str] = dict()
        contracts = sdc.contracts
        # contract file -> byte offset -> to insert
        function_finder_instrumentation: Dict[str, Dict[int, Instrumentation]] = dict()
        for c in contracts:
            debug_print(f"visiting contract {c.name}")
            out_name = f"version_check_{c.name}"
            debug_print(f"Checking solidity version for {c.name} for sdc {sdc.primary_contract}")
            run_cmd(
                f"{self.get_relevant_solc(sdc.primary_contract)} --version",
                name=out_name, config_path=self.config_path)
            with open(f"{self.config_path}/{out_name}.stdout", "r") as r:
                version_string = r.read(-1)
            version_matches = [(int(m.group(1)), int(m.group(2)), int(m.group(3))) for m in
                               [re.match(r'^(\d+)\.(\d+).(\d+)', l[len("Version: "):]) for l in
                                version_string.splitlines() if l.startswith("Version: ")] if m is not None]
            if len(version_matches) != 1:
                debug_print(f"Couldn't extract solidity version from output {version_string}, giving up")
                return None
            version = version_matches[0]
            debug_print(f"Inferred {version} for contract {c.name}")
            for f in c.internal_funcs.union(c.public_funcs):
                if f.isConstructor:
                    continue
                loc = f.where
                if loc is None:
                    if not f.implemented:
                        continue
                    debug_print(f"Found an (implemented) function {f.name} in {c.name} that doesn't have a location")
                    return None
                if loc[0] not in function_finder_instrumentation:
                    function_finder_instrumentation[loc[0]] = dict()
                if len(f.fullArgs) != len(f.argNames):
                    print_warning(f"Do not have argument names for {f.name} in {c.name}, giving up auto finders")
                    return None
                per_file_inst = function_finder_instrumentation[loc[0]]

                start_byte = int(loc[1].split(":")[0])
                # suuuuch a hack
                if start_byte in per_file_inst:
                    continue

                if f.ast_id is None:
                    debug_print(f"No ast_id for function {f}, giving up here")
                    return None
                def_node = self.asts[contract_file].get(loc[0], dict()).get(f.ast_id, None)
                if def_node is None or type(def_node) != dict:
                    debug_print(f"Failed to find def node for {f} {def_node} {f.ast_id}")
                    return None
                mods = def_node.get("modifiers", [])  # type: List[Dict[str, Any]]

                internal_id = self.function_finder_generator_idx
                self.function_finder_generator_idx += 1
                function_symbol = 0xf196e50000 + internal_id
                function_finder_by_contract["0x%x" % function_symbol] = f.source_code_signature()
                finder_string = self.generate_assembly_finder(f, internal_id, function_symbol, version)
                if finder_string is None:
                    debug_print(f"Generating auto finder for {f.name} @ {f.where} failed, giving up generation")
                    return None

                if len(mods) > 0:
                    # we need to add the instrumentation in a modifer because solidity modifiers will (potentially)
                    # appear before any instrumentation we add to the literal source body, which will tank the detection
                    # process. We cannot instrument the modifiers directly because they can be shared among multiple
                    # implementations.
                    #
                    # Q: Why not always instrument with modifiers?
                    # A: Without modifiers already present, the solidity AST makes it extremely difficult to figure out
                    # where in the source such modifiers will go. In order to insert a modifier, we have to have at
                    # least one modifier already present, and then insert before the first modifier's location in the
                    # source code
                    modifier_name = f"internalLog{str(internal_id)}"
                    arg_with_types = zip(f.fullArgs, f.argNames)
                    if any(map(lambda k: k.solidity_type_declaration is None, f.fullArgs)):
                        debug_print(f"Can't get type string for arguments of {f.name} @ {f.where}")
                        return None
                    arg_list = ", ".join([f"{ty.solidity_type_declaration} {name}" for ty, name in arg_with_types])
                    modifier_def = f"""
                    modifier {modifier_name}({arg_list}) {{
                       {finder_string}
                       _;
                    }}\n
                    """
                    func_def_start_str = def_node.get("src", None)
                    if func_def_start_str is None or type(func_def_start_str) != str:
                        debug_print(f"Could not get source information for function {f.name} @ {f.where}")
                        return None
                    func_start_byte = int(func_def_start_str.split(":")[0])
                    per_file_inst[func_start_byte] = Instrumentation(expected=b'f', to_ins=modifier_def, before=True)

                    if any(map(lambda mod: mod.get("nodeType", None) != "ModifierInvocation" or
                               type(mod.get("src", None)) != str, mods)):
                        debug_print(f"Unrecognized modifier AST node for {f.name} @ {f.where}")
                        return None
                    first_mod = min(mods, key=lambda mod: int(mod["src"].split(":")[0]))
                    modifier_invocation = f"""{modifier_name}({", ".join(f.argNames)}) """
                    modifier_name = first_mod.get("modifierName", dict()).get("name", None)
                    if type(modifier_name) != str:
                        debug_print(f"Can't infer expected name for modififer "
                                    f"{modifier_invocation} for {f.name} @ {f.where}")
                        return None
                    first_mod_offset = int(first_mod["src"].split(":")[0])
                    per_file_inst[first_mod_offset] = Instrumentation(expected=bytes(modifier_name[0:1], "utf-8"),
                                                                      to_ins=modifier_invocation, before=True)
                else:
                    per_file_inst[start_byte] = Instrumentation(expected=b'{', to_ins=finder_string, before=False)
        return function_finder_by_contract, function_finder_instrumentation

    def cleanup(self) -> None:
        for f in self.generated_files:
            if os.path.isfile(f):
                remove_file(f)

    def get_all_function_call_refs(self, contract_file_ast: Dict[int, Any], contract_name: str) -> List[int]:
        return [int(contract_file_ast[node_id]["expression"]["referencedDeclaration"]) for node_id in
                contract_file_ast if
                "nodeType" in contract_file_ast[node_id] and contract_file_ast[node_id][
                    "nodeType"] == "FunctionCall" and "expression" in contract_file_ast[
                    node_id] and "referencedDeclaration" in contract_file_ast[node_id]["expression"].keys() and
                # a referencedDeclaration could be null
                contract_file_ast[node_id]["expression"]["referencedDeclaration"] is not None and
                contract_file_ast[node_id][self.CERTORA_CONTRACT_NAME()] == contract_name]

    def get_libraries_referenced_with_internal_functions(self, build_arg_contract_file: str, contract_file: str,
                                                         contract_name: str) -> List[str]:
        ast = self.asts[build_arg_contract_file][contract_file]
        referenced_functions = self.get_all_function_call_refs(ast, contract_name)
        referenced_nodes = [self.get_node_from_asts(self.asts, build_arg_contract_file, node_id) for
                            node_id in referenced_functions]
        # some referenced function calls could be builtins like require, whose declarations we do not see
        return [node[self.CERTORA_CONTRACT_NAME()] for node in referenced_nodes if self.CERTORA_CONTRACT_NAME() in node]

    @staticmethod
    def __find_closest_methods(method_name: str, methods: List[Func]) -> List[str]:
        """
        Gets a name of a method and a list of existing methods. Returns a list of closest matching method signatures.
        The match is performed on the name only, ignoring the parameters in the function.
        :param method_name: Name of a method
        :param methods: A list of possible methods.
        :return: An list of best suggested method signatures as replacement. Ordered by descending relevance.
        """
        # Step 1: find closest method names
        all_method_names = [method.name for method in methods]
        all_method_names = list(set(all_method_names))  # remove duplicate names
        possible_method_names = get_closest_strings(method_name, all_method_names)

        # Step 2: fetch the parameters of closest matching method names
        possible_methods = list()
        for name in possible_method_names:
            for method in methods:
                if method.name == name:
                    possible_methods.append(method.signature())
        return possible_methods

    @staticmethod
    def __suggest_methods(wrong_sig: str, suggested_replacements: List[str]) -> None:
        """
        Raises an error suggesting replacement methods for an erroneous signature.
        :param wrong_sig: A method signature as inserted by the user. Had no exact matches in the code.
        :param suggested_replacements: A list of suggested method signatures, ordered by descending relevance
        :raises: AttributeError always
        """
        if len(suggested_replacements) == 0:
            raise AttributeError(f"Method {wrong_sig} was not found.")

        if len(suggested_replacements) == 1:
            options_str = suggested_replacements[0]
        elif len(suggested_replacements) == 2:
            options_str = " or ".join(suggested_replacements)
        elif len(suggested_replacements) > 2:
            # Code below adds or after the last comma if there are multiple options
            options_str = ", ".join(suggested_replacements)
            last_commas_location_regex = r"(?<=,)(?=[^,]*$)"
            options_str = re.sub(last_commas_location_regex, r" or", options_str)

        raise AttributeError(f"Method {wrong_sig} was not found. Maybe you meant {options_str}?")

    def __verify_method(self, method_input: str, sdc_pre_finder: SDC) -> None:
        input_method_name = method_input.split('(')[0]
        input_method_sig = method_input.replace(' ', '')

        '''
        A list of suggested methods, in case the user inserted a wrong method signature. Only public/external methods
        are suggested to the user. The suggestions are ordered by closest match - index zero is the best match, and
        descending.
        '''
        possible_methods = list()

        # Step #1 - check if an exact match exists. If not, check if only the parameters were wrong in the signature

        public_method_sets = [contract.methods for contract in sdc_pre_finder.contracts]
        public_methods = flatten_set_list(public_method_sets)

        for method in public_methods:
            if method.name == input_method_name:  # Correct name, now we check parameter types
                if method.signature() == input_method_sig:  # An exact match was found
                    return

                # A method with the same name but different parameters exists
                possible_methods.append(method.signature())

        # Now we check if the method exists, but is private or external
        private_method_sets = [contract.internal_funcs for contract in sdc_pre_finder.contracts]
        private_methods = flatten_set_list(private_method_sets)

        for method in private_methods:
            if method.name == input_method_name:  # Correct name, now we check parameter types
                if method.signature() == input_method_sig:  # An exact match was found
                    raise AttributeError(
                        f"Method {input_method_sig} is {method.visibility}. Please change it to external or public")

        # We suggest a different method name, if we have a good enough suggestion

        # A method with correct name but wrong argument types takes precedence over a method with a different name
        if len(possible_methods) == 0:
            possible_methods = self.__find_closest_methods(input_method_name, public_methods)

        if len(possible_methods) > 0:  # We have suggestions
            self.__suggest_methods(method_input, possible_methods)

        raise AttributeError(f"Method {method_input} was not found")

    def build(self, args: argparse.Namespace) -> None:

        for i, build_arg_contract_file in enumerate(sorted(self.input_config.files)):
            debug_print(f"\nbuilding file {build_arg_contract_file}")
            sdc_pre_finder = self.collect_for_file(build_arg_contract_file, i, debug=self.input_config.debug)
            if args.method and build_arg_contract_file in args.verified_contract_files:
                self.__verify_method(args.method, sdc_pre_finder)

            added_finders, sdc = self.instrument_auto_finders(build_arg_contract_file, i, sdc_pre_finder)

            for contract in sdc.contracts:
                for k, v in added_finders.items():
                    contract.function_finders[k] = v

            # First, add library addresses as SDCs too (they should be processed first)
            debug_print(f"Libraries to add = {sdc.library_addresses}")
            for library_address in sdc.library_addresses:
                library_contract_candidates = [contract for contract in sdc.contracts
                                               if contract.address == library_address]
                if len(library_contract_candidates) != 1:
                    fatal_error_if_not_library(
                        f"Error: Expected to have exactly one library address for {library_address}, "
                        f"got {library_contract_candidates}")

                library_contract = library_contract_candidates[0]
                debug_print(f"Found library contract {library_contract}")
                # TODO: What will happen to libraries with libraries?
                sdc_lib = SDC(library_contract.name,
                              library_address,
                              library_contract.original_file,
                              sdc.original_srclist,
                              sdc.report_srclist,
                              f"{sdc.sdc_name}_{library_contract.name}",
                              self.get_primary_contract_from_sdc(sdc.contracts, library_contract.name),
                              [],
                              sdc.generated_with,
                              {},
                              {})
                self.SDCs[self.get_sdc_key(sdc_lib.primary_contract, sdc_lib.primary_contract_address)] = sdc_lib

            # Filter out irrelevant contracts, now that we extracted the libraries, leave just the primary
            sdc.contracts = self.get_primary_contract_from_sdc(sdc.contracts, sdc.primary_contract)
            self.SDCs[self.get_sdc_key(sdc.primary_contract, sdc.primary_contract_address)] = sdc

        self.handle_links()
        self.handle_struct_links()

    def instrument_auto_finders(self, build_arg_contract_file: str, i: int, sdc_pre_finder: SDC) -> \
            Tuple[Dict[str, str], SDC]:
        debug_print(f"Instrumenting auto finders in {build_arg_contract_file}")
        added_finders_tuple = self.add_auto_finders(build_arg_contract_file, sdc_pre_finder)
        if added_finders_tuple is None:
            print_warning(f"Computing finder instrumentation failed for {build_arg_contract_file}")
            return {}, sdc_pre_finder
        (added_finders, instr) = added_finders_tuple
        remapping_dict: Dict[str, str] = dict()
        if abs_posix_path(build_arg_contract_file) not in instr:
            instr[abs_posix_path(build_arg_contract_file)] = dict()
        for contract_file, instr_loc in instr.items():
            new_name = replace_file_name(contract_file, f"autoFinder_{get_file_basename(contract_file)}")

            old_abs_path = abs_posix_path(contract_file)
            new_abs_path = abs_posix_path(new_name)

            if not self.input_config.debug:
                self.generated_files.append(new_abs_path)

            remapping_dict[old_abs_path] = new_abs_path
            instr_rewrites: List[Tuple[int, Instrumentation]] = list(instr_loc.items())
            ordered_rewrite = sorted(instr_rewrites, key=lambda it: it[0])
            with open(old_abs_path, 'rb') as in_file:
                with open(new_abs_path, "wb+") as output:
                    read_so_far = 0
                    for byte_offs, to_insert in ordered_rewrite:
                        debug_print(f"Next chunk: {byte_offs}, inserting {to_insert.to_ins}")
                        amt = byte_offs - read_so_far
                        next_chunk = in_file.read(amt)
                        old_pos = in_file.tell()
                        output.write(next_chunk)
                        next_byte = in_file.read(1)
                        if next_byte != to_insert.expected:
                            debug_print(f"Failed to find {repr(to_insert.expected)} at offset {byte_offs} "
                                        f"in {old_abs_path} (got {repr(next_byte)})")
                            debug_print(f"Underlying file reports {in_file.tell()} (before read: {old_pos})")
                            return {}, sdc_pre_finder
                        insertion_bytes = bytes(to_insert.to_ins, "utf-8")
                        if to_insert.before:
                            debug_print(f"Writing instrumentation in {new_abs_path} at {byte_offs}")
                            output.write(insertion_bytes)
                            output.write(next_byte)
                        else:
                            output.write(next_byte)
                            debug_print(f"Writing instrumentation in {new_abs_path} at {byte_offs + 1}")
                            output.write(insertion_bytes)
                        read_so_far += amt + 1
                    output.write(in_file.read(-1))

        new_name = f"autoFinder_{get_file_basename(build_arg_contract_file)}"
        new_file = replace_file_name(build_arg_contract_file, new_name)
        self.input_config.fileToContractName[new_file] = self.input_config.fileToContractName[
            build_arg_contract_file]
        for (_, node_dict) in self.asts[build_arg_contract_file].items():
            for (_, n) in node_dict.items():
                if n.get("nodeType", None) != "ImportDirective":
                    continue
                if n.get("absolutePath", "") in remapping_dict and type(n.get("file", None)) == str:
                    remapping_dict[n.get("file")] = remapping_dict[n.get("absolutePath")]
        remappings = [f"{old_abs_path}={new_abs_path}" for (old_abs_path, new_abs_path) in remapping_dict.items()]
        # TODO: I think this file name gets passed on to kotlin?? Not sure if it'll ever want to open the
        #       file, or if it'll only get the .certora_config one??
        try:
            sdc = self.collect_for_file(new_file, i, remappings, self.input_config.debug,
                                        fail_on_compilation_error=False)
        except SolcCompilationException as e:
            print(f"Encountered an exception generating autofinder {new_file} ({e}), falling back to original "
                  f"file {get_file_basename(build_arg_contract_file)}")
            return {}, sdc_pre_finder
        return added_finders, sdc

    def handle_links(self) -> None:
        # Link processing
        if self.input_config.link is not None:
            links = self.input_config.link
            for link in links:
                src, dst = link.split("=", 2)
                src_contract, reference_to_replace_with_link = src.split(":", 2)
                sources_to_update = self.get_matching_sdc_names_from_SDCs(src_contract)
                if len(sources_to_update) > 1:
                    fatal_error(
                        f"Not expecting to find multiple SDC matches {sources_to_update} for {src_contract}")
                if len(sources_to_update) == 0:
                    fatal_error(f"No contract to link to with the name {src_contract}")
                source_to_update = sources_to_update[0]
                # Primary contract name should match here
                if self.has_sdc_name_from_SDCs_starting_with(dst):
                    example_dst = self.get_one_sdc_name_from_SDCs(dst)  # Enough to pick one
                    dst_address = self.SDCs[example_dst].primary_contract_address
                else:
                    if is_hex(dst):
                        dst = hex_str_to_cvt_compatible(dst)
                        # The jar doesn't accept numbers with 0x prefix
                    dst_address = dst  # Actually, just a number

                # Decide how to link
                matching_immutable = list({(c, x.varname) for c in self.SDCs[source_to_update].contracts for x in
                                           c.immutables
                                           if
                                           x.varname == reference_to_replace_with_link and c.name == src_contract})
                if len(matching_immutable) > 1:
                    fatal_error(
                        f"Not expecting to find multiple immutables with the name {reference_to_replace_with_link}, "
                        f"got matches {matching_immutable}")
                """
                Three kinds of links, resolved in the following order:
                1. Immutables. We expect at most one pair of (src_contract, immutableVarName) that matches
                2. Field names. Allocated in the storage - we fetch their slot number. (TODO: OFFSET)
                3. Slot numbers in EVM. Requires knowledge about the Solidity compilation. (TODO: OFFSET)
                """
                debug_print(f"Reference to replace with link: {reference_to_replace_with_link}")
                if len(matching_immutable) == 1 and reference_to_replace_with_link == matching_immutable[0][1]:
                    contract_match = matching_immutable[0][0]

                    def map_immut(immutable_reference: ImmutableReference) -> ImmutableReference:
                        if immutable_reference.varname == reference_to_replace_with_link:
                            return PresetImmutableReference(immutable_reference.offset, immutable_reference.length,
                                                            immutable_reference.varname, dst_address)
                        else:
                            return immutable_reference

                    contract_match.immutables = [map_immut(immutable_reference) for immutable_reference in
                                                 contract_match.immutables]

                    continue
                elif not reference_to_replace_with_link.isnumeric() and not is_hex(reference_to_replace_with_link):
                    # We need to convert the string to a slot number
                    resolved_src_slot = self.resolve_slot(src_contract, reference_to_replace_with_link)
                else:
                    # numeric case
                    if is_hex(reference_to_replace_with_link):
                        # if hex, need to remove the 0x
                        reference_to_replace_with_link = hex_str_to_cvt_compatible(reference_to_replace_with_link)
                    else:
                        # need to convert the dec to hex
                        reference_to_replace_with_link = decimal_str_to_cvt_compatible(reference_to_replace_with_link)
                    resolved_src_slot = reference_to_replace_with_link
                debug_print(f"Linking slot {resolved_src_slot} of {src_contract} to {dst}")
                debug_print(' '.join(k for k in self.SDCs.keys()))

                debug_print(f"Linking {src_contract} ({source_to_update}) to {dst_address} in slot {resolved_src_slot}")
                self.SDCs[source_to_update].state[resolved_src_slot] = dst_address

    def handle_struct_links(self) -> None:
        # struct link processing
        if self.input_config.struct_link is not None:
            debug_print('handling struct linking')
            links = self.input_config.struct_link
            for link in links:
                src, dst = link.split("=", 2)
                src_contract, reference_to_replace_with_link = src.split(":", 2)
                sources_to_update = self.get_matching_sdc_names_from_SDCs(src_contract)
                if len(sources_to_update) > 1:
                    fatal_error(f"Not expecting to find multiple SDC matches {sources_to_update} for {src_contract}")
                source_to_update = sources_to_update[0]
                # Primary contract name should match here
                if self.has_sdc_name_from_SDCs_starting_with(dst):
                    example_dst = self.get_one_sdc_name_from_SDCs(dst)  # Enough to pick one
                    dst_address = self.SDCs[example_dst].primary_contract_address
                else:
                    dst_address = dst  # Actually, just a number

                debug_print(f"STRUCT Reference to replace with link: {reference_to_replace_with_link}")

                if not reference_to_replace_with_link.isnumeric() and not is_hex(reference_to_replace_with_link):
                    # We need to convert the string to a slot number
                    fatal_error_if_not_library(f"error: struct link slot '{reference_to_replace_with_link}' not a "
                                               f"hexadecimal number")
                else:
                    if is_hex(reference_to_replace_with_link):
                        resolved_src_slot = hex_str_to_cvt_compatible(reference_to_replace_with_link)
                        # The jar doesn't accept numbers with 0x or 0X as prefix
                    else:
                        resolved_src_slot = decimal_str_to_cvt_compatible(reference_to_replace_with_link)
                debug_print(f"STRUCT Linking slot {resolved_src_slot} of {src_contract} to {dst}")
                debug_print(' '.join(k for k in self.SDCs.keys()))

                debug_print(f"STRUCT Linking {src_contract} ({source_to_update}) to {dst_address} in slot "
                            f"{resolved_src_slot}")
                self.SDCs[source_to_update].structLinkingInfo[resolved_src_slot] = dst_address

    def has_sdc_name_from_SDCs_starting_with(self, potential_contract_name: str) -> bool:
        candidates = self.get_matching_sdc_names_from_SDCs(potential_contract_name)
        return len(candidates) > 0

    def get_one_sdc_name_from_SDCs(self, contract: str) -> str:
        return [k for k, v in self.SDCs.items() if k.startswith(f"{contract}_")][0]

    def get_matching_sdc_names_from_SDCs(self, contract: str) -> List[str]:
        return [k for k, v in self.SDCs.items() if k.startswith(f"{contract}_")]

    @staticmethod
    def resolve_slot_from_storage_layout(primary_contract: str, slot_name: str, sdc: SDC) -> Optional[str]:
        """
        @param primary_contract: Name of the contract
        @param slot_name: Name of the field we wish to associate with a slot number
        @param sdc: The object representing an invocation of solc where we hope to find storageLayout
        @return: If there is a valid storage layout, returns the slot number associated with slot_name as hex without
        preceding 0x (or 0X)
        """
        storage_layouts = [c.storageLayout for c in sdc.contracts if
                           c.name == primary_contract and c.storageLayout is not None]
        if len(storage_layouts) != 1:
            debug_print(f"Expected exactly one storage layout matching {primary_contract}, got {len(storage_layouts)}")
            return None

        storage_layout = storage_layouts[0]
        if storage_layout is None or "storage" not in storage_layout:
            debug_print(f"Storage layout should be an object containing a 'storage' field, but got {storage_layout}")
            return None

        relevant_slots = [slot for slot in storage_layout["storage"] if
                          "label" in slot and slot["label"] == slot_name]
        debug_print(f"Found relevant slots in storage layout of {primary_contract}: {relevant_slots}")
        if len(relevant_slots) == 1:
            slot_number = relevant_slots[0]["slot"]
            # slot_number from storage layout is already in decimal.
            return decimal_str_to_cvt_compatible(slot_number)
        else:
            debug_print(
                f"Found multiple matches of {slot_name} "
                f"in storage layout of contract {primary_contract}: {relevant_slots}")
            return None

    def resolve_slot(self, primary_contract: str, slot_name: str) -> str:
        """
        @param primary_contract: Name of the contract
        @param slot_name: Name of the field we wish to associate with a slot number
        @return: The resolved slot number as hex without preceding 0x (or 0X)
        """
        debug_print(f"Resolving slots for {primary_contract} out of {self.SDCs.keys()}")
        sdc = self.SDCs[self.get_one_sdc_name_from_SDCs(primary_contract)]  # Enough to pick one

        slot_number_from_storage_layout = self.resolve_slot_from_storage_layout(primary_contract, slot_name, sdc)
        if slot_number_from_storage_layout is not None:
            return slot_number_from_storage_layout

        debug_print(f"Storage layout not available for contract {primary_contract}. "
                    f"Matching slots from ASM output instead")

        file = sdc.sdc_origin_file
        solc_ver_to_run = self.get_relevant_solc(primary_contract)
        solc_add_extra_args = self.get_extra_solc_args()

        asm_collect_cmd = f"{solc_ver_to_run} {solc_add_extra_args} -o {self.config_path}/ --overwrite --asm " \
                          f"--allow-paths {self.input_config.path} {file}"
        if self.input_config.packages is not None:
            asm_collect_cmd = f"{asm_collect_cmd} {' '.join(self.input_config.packages)}"

        run_cmd(asm_collect_cmd, f"{primary_contract}.asm", self.config_path, shell=False, debug=DEBUG)

        with open(f"{self.config_path}/{primary_contract}.evm", "r") as asm_file:
            debug_print(f"Got asm {asm_file}")
            saw_match = False
            candidate_slots = []
            for line in asm_file:
                if saw_match:
                    candidate_slots.append(line)
                    saw_match = False
                else:
                    regex = r'/\* "[a-zA-Z0-9./_\-:]+":[0-9]+:[0-9]+\s* %s \*/' % (slot_name,)
                    saw_match = re.search(regex, line) is not None
                    if saw_match:
                        debug_print(f"Saw match for {regex} on line {line}")
            debug_print(f"Candidate slots: {candidate_slots}")
            normalized_candidate_slots = [x.strip() for x in candidate_slots]
            debug_print(f"Candidate slots: {normalized_candidate_slots}")
            filtered_candidate_slots = [x for x in normalized_candidate_slots if re.search('^0[xX]', x)]
            set_candidate_slots = set(filtered_candidate_slots)
            debug_print(f"Set of candidate slots: {set_candidate_slots}")
            if len(set_candidate_slots) == 1:
                # Auto detect base (should be 16 though thanks to 0x)
                slot_number = hex(int(list(set_candidate_slots)[0], 0))[2:]
                debug_print(f"Got slot number {slot_number}")
            else:
                raise Exception(f"Failed to resolve slot for {slot_name} in {primary_contract}, "
                                f"valid candidates: {set_candidate_slots}")

        return slot_number


class SpecImportLexer(Lexer):
    """
        A lexer that creates designated tokens for 'import' keywords and strings literals in the given spec file.
    """

    def __init__(self, spec_file: str, spec_content: str):
        self.spec_file = spec_file
        self.spec_content = spec_content

    tokens = {ANY, IMPORT, STRING}  # type: ignore # noqa: F821

    ignore = ' \t'  # Ignore whitespace and tab characters

    # Ignore comments; in particular, ignore commented out imports;
    ignore_comments_a = r'[/][/][^\n\r]*'

    @_(r'[/][*][\s\S]*?[*][/]')  # type: ignore # noqa: F821
    def ignore_comments_b(self, t: Token) -> None:
        self.lineno += t.value.count("\n")

    IMPORT = 'import'  # First, match against 'import' keywords and string literals

    @_(r'\"[^"]*\"')  # type: ignore # noqa: F821
    def STRING(self, t: Token) -> Token:  # Extract the characters of the string literal, e.g., '"abc"' --> 'abc'
        result = re.search(r'[^"]+', t.value)
        if result:
            t.value = result.group(0)
        else:  # An empty string literal (i.e., '""')
            t.value = ''
        return t

    ANY = r'.'  # Default: Characters that have nothing to do with import declarations

    @_(r'\n+')  # type: ignore # noqa: F821
    def ignore_newline(self, t: Token) -> None:  # Ignore new line characters; use those to compute the line number
        self.lineno += len(t.value)

    # Error handling
    def error(self, t: Token) -> None:
        raise Exception(fr'{self.spec_file}:{self.lineno}:{self.find_column(t.index)}: '
                        fr'Encountered the illegal symbol {repr(t.value[0])}')

    # Computes the column number from the given token's index
    def find_column(self, token_index: int) -> int:
        last_cr = self.spec_content.rfind('\n', 0, token_index)
        if last_cr < 0:
            last_cr = 0
        column = (token_index - last_cr) + 1
        return column


class SpecImportParser(Parser):
    """
           A parser for import declarations of specification files, namely strings that have the form
           'IMPORT STRING'.
           NOTE: The parser should guarantee that if the spec file has a valid syntax, then all of its imports
           are parsed. In particular, no actual imports are omitted, and no
           non-existing or commented out imports are erroneously added.
           If the spec has an invalid syntax, we may over-approximate the actual set of imports,
           but we expect that the CVL parser would fail later.

    """

    def __init__(self, _lexer: SpecImportLexer):
        self.lexer = _lexer
        self.parse_error_msgs = []  # type: List[str]

    # Get the token list from the lexer (required)
    tokens = SpecImportLexer.tokens

    # Grammar rules and actions
    @_('imports maybe_import_decl')  # type: ignore # noqa: F821,F811
    def imports(self, p: YaccProduction) -> List[Tuple[str, str]]:
        return p.imports if not p.maybe_import_decl else p.imports + p.maybe_import_decl

    @_('')  # type: ignore # noqa: F821,F811
    def imports(self, p: YaccProduction) -> List[Tuple[str, str]]:  # noqa: F821,F811
        return []

    @_('ANY', 'STRING')  # type: ignore # noqa: F821,F811
    def maybe_import_decl(self, p: YaccProduction) -> None:  # Surely NOT an import declaration
        return None

    @_('IMPORT STRING')  # type: ignore # noqa: F821,F811
    def maybe_import_decl(self, p: YaccProduction) -> List[Tuple[str, str]]:  # noqa: F821,F811
        # Surely an import declaration
        # Also log the location of the import declaration
        return [(p.STRING, f'{p.lineno}:{self.lexer.find_column(p.index)}')]

    def error(self, p: Token) -> Token:
        self.parse_error_msgs.append(fr'{self.lexer.spec_file}:{p.lineno}:{self.lexer.find_column(p.index)}: '
                                     fr'Did not expect the symbol {repr(p.value)}')  # log the error
        # Read ahead looking for an 'import' keyword.
        # If such a keyword is found, restart the parser in its initial state
        while True:
            p = next(self.tokens.__iter__(), None)
            if not p or p.type == 'IMPORT':
                break
            self.restart()
        return p  # Return IMPORT as the next lookahead token


class SpecWithImports:
    """
        .spec file together with the import declarations of .spec files that were collected transitively from it.
    """

    def __init__(self, _spec_file: str, _spec_idx: int, _abspath_imports_to_locs: Dict[str, Set[str]],
                 _spec_files_to_orig_imports: Dict[str, Set[str]]):

        self.spec_file = _spec_file  # The path of the main .spec file

        self.spec_idx = _spec_idx  # The index that will be prepended to the names of the main and imported .spec files

        #  The path where the main .spec file will eventually be copied to
        self.eventual_path_to_spec = self.__get_eventual_path_to_spec(self.spec_file)

        # Maps absolute .spec import paths to locations of corresponding import declarations in the .spec files
        self.abspath_imports_to_locs = _abspath_imports_to_locs

        # Maps each .spec file to the import paths that appear in the import declarations that this file contains.
        # Each key is the absolute path of the .spec file
        self.spec_files_to_orig_imports = _spec_files_to_orig_imports

        # Maps each "eventual" path of a .spec file to the import paths that appear in this file.
        # The "eventual" path is where the .spec file will eventually be copied to;
        # e.g., "./someFolder/s.spec" -> .certora_config/{self.spec_idx}_s.spec
        self.eventual_path_to_orig_imports = {self.__get_eventual_path_to_spec(abspath): list(orig_imports) for
                                              abspath, orig_imports in self.spec_files_to_orig_imports.items()}

        #  Maps each absolute .spec import path to the one where the imported .spec file will eventually be copied to
        self.abspath_to_eventual_import_paths = {abspath: self.__get_eventual_path_to_spec(abspath) for abspath in
                                                 self.abspath_imports_to_locs.keys()}

        # Maps each "eventual" .spec import path to a (canonicalized) relative form of the original import declaration
        self.eventual_import_paths_to_relpaths = {
            self.__get_eventual_path_to_spec(abspath): as_posix(os.path.relpath(abspath)) for abspath in
            self.abspath_imports_to_locs.keys()
        }

        self.__assert_distinct_filenames()

    def __get_eventual_path_to_spec(self, path: str) -> str:
        return f".certora_config/{self.spec_idx}_{get_file_basename(as_posix(path))}.spec"

    #  Checks that we don't have distinct import paths that share the same file names, e.g.,
    #  './folder/a.spec' and './otherFolder/a.spec'
    #  Also checks that there is no import path whose file name is the same as that of the main .spec file.
    #  Note: This is required because we copy all of the imported .spec files, together with the main .spec file,
    #  into the same directory.
    def __assert_distinct_filenames(self) -> None:

        def invalid_imports_str(invalid_imports: List[str]) -> str:
            return '\n'.join(
                [f'\"{abspath}\" @ {"; ".join(self.abspath_imports_to_locs[abspath])}' for abspath in
                 invalid_imports])

        distinct_imports_filenames = list(
            map((lambda path: os.path.basename(path)), self.abspath_imports_to_locs.keys()))

        distinct_imports_with_shared_filenames = \
            [path for path in self.abspath_imports_to_locs.keys() if
             distinct_imports_filenames.count(os.path.basename(path)) > 1]

        if distinct_imports_with_shared_filenames:
            raise Exception(
                f'Expected all distinct .spec file imports to also have distinct file names, but got:\n'
                f'{invalid_imports_str(distinct_imports_with_shared_filenames)}')

        spec_file_basename = os.path.basename(self.spec_file)
        imports_with_spec_file_basename = [path for path in self.abspath_imports_to_locs.keys() if
                                           os.path.basename(path) == spec_file_basename]
        if imports_with_spec_file_basename:
            raise Exception(
                f'Expected all .spec file imports to have file names different from \'{spec_file_basename}\', but got:'
                f'\n{invalid_imports_str(imports_with_spec_file_basename)}')


class CertoraVerifyGenerator:
    def __init__(self, build_generator: CertoraBuildGenerator):
        self.build_generator = build_generator
        self.input_config = build_generator.input_config
        self.certora_verify_struct = []
        self.verify = {}  # type: Dict[str, List[SpecWithImports]]
        if self.input_config.verify is not None \
                or self.input_config.assert_contracts is not None:
            if self.input_config.verify is not None:
                verification_queries = self.input_config.verify
                vq_spec_idx = 0
                for verification_query in verification_queries:
                    vq_contract, vq_spec = verification_query.split(":", 2)
                    vq_spec = abs_posix_path(vq_spec)  # get full abs path
                    if self.verify.get(vq_contract, None) is None:
                        self.verify[vq_contract] = []
                    vq_spec_with_imports = self.get_spec_with_imports(vq_spec, vq_spec_idx)  # type: SpecWithImports
                    self.verify[vq_contract].append(vq_spec_with_imports)
                    self.certora_verify_struct.append(
                        {"type": "spec",
                         "primary_contract": vq_contract,
                         "specfile": vq_spec_with_imports.eventual_path_to_spec,
                         "specfileOrigRelpath": as_posix(os.path.relpath(vq_spec)),
                         "specfilesToImportDecls": vq_spec_with_imports.eventual_path_to_orig_imports,
                         "importFilesToOrigRelpaths": vq_spec_with_imports.eventual_import_paths_to_relpaths
                         }
                    )
                    vq_spec_idx += 1
            if self.input_config.assert_contracts is not None:
                for contractToCheckAssertsFor in self.input_config.assert_contracts:
                    self.certora_verify_struct.append(
                        {"type": "assertion",
                         "primary_contract": contractToCheckAssertsFor}
                    )

        else:
            # if no --verify or --assert, remove verify json file
            remove_file(f'{OPTION_OUTPUT_VERIFY}.json')

    def get_spec_with_imports(self, spec_file: str, spec_idx: int) -> SpecWithImports:
        seen_abspath_imports_to_locs = dict()  # type: Dict[str, Set[str]]
        spec_file_to_orig_imports = dict()  # type: Dict[str, Set[str]]
        self.check_and_collect_imported_spec_files(spec_file, seen_abspath_imports_to_locs, [spec_file],
                                                   spec_file_to_orig_imports)
        return SpecWithImports(spec_file, spec_idx, seen_abspath_imports_to_locs, spec_file_to_orig_imports)

    def check_and_collect_imported_spec_files(self, spec_file: str, seen_abspath_imports_to_locs: Dict[str, Set[str]],
                                              dfs_stack: List[str], spec_file_to_orig_imports: Dict[str, Set[str]]) -> \
            None:
        with open(spec_file, 'r') as f:
            spec_content = f.read()
            spec_import_lexer = SpecImportLexer(spec_file, spec_content)
            spec_import_parser = SpecImportParser(spec_import_lexer)
            imports_with_locs = spec_import_parser.parse(spec_import_lexer.tokenize(spec_content))

            if imports_with_locs:
                spec_file_to_orig_imports[spec_file] = set()
                for orig_import_to_loc in imports_with_locs:
                    spec_file_to_orig_imports[spec_file].add(orig_import_to_loc[0])

            debug_print(fr'In {spec_file}, found the imports: {imports_with_locs}')
            if spec_import_parser.parse_error_msgs:  # We have parsing errors
                errors_str = '\n'.join(spec_import_parser.parse_error_msgs)
                raise Exception(f'Could not parse {spec_file} due to the following errors:\n{errors_str}')

            abspath_imports_with_locs = list(map(
                lambda path_to_loc: (abs_posix_path_relative_to_root_file(path_to_loc[0], spec_file), path_to_loc[1]),
                imports_with_locs))

            invalid_imports_with_locs = [p for p in abspath_imports_with_locs if not os.path.isfile(p[0]) or
                                         os.path.splitext(p[0])[1] != '.spec']

            def path_to_loc_str(path_to_loc: Tuple[str, str]) -> str:
                return f'{path_to_loc[1]}:\"{path_to_loc[0]}\"'

            if invalid_imports_with_locs:
                invalid_paths_str = '\n'.join(map(path_to_loc_str, invalid_imports_with_locs))
                raise Exception(
                    f'In {spec_file}, the following import declarations do not import existing .spec files:'
                    f'\n{invalid_paths_str}\n'
                )

            for import_path_to_loc in abspath_imports_with_locs:  # Visit each import declaration in a DFS fashion
                if import_path_to_loc[0] in dfs_stack:  # We have cyclic imports :(((
                    imports_cycle = ' -->\n'.join(
                        dfs_stack[dfs_stack.index(import_path_to_loc[0]):] + [import_path_to_loc[0]])
                    raise Exception(f'In {spec_file}, the import declaration {path_to_loc_str(import_path_to_loc)} '
                                    f'leads to an imports\' cycle:\n{imports_cycle}')

                import_loc_with_spec_file = f'{spec_file}:{import_path_to_loc[1]}'

                if import_path_to_loc[0] in seen_abspath_imports_to_locs:  # Visit each import declaration only once
                    seen_abspath_imports_to_locs[import_path_to_loc[0]].add(import_loc_with_spec_file)
                    continue

                seen_abspath_imports_to_locs[import_path_to_loc[0]] = {import_loc_with_spec_file}
                dfs_stack.append(import_path_to_loc[0])
                self.check_and_collect_imported_spec_files(import_path_to_loc[0], seen_abspath_imports_to_locs,
                                                           dfs_stack, spec_file_to_orig_imports)
                dfs_stack.pop()

    def copy_specs(self) -> None:
        for contract, specs_with_imports in self.verify.items():
            for spec_w_i in specs_with_imports:
                shutil.copy2(spec_w_i.spec_file, spec_w_i.eventual_path_to_spec)
                #  copy .spec imports
                for import_srcpath, import_dstpath in spec_w_i.abspath_to_eventual_import_paths.items():
                    shutil.copy2(import_srcpath, import_dstpath)

    def check(self) -> None:
        for contract in self.verify:
            if len(self.build_generator.get_matching_sdc_names_from_SDCs(contract)) == 0:
                fatal_error_if_not_library(
                    f"Error: Could not find contract {contract} in contracts "
                    f"[{','.join(map(lambda x: x[1].primary_contract, self.build_generator.SDCs.items()))}]")

    def dump(self) -> None:
        debug_print(f"writing {CERTORA_VERIFY_FILE}")
        with open(CERTORA_VERIFY_FILE, 'w+') as output_file:
            json.dump(self.certora_verify_struct, output_file, indent=4, sort_keys=True)


def build(args: argparse.Namespace, is_library: bool = False) -> None:
    """
    This is the main function of certoraBuild
    @param args: A namespace including command line arguments. We expect the namespace to include validated arguments
    @param is_library: True if we run this function from a library, like in regTest.py
    """
    global BUILD_IS_LIBRARY
    BUILD_IS_LIBRARY = is_library
    global DEBUG

    try:
        if args.debug:
            DEBUG = True

        input_config = InputConfig(args)

        # Create generators
        certora_build_generator = CertoraBuildGenerator(input_config)

        # Build .certora_verify.json
        certora_verify_generator = CertoraVerifyGenerator(certora_build_generator)
        certora_verify_generator.copy_specs()
        certora_verify_generator.dump()

        # Start by syntax checking, if we're in the right mode
        if mode_has_spec_file(args.mode) and not args.build_only:
            if args.disableLocalTypeChecking:
                print_warning(
                    "Local checks of CVL specification files disabled. It is recommended to enable the checks.")
            else:
                run_local_spec_check(with_typechecking=False, is_library=BUILD_IS_LIBRARY)
                print_completion_message("Local CVL specification syntax checking finished successfully", True)

        # Start to collect information from solc
        try:
            certora_build_generator.build(args)
        except Exception:
            raise
        finally:
            certora_build_generator.cleanup()

        certora_verify_generator.check()

        # Output
        debug_print(f"writing file {CERTORA_BUILD_FILE}")
        with open(CERTORA_BUILD_FILE, 'w+') as output_file:
            json.dump({k: v.as_dict() for k, v in certora_build_generator.SDCs.items()},
                      output_file,
                      indent=4,
                      sort_keys=True)

    except Exception as e:
        print("Encountered an error configuring the verification environment:", e)
        debug_print(traceback.format_exc())
        exit_if_not_library(1)

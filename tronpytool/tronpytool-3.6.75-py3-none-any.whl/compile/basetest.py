# !/usr/bin/env python
# coding: utf-8
import codecs
import json
import os
import subprocess
import time

from .compile import BuildRemoteLinuxCommand, BuildLang
from .. import Tron, Evm
from ..compile.paths import Paths
from ..exceptions import ValidationError
from ..trx import Trx

ROOT = os.path.join(os.path.dirname(__file__))


class SolcWrap(object):
    """docstring for SolcWrap"""
    OUTPUT_BUILD = "build"
    WORKSPACE_PATH = ""
    solfolder = ""
    file_name = "xxx.sol"
    prefixname = ""
    statement = 'End : {}, IO File {}'

    def __init__(self, workspace):
        """param workspace: this is the local path for the file set"""
        self.WORKSPACE_PATH = workspace
        super(SolcWrap, self).__init__()

    def SetOutput(self, path):
        self.OUTPUTBUILD = path
        return self

    def SetSolPath(self, path):
        self.solfolder = path
        return self

    def BuildRemote(self):
        """This is the remote command to execute the solc_remote bash file
        using remote compile method to compile the sol files
        all works will be done with the remote server or using the docker"""
        list_files = subprocess.run(["{}/solc_remote".format(self.WORKSPACE_PATH)])
        print("The exit code was: %d" % list_files.returncode)
        return self

    def WrapModel(self):
        """setup initialize the file for combined.json"""
        pathc = os.path.join(self.WORKSPACE_PATH, self.OUTPUT_BUILD, "combined.json")
        try:
            pathcli = codecs.open(pathc, 'r', 'utf-8-sig')
            self.combined_data = json.load(pathcli)
        except Exception as e:
            print("Problems from loading items from the file: ", e)
        return self

    def GetCodeClass(self, classname) -> [any, any]:
        p1bin = os.path.join(self.WORKSPACE_PATH, self.OUTPUT_BUILD, "{}.bin".format(classname))
        p2abi = os.path.join(self.WORKSPACE_PATH, self.OUTPUT_BUILD, "{}.abi".format(classname))
        bin = codecs.open(p1bin, 'r', 'utf-8-sig').read()
        abi = json.load(codecs.open(p2abi, 'r', 'utf-8-sig'))
        return abi, bin

    def byClassName(self, path, classname):
        return "{prefix}:{name}".format(prefix=path, name=classname)

    def GetCodeTag(self, fullname):
        return self.combined_data["contracts"][fullname]["abi"], self.combined_data["contracts"][fullname]["bin"]

    def GetCode(self, path, classname) -> [str, str]:
        abi = self.combined_data["contracts"][self.byClassName(path, classname)]["abi"]
        bin = self.combined_data["contracts"][self.byClassName(path, classname)]["bin"]
        return abi, bin

    def writeFile(self, content, filename):
        fo = open(filename, "w")
        fo.write(content)
        fo.close()
        print(self.statement.format(time.ctime(), filename))

    @property
    def workspace(self):
        return self.WORKSPACE_PATH

    def StoreTxResult(self, tx_result_data: any, filepath: str):
        self.writeFile(json.dumps(tx_result_data, ensure_ascii=False), filepath)


class CoreBase:
    gas: int = 10 ** 9
    userSrcPercent: int = 1
    one: int = 0
    wait_time: int = 0
    list_type: str = "list_address"
    _contract_dict: dict = dict()
    _sol_list: list = []
    _sol_link: list = None
    sol_wrap: SolcWrap = None
    pathfinder: Paths = None
    is_debug: bool = False
    EVM_VERSION = Evm.BERLIN


class CoreDeploy(CoreBase):
    """DEFI Contract deployment
    with the right strategies
    """

    def __init__(self, tron: Tron):
        self.tron = tron
        self.last_class = ""
        self.is_deploy = False

    def debug(self):
        self.is_debug = True

    def OverrideGasConfig(self, _gas: int, _percent: int) -> None:
        """
        the override the configuration for the gas amount and the gas price
        :param _gas: int
        :param _gas_price: int
        :return: NONE
        """
        self.gas = _gas
        self.userSrcPercent = _percent

    def OverrideChainConfig(self, one: int, wait: int) -> None:
        """
        Lets have the configuration done now.
        :param one: ONE coin to measure
        :param wait: the waiting time from each block confirmation
        :return:
        """
        self.wait_time = wait
        self.one = one

    @property
    def one(self) -> int:
        """
        ONE platform coin will be decoded to be...
        :return: int
        """
        return self.one

    @property
    def waitSec(self) -> int:
        return self.wait_time

    @property
    def __list_key_label(self) -> str:
        return "{}_{}".format(self.list_type, self.last_class)

    @property
    def __kv_label(self) -> str:
        return "kv_{}".format(self.last_class)

    def getAddr(self, keyname: str) -> str:
        """example: TT67rPNwgmpeimvHUMVzFfKsjL9GZ1wGw8"""
        return self._contract_dict.get(keyname)

    def getAddr0x(self, keyname: str) -> str:
        """example: 0xBBC8C05F1B09839E72DB044A6AA57E2A5D414A10"""
        return self.tron.address.to_hex_0x(self._contract_dict.get(keyname))

    def getAddr0x41(self, keyname: str) -> str:
        """example: 0x41BBC8C05F1B09839E72DB044A6AA57E2A5D414A10"""
        return self.tron.address.to_hex_0x_41(self._contract_dict.get(keyname))

    def getAddrHex(self, keyname: str) -> str:
        """example: 41BBC8C05F1B09839E72DB044A6AA57E2A5D414A10"""
        return self.tron.address.to_hex(self._contract_dict.get(keyname))

    def getAllAddress(self) -> dict:
        return self._contract_dict

    def preview_all_addresses(self) -> None:
        print(self._contract_dict)

    def is_deployment(self) -> bool:
        return self.is_deploy

    def ready_io(self, show_address: bool = False):
        """try to load up the file from the existing path"""
        try:
            self._contract_dict = self.pathfinder.LoadDeploymentFile()
            print("==== 🛄 data is prepared and it is ready now.. ")
            if show_address:
                self.preview_all_addresses()
        except ValueError:
            pass
        except TypeError as e:
            print(e)

    def connect_deploy_core(self, workspace: str, rebuild=False, deploy=False) -> None:
        if rebuild:
            self.sol_wrap = SolcWrap(workspace).BuildRemote()
        else:
            self.sol_wrap = SolcWrap(workspace)
        self.pathfinder = Paths(workspace).setDefaultPath().Network(self.tron.network_name)
        self.is_deploy = deploy

        if not deploy:
            self.ready_io(True)

    def connect(self, workspace: str, history: any) -> None:
        self.is_deploy = False
        self.sol_wrap = SolcWrap(workspace)
        if history is False:
            self.pathfinder = Paths(workspace).setDefaultPath().Network(self.tron.network_name)
        else:
            self.pathfinder = Paths(workspace).SetUseVersion(history).Network(self.tron.network_name)

        self.ready_io(True)

    def SetupContract(self):
        pass

    def after_deployment_initialize_settings(self):
        """
        setup contract starting params
        setup the starting time using bang
        setup the first member
        :return:
        """
        pass

    def complete_deployment(self) -> None:
        """store up the deployed contrcat addresses to the local file storage"""
        self.sol_wrap.StoreTxResult(self._contract_dict, self.pathfinder.SaveDeployConfig)

    def _checkErrorForTxReceipt(self, receipt: any, class_name: str) -> str:
        if "transaction" not in receipt:
            print("⚠️ Failed to deploy contract with this error result from this.", receipt)
            raise ValidationError

        tx = receipt["transaction"]

        if "contract_address" not in tx:
            print(f"⚠️ Contract address is not found for deployment - {class_name}.")
            raise ValidationError

        contract_address_hex = tx["contract_address"]
        txID = tx["txID"]
        contract_address = self.tron.address.from_hex(contract_address_hex)
        self._contract_dict[class_name] = contract_address
        self._contract_dict["kv_{}".format(class_name)] = dict(
            owner=self.tron.default_address.base58,
        )
        print(txID)
        self.hashLink(txID)
        print("📦 Address saved to ✅ {} -> {}".format(contract_address, class_name))
        return contract_address

    def hashLink(self, hash: str):
        if self.tron.network_name == "nile":
            print(f"https://nile.tronscan.org/#/transaction/{hash}")
        if self.tron.network_name == "default":
            print(f"https://tronscan.org/#/transaction/{hash}")

    def deploy(self,
               classname: str,
               params: list = [],
               fee: int = 0,
               percent: int = 0) -> str:

        if self.sol_wrap is None:
            print("⚠️ The wrapper solc is not init.")

        """This is using the faster way to deploy files by using the specific abi and bin files"""
        _abi, _bytecode = self.sol_wrap.GetCodeClass(classname)
        contractwork = self.tron.Chain.contract(abi=_abi, bytecode=_bytecode)
        contract = contractwork.constructor()

        # contract = contractwork.constructor()
        default_gas = self.gas
        userSrcPercent = self.userSrcPercent
        h1 = default_gas if fee == 0 else fee
        h2 = userSrcPercent if percent == 0 else percent

        # user source percentage
        tx_data = contract.transact(
            fee_limit=h1,
            call_value=0,
            parameters=params,
            consume_user_resource_percent=h2)

        print("========TX Pre-Result ✅")
        if self.is_debug is True:
            print(tx_data)

        sign = self.tron.Chain.sign(tx_data)
        print("======== Signing {} ✅".format(classname))
        print(f"========🖍 Signing {classname}, ...")
        result = self.tron.Chain.broadcast(sign)
        print("======== Broadcast Result ✅ -> {}".format(Paths.showCurrentDeployedClass(classname)))
        self.sol_wrap.StoreTxResult(result, self.pathfinder.classObject(classname))
        address = self._checkErrorForTxReceipt(result, classname)
        self.complete_deployment()
        return address

    def setTargetClass(self, classname: str) -> "CoreDeploy":
        self.last_class = classname
        return self

    def setTargetListName(self, listname: str) -> "CoreDeploy":
        self.list_type = listname
        return self

    def setClassSolNames(self, to_compile_contract_list: list) -> "CoreDeploy":
        self._sol_list = to_compile_contract_list
        return self

    def setClassSolLinks(self, compile_links: list) -> "CoreDeploy":
        self._sol_link = compile_links
        return self

    def setEvm(self, verc: str) -> "CoreDeploy":
        self.EVM_VERSION = verc
        return self

    def remoteCompile(self, ver: str) -> "CoreDeploy":
        if ver == "":
            print("there is no solidity version specified")
            exit(0)
        self.pathfinder.setSolVersion(ver)
        self.pathfinder.setEvm(self.EVM_VERSION)
        BuildRemoteLinuxCommand(self.pathfinder, self._sol_list, self._sol_link)
        return self

    def localTranspile(self, dapp_folder: str = "app") -> "CoreDeploy":
        self.pathfinder.updateTargetDappFolder(dapp_folder)
        BuildLang(self.pathfinder, self._sol_list)
        return self

    def setKV(self, key: str, value: any) -> "CoreDeploy":
        if self.__kv_label not in self._contract_dict:
            self._contract_dict[self.__kv_label] = dict()
        self._contract_dict[self.__kv_label][key] = value
        return self

    def hasAddressInList(self, address: str) -> bool:
        if self.__list_key_label not in self._contract_dict:
            return False
        try:
            v = self._contract_dict[self.__list_key_label].index(address)
            return True
        except ValueError:
            return False

    def pushAddress(self, address: str, unique: bool = True) -> bool:
        if self.__list_key_label not in self._contract_dict:
            self._contract_dict[self.__list_key_label] = list()

        if unique is True:
            try:
                found_index = self._contract_dict[self.__list_key_label].index(address)
                return False
            except ValueError:
                self._contract_dict[self.__list_key_label].append(address)
                return True
            except IndexError:
                self._contract_dict[self.__list_key_label].append(address)
                return True
        else:
            self._contract_dict[self.__list_key_label].append(address)
            return True

    def removeAddress(self, address: str) -> bool:
        if self.__list_key_label not in self._contract_dict:
            return False
        self._contract_dict[self.__list_key_label].remove(address)
        return True

    def iterList(self) -> iter:
        if self.__list_key_label not in self._contract_dict:
            raise Exception("there is no list in the map")
        return iter(self._contract_dict[self.__list_key_label])

    def hasList(self) -> bool:
        if self.__list_key_label not in self._contract_dict:
            return False
        return len(self._contract_dict[self.__list_key_label]) > 0

    def hasField(self, key: str) -> bool:
        if self.__kv_label not in self._contract_dict:
            self._contract_dict[self.__kv_label] = dict()

        if key not in self._contract_dict[self.__kv_label]:
            return False
        else:
            return True

    def getString(self, key: str) -> str:
        return str(self.getVal(key))

    def getInt(self, key: str) -> int:
        return int(self.getVal(key))

    def getBytesArray(self, key: str) -> bytearray:
        return bytearray(self.getVal(key))

    def getBytes(self, key: str) -> bytes:
        return bytes(self.getVal(key))

    def getFloat(self, key: str) -> float:
        return float(self.getVal(key))

    def getVal(self, key: str) -> any:
        if self.__kv_label not in self._contract_dict:
            self._contract_dict[self.__kv_label] = dict()

        if key in self._contract_dict[self.__kv_label]:
            return self._contract_dict[self.__kv_label][key]

        return ""

    def SaveConfig(self) -> None:
        self.complete_deployment()

    def classic_deploy(self, sol_wrap: SolcWrap, path: str, classname: str, params: list = []) -> str:
        """
        This is the depreciated class and please check the class from deploy
        """
        self.sol_wrap.WrapModel()
        _abi, _bytecode = sol_wrap.GetCode(path, classname)
        contractwork = self.tron.Chain.contract(abi=_abi, bytecode=_bytecode)
        contract = contractwork.constructor()
        tx_data = contract.transact(
            fee_limit=10 ** 9,
            call_value=0,
            parameters=params,
            consume_user_resource_percent=1)
        print("======== TX Result ✅")
        sign = self.tron.Chain.sign(tx_data)
        print("======== Signing {} ✅".format(classname))
        result = self.tron.Chain.broadcast(sign)
        print("======== Broadcast Result ✅ -> {}".format(Paths.showCurrentDeployedClass(classname)))
        sol_wrap.StoreTxResult(result, self.pathfinder.classObject(classname))
        contract_address = self.tron.address.from_hex(result["transaction"]["contract_address"])
        self._contract_dict[classname] = contract_address
        print("======== address saved to ✅ {} -> {}".format(contract_address, classname))
        return contract_address

    def _balanceOf(self, address: str) -> int:
        amount = self.tron.Chain.get_balance(address, False)
        return amount


class WrapContract(object):
    """docstring for WrapContract The contract for this BOBA TEA"""

    def __init__(self, _network):
        nn1 = Tron().setNetwork(_network)
        if nn1.is_connected():
            self.tron_client = nn1
        else:
            print("client v1 is not connected. please check the internet connection or the service is down! network: {}".format(
                _network))
        self._tron_module = nn1.Chain
        self._contract = None
        self._network = _network

    def getClientTron(self) -> "Tron":
        return self.tron_client

    def getTrxModule(self) -> "Trx":
        return self._tron_module

    def getNewTronClient(self, wallet_address: str, pri_key: str) -> "Tron":
        client = Tron().setNetwork(self._network)
        client.private_key = pri_key
        client.default_address = wallet_address
        return client

    def setMasterKey(self, pub: str, pri: str) -> "WrapContract":
        self.tron_client.private_key = pri
        self.tron_client.default_address = pub
        return self


class ContractTool(CoreDeploy):
    def __init__(self, root: str, network: str, pub: str, pri: str):
        _workSpace1 = WrapContract(network).setMasterKey(pub, pri)
        _tron = _workSpace1.getClientTron()
        super().__init__(_tron)
        self.connect(root, False)
        print("-----> root for contract base")
        print(root)




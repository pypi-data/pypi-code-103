import os
import re

from tronpytool import Paths
from . import REC, ITEM, ITEMLINK, ITEM_CP_LOCAL, TRANS_LOCAL, ITEM_TRANSPILE_PYTHON, ITEM_TRANSPILE_TS, PRE_HEAD


def compileItem1(tar: Paths, k0: str) -> str:
    """
    list the item content
    :param tar:
    :param k0:
    :return:
    """
    return ITEM.format(
        SOLCPATH=tar.SOLCPATH,
        COMPILE_COIN=k0,
        SOLVER=tar.SOLC_VER,
        EVMVERSION=tar.EVM_VERSION
    )


def compileItem2(tar: Paths, k0: str, link_lib_conf: str) -> str:
    """

    :param tar:
    :param k0:
    :param link:
    :return:
    """

    return ITEMLINK.format(
        SOLCPATH=tar.SOLCPATH,
        COMPILE_COIN=k0,
        FILES_CONFIG=link_lib_conf,
        SOLVER=tar.SOLC_VER,
    )


def BuildRemoteLinuxCommand(p: Paths, list_files: list = None, linked: dict = None) -> None:
    """
    building the remote linux command line
    :param p:
    :param list_files:
    :return:
    """
    k = list()
    # ==================================================
    if list_files is not None:
        for v in list_files:
            k.append(compileItem1(p, v))
    # ==================================================
    if linked is not None:
        for c in linked:
            if "compile" in c and "libraries" in c:
                compile_file = c["compile"]
                lib_cmds = list()
                """
                solc before v0.8.1

                example: link = {
                    "filepath.sol:CLASS:0x0930193019391093012930209099302129"
                }

                solc --optimize --bin MetaCoin.sol | solc --link --libraries TestLib:<address>

                """
                for b in c["libraries"]:
                    if "class" in b and "address" in b:
                        source_line = "{}:{}".format(b["class"], b["address"])
                        if "src" in b:
                            source_line = "{}:{}:{}".format(b["src"], b["class"], b["address"])
                        lib_cmds.append(source_line)
                library_link_cmd = " ".join(lib_cmds)
                k.append(compileItem2(p, compile_file, library_link_cmd))
    # ==================================================
    with open(p.workspaceFilename("remotesolc"), 'w') as f:
        f.write(wrapContentCompile(p, k))
        f.close()
    # ==================================================


REG = r"(.+?)([A-Z])"


def snake(match):
    return match.group(1).lower() + "_" + match.group(2).lower()


def filter_file_name(y: str) -> str:
    classNameNew = y
    if y.startswith("TRC"):
        classNameNew = y.lower()
    elif y.startswith("ERC20"):
        classNameNew = y.upper()
    else:
        classNameNew = re.sub(REG, snake, y, 0)
    print(classNameNew)
    return classNameNew


def buildCmdTsUpdate(p: Paths, pathName: str) -> str:
    nameClass = filter_file_name(os.path.basename(pathName)).replace('.sol', '')
    fromp = "{}/codec/gen_ts/{}.ts".format(p.BUILDPATH, nameClass)
    top = "{}/{}/src/api/abi/{}.ts".format(p.BUILDPATH, p.WEB_DAPP_SRC, nameClass)
    return ITEM_CP_LOCAL.format(
        fromlocation=fromp,
        tolocation=top
    )


def buildCmdPy(p: Paths, pathName: str) -> str:
    return ITEM_TRANSPILE_PYTHON.format(
        outputfolder=f"{p.BUILDPATH}/codec/gen_py",
        target_abi=f"{p.BUILDPATH}/build/{os.path.basename(pathName).replace('.sol', '')}.abi",
        BUILDPATH=p.BUILDPATH
    )


def buildCmdTs(p: Paths, pathName: str) -> str:
    return ITEM_TRANSPILE_TS.format(
        outputfolder=f"{p.BUILDPATH}/codec/gen_ts",
        target_abi=f"{p.BUILDPATH}/build/{os.path.basename(pathName).replace('.sol', '')}.abi",
        BUILDPATH=p.BUILDPATH
    )


def wrapContentTranspile(tar: Paths, compile_list: list) -> str:
    """
    wrap content
    :param tar:
    :param compile_list:
    :return:
    """
    return TRANS_LOCAL.format(
        LISTP="\n".join(compile_list),
        TARGET_LOC=tar.TARGET_LOC,
        COMPRESSED_NAME=tar.COMPRESSED_NAME,
        SOLVER=tar.SOLC_VER,
        PRE_HEAD=PRE_HEAD
    )


def wrapContentCompile(tar: Paths, compile_list: list) -> str:
    """
    wrap content
    :param tar:
    :param compile_list:
    :return:
    """
    return REC.format(
        LISTP="\n".join(compile_list),
        TARGET_LOC=tar.TARGET_LOC,
        COMPRESSED_NAME=tar.COMPRESSED_NAME,
        SOLVER=tar.SOLC_VER
    )


def BuildLang(p: Paths, list_class_names: list) -> None:
    """

    :param p:
    :param list_class_names:
    :return:
    """
    k = list()
    # ==================================================
    for v in list_class_names:
        k.append(buildCmdPy(p, v))
        k.append(buildCmdTs(p, v))
        k.append(buildCmdTsUpdate(p, v))
    # ==================================================
    with open(p.workspaceFilename("localpile"), 'w') as f:
        f.write(wrapContentTranspile(p, k))
        f.close()

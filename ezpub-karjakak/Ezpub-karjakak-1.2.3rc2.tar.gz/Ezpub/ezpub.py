# -*- coding: utf-8 -*-
# Copyright © karjakak (K A K)

from .AttSet import AttSet
import os
import shutil
from subprocess import Popen, PIPE
import argparse
from datetime import datetime as dt
from Clien import clien
import sys
from sys import platform
from pathlib import Path

# Reference:
# stackoverflow.com/.../constantly-print-subprocess-output-while-process-is-running


def tokfile(token: str = None):
    # Create token to .pyirc for publish to PyPI.

    pth = "USERPROFILE" if platform.startswith("win") else "HOME"
    pth = os.path.join(os.environ[pth], ".pypirc")
    ky = None
    vr = "TOKEN_PYPI"
    if token:
        if token == "d":
            if os.path.isfile(pth):
                if platform.startswith("win"):
                    a = AttSet(pth)
                    for i in [
                        a.FILE_ATTRIBUTE_HIDDEN,
                        a.FILE_ATTRIBUTE_SYSTEM,
                        a.FILE_ATTRIBUTE_READONLY,
                    ]:
                        a.set_file_attrib(i)
                os.remove(pth)
                print("Token Removed")
            else:
                print("Nothing to remove, token not created yet!")
        else:
            ky = token
    else:
        print(f"IMPORTANT!")
        print(f"Please fill var: {vr}")
        gtt = clien.insdat()
        if gtt and gtt[1] == vr:
            clien.cmsk(gtt[0], gtt[2], gtt[1])
        else:
            if gtt is None:
                print("All fields need to be filled!")
            else:
                print(f'Field "var:" must be "{vr}"!')
    if ky:
        if all([os.getenv(vr, False) == ky, pss := clien.pssd()]):
            if ky := clien.reading(ky, pss):
                if not os.path.isfile(pth):
                    with open(pth, "w") as tkn:
                        tkn.write(f"[pypi]\nusername = __token__\npassword = {ky}")
                    del ky
                    if platform.startswith("win"):
                        a = AttSet(pth, True)
                        for i in [
                            a.FILE_ATTRIBUTE_HIDDEN,
                            a.FILE_ATTRIBUTE_SYSTEM,
                            a.FILE_ATTRIBUTE_READONLY,
                        ]:
                            a.set_file_attrib(i)
                    print("Token created")
                else:
                    print("Nothing to create, token already created!")
            else:
                print("Unable to create token!")
        else:
            if os.getenv(vr, False):
                print("Missing passcode!!!")
            else:
                print(
                    'Variable for token is not exist!!!\nPlease type: "ezpub -t None"'
                )


def build(path: str):
    # Build egg info, build, dist for upload to PyPI.
    # When rebuild, existing ones will be removed auto or manually by user.

    pth = Path(os.path.abspath(path))
    if os.path.isdir(pth):
        os.chdir(pth)
        folds = [
            f for i in ["build", "dist", ".egg-info"] for f in os.listdir() if i in f
        ]
        if folds:
            fda = Path(
                os.path.join(
                    ("Archive_" + pth.name),
                    f'{str(dt.timestamp(dt.now())).replace(".", "_")}',
                )
            )
            if not os.path.isdir(fda.parent):
                os.mkdir(fda.parent)
            os.mkdir(fda)
            for i in folds:
                try:
                    shutil.move(i, fda)
                except Exception as e:
                    print(e)
                    print(f"Please remove {folds} manually!")
                    if platform.startswith("win"):
                        os.startfile(path)
                    else:
                        os.system(f"open {path}")
                    sys.exit()
        pnam = (
            f"py -m build" if platform.startswith("win") else "python3 -m build".split()
        )
        with Popen(
            pnam, stdout=PIPE, bufsize=1, universal_newlines=True, text=True
        ) as p:
            for line in p.stdout:
                print(line, end="")


def popenp(pnam: str | list):
    with Popen(
        pnam, stdout=PIPE, bufsize=1, universal_newlines=True, text=True
    ) as p:
        for line in p.stdout:
            print(line, end="")


def publish(path: str):
    # Upload to PyPI.

    pth = os.path.abspath(path)
    ckplt = (
        Path(os.path.join(os.environ["USERPROFILE"], ".pypirc")), True
    ) if platform.startswith("win") else (
        Path(os.path.join(os.environ["HOME"], ".pypirc")), False
    )
    altr = os.path.exists(ckplt[0]), ckplt[1]
    match altr:
        case (True, True):
            os.chdir(ckplt[0].parent)
            pnam = f'py -m twine upload "{pth}"'
            popenp(pnam)
        case (True, False):
            os.chdir(ckplt[0].parent)
            pnam = ['python3', '-m', 'twine', 'upload', f"{pth}"]
            popenp(pnam)
        case (False, _):
            print("Please create token first!")
    del pth, ckplt, altr


def main():
    # This will only work in cli.

    parser = argparse.ArgumentParser(description="Upload projects to PyPi")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t", "--token", type=str, help="Token for publish.")
    group.add_argument(
        "-b", "--build", type=str, help="Build project, ready for publish."
    )
    group.add_argument("-p", "--publish", type=str, help="Publish to pypi.")
    args = parser.parse_args()
    if args.token:
        if args.token == "None":
            tokfile()
        else:
            tokfile(args.token)
    elif args.build:
        build(args.build)
    elif args.publish:
        publish(args.publish)


if __name__ == "__main__":
    main()

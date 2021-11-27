#
#   NatMLX
#   Copyright (c) 2021 Yusuf Olokoba.
#

from argparse import Namespace
from path import Path
from tarfile import open as open_tar
from tempfile import TemporaryDirectory
from uuid import uuid4
from yaml import safe_load as load_yaml

def hydrate (input: str, args: Namespace) -> str:
    """
    Hydrate a template string with provided arguments.

    Parameters:
        input (str): Template string.
        args (argparse.Namespace): Input arguments.

    Returns:
        str: Hydrated input string.
    """
    input = input.replace("GUID", uuid4().hex)
    input = input.replace("CLASS_NAME", args.class_name)
    input = input.replace("TAG", f"@{args.author}/{args.name}")
    input = input.replace("NAME", args.name)
    input = input.replace("AUTHOR", args.author)
    input = input.replace("DESCRIPTION", args.description)
    return input

def write_node_package (package_dir, output_path):
    """
    Write a directory tree to a Node archive.

    Parameters:
        package_dir (str): Package directory.
        output_path (str): Output package path.
    """
    with open_tar(output_path, "w:gz") as package_file:
        package_file.add(package_dir, "/")

def write_unity_package (package_dir, output_path):
    """
    Write a directory tree to a `unitypackage` archive.

    Parameters:
        package_dir (str): Package directory.
        output_path (str): Output package path.
    """
    # Create exploded tar directory
    with TemporaryDirectory() as exploded_dir:
        exploded_dir = Path(exploded_dir) / "exploded"
        # Write top level package
        _write_unity_package_file(exploded_dir, "Assets/ML", package_dir / "ML.meta")
        _write_unity_package_file(exploded_dir, f"Assets/ML/{package_dir.name}", package_dir / "predictor.meta")
        # Write package directories
        for d in package_dir.walkdirs():
            rel_path = d.relpath(package_dir)
            _write_unity_package_file(exploded_dir, f"Assets/ML/{package_dir.name}/{rel_path}", d.with_suffix(".meta"))
        # Write package files
        for d in package_dir.walkfiles():
            if d.ext == ".meta":
                continue
            meta_path = Path(d + ".meta")
            if not meta_path.exists():
                print("File has no meta:", d)
                continue
            rel_path = d.relpath(package_dir)
            _write_unity_package_file(exploded_dir, f"Assets/ML/{package_dir.name}/{rel_path}", meta_path, d)
        # Tar
        with open_tar(output_path, "w:gz") as package_file:
            package_file.add(exploded_dir, "/")

def _write_unity_package_file (package_dir, relative_path: str, meta_path, file_path = None):
    # Get GUID from meta
    with open(meta_path, "r") as p:
        package_guid = load_yaml(p)["guid"]
    # Create asset dir
    asset_dir = package_dir / package_guid
    asset_dir.makedirs()
    # Create files
    meta_path.copy(asset_dir / "asset.meta")
    with open(asset_dir / "pathname", "w") as f:
        f.write(relative_path)
    if file_path:
        file_path.copy(asset_dir / "asset")

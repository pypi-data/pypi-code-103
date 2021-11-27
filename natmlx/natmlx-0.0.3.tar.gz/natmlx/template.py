#
#   NatMLX
#   Copyright (c) 2021 Yusuf Olokoba.
#

from argparse import ArgumentParser
from path import Path
from pkg_resources import resource_filename
from tempfile import TemporaryDirectory

from .utils import hydrate, write_node_package, write_unity_package

# Define arguments
TYPE_CHOICES = ["edge", "hub"]
FRAMEWORK_CHOICES = ["unity", "node", "python"]
parser = ArgumentParser(description="NatML Predictor Template Generator")
parser.add_argument("--name", type=str, required=True, help="Package name")
parser.add_argument("--author", type=str, required=True, help="Package author")
parser.add_argument("--description", type=str, required=True, help="Package description")
parser.add_argument("--class-name", type=str, required=True, help="Predictor class name")
parser.add_argument("--type", type=str.lower, required=True, choices=TYPE_CHOICES, help="Predictor type")
parser.add_argument("--framework", type=str.lower, required=True, choices=FRAMEWORK_CHOICES, help="Development framework")
parser.add_argument("--output", type=str, required=False, help="Output path")

def main ():
    # Parse arguments
    args = parser.parse_args()
    # Create package
    with TemporaryDirectory() as package_dir:
        # Clone template 
        package_dir = Path(package_dir) / args.name
        template_dir = resource_filename("natmlx", f"templates/{args.type}_{args.framework}")
        Path(template_dir).copytree(package_dir)   
        # Hydrate
        for file in package_dir.walkfiles():
            # Substitute file contents
            if file.ext in [".cs", ".meta", ".asmdef", ".md", ".ts", ".js", ".py", ".json"]:
                with open(file, "r") as h:
                    contents = h.read()
                with open(file, "w") as h:
                    h.write(hydrate(contents, args))
            # Rename file
            file.rename(file.parent / hydrate(file.name, args))
        # Write package
        if args.framework == "node":
            write_node_package(package_dir, args.output)
        elif args.framework == "unity":
            write_unity_package(package_dir, args.output)
        elif args.framework == "python":
            pass

from argparse import ArgumentParser
from .dgx import create_app, delete_app, add_optional, create_module

parser = ArgumentParser(description='Dealergeek Generator API Express', usage='DGX', )

parser.add_argument(
    "-d",
    "--delete",
    default=None,
    required=False,
    help="Delete the project"
)
parser.add_argument(
    "-i",
    "--init",
    default=None,
    required=False,
    help="Create a new api"
)
parser.add_argument(
    "-a",
    "--add",
    default=None,
    required=False,
    help="Add a module"
)
parser.add_argument(
    "-c",
    "--create",
    default=None,
    required=False,
    help="Create a new module"
)


def main():
    """
    Evalua los parametros
    """
    args = parser.parse_args()
    if args.init:
        create_app(args.init)
    elif args.delete:
        delete_app(args.delete)
    elif args.add:
        add_optional(args.add, None)
    elif args.create:
        create_module(args.create)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

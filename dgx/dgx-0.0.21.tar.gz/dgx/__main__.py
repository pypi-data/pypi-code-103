from argparse import ArgumentParser
from .dgx import create_app, delete_app

parser = ArgumentParser(description='Dealergeek Generator API Express', usage='DGX', )

parser.add_argument(
    "-d",
    "--delete",
    default=None,
    required=False,
    help="Delete the project",
)
parser.add_argument(
    "-c",
    "--create",
    default=None,
    required=False,
    help="Create a new api",
)


def main():
    """
    Evalua los parametros
    """
    args = parser.parse_args()
    if args.create:
        create_app(args.create)
    elif args.delete:
        delete_app(args.delete)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

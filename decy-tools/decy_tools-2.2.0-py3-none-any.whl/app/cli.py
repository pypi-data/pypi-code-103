from argparse import ArgumentParser, Namespace
from .router import router
from .config import PARSER_BUILD_CONFIG
import sys


def build_argparser(build_config: dict) -> Namespace:
    parser = ArgumentParser()
    sub_parsers = parser.add_subparsers()
    for feature in build_config:
        arguments = build_config[feature]["arguments"]
        sub_parser = sub_parsers.add_parser(feature)
        for argument in arguments:
            sub_parser.add_argument(
                argument["long"],
                argument["short"],
                type=argument["arg_type"],
                required=argument["required"],
            )
            sub_parser.set_defaults(which=feature)
    return parser.parse_args()


def main():
    try:
        args = build_argparser(PARSER_BUILD_CONFIG)
        app = args.which
        workflow_router = router.Router(app, args)
        return workflow_router.run_workflow()
    except AttributeError as e:
        sys.exit("\nERROR: Please pass a subcommand. See decy-tool -h for details\n"
)


if __name__ == "__main__":
    main()

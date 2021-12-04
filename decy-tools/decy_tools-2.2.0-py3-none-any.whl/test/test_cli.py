from app.cli import build_argparser, main
from unittest.mock import Mock, patch, call


PARSER_BUILD_CONFIG = {
    "new-email": {
        "arguments": [
            {"long": "--first-name", "short": "-fn", "arg_type": str, "required": True},
        ]
    }
}


@patch("app.cli.ArgumentParser")
def test_build_argparser(mock_argparser):
    parser = build_argparser(PARSER_BUILD_CONFIG)
    mock_argparser.assert_has_calls(
        [
            call(),
            call().add_subparsers(),
            call().add_subparsers().add_parser("new-email"),
            call().add_subparsers().add_parser().add_argument("--first-name", "-fn", type=str, required=True),
            call().add_subparsers().add_parser().set_defaults(which="new-email"),
            call().parse_args(),
        ]
    )


@patch("app.cli.router")
@patch("app.cli.PARSER_BUILD_CONFIG")
@patch("app.cli.build_argparser")
def test_main(mock_argparser, mock_build_config, mock_router):
    class MockObj:
        which = "asdf"

    mock_argparser.return_value = MockObj
    main()
    mock_router.assert_has_calls([call.Router("asdf", MockObj), call.Router().run_workflow()])
    mock_argparser.assert_has_calls([call(mock_build_config)])


@patch("app.cli.router")
@patch("app.cli.PARSER_BUILD_CONFIG")
@patch("app.cli.sys.exit")
def test_main_exception(mock_exit, mock_build_config, mock_argparser):
    class MockObj:
        whichd = "asdf"

    mock_argparser.return_value = MockObj
    main()
    mock_exit.assert_has_calls([call(2), call('\nERROR: Please pass a subcommand. See decy-tool -h for details\n')])

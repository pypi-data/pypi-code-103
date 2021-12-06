"""Main function call
"""

import argparse
from pathlib import Path, PosixPath, WindowsPath
from . import deploy_script, gitlab_test, config_generator

def main():
    parser_deploy = argparse.ArgumentParser()
    parser_deploy.add_argument("-g", "--generateConfig", help="Add this flag to run config generator", action="store_true")
    parser_deploy.add_argument("remote", choices=['gitlab','github'], help="Deploy it to Gitlab or Github",nargs="?")
    parser_deploy.add_argument("config", help="Path to config/config template", type=Path)
    args = parser_deploy.parse_args()
    config_path = args.config  # type: Path
    if args.generateConfig:
        config_generator.main(config_path)
        return
    elif args.remote =="gitlab":
        gitlab_test.main(config_path)
    elif args.remote =="github":
        deploy_script.main(config_path)
    else:
        print("No option was selected")

if __name__ == "__main__":
    main()

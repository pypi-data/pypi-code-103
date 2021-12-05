from typing import AnyStr
from prompt_toolkit import print_formatted_text, ANSI


def cli() -> None:
    print(
        """
CLI to interact with Twitter API v2
    
VERSION
    withv2/0.2.1-alpha 
    
USAGE:
    $ withv2 [command]
    
COMMANDS:
    tweets          manage tweet objects, streams 
    users           manage follows, blocks & mutes
    spaces          lookup and search spaces
    lists           manage user's lists 
    
     
For documentations and more information check https://repo.twivity.dev"""
    )

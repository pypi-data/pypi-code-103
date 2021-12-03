import argparse
import socket
import os
import subprocess


from typing import AnyStr

from prompt_toolkit import prompt, print_formatted_text, ANSI, PromptSession
from prompt_toolkit.completion import WordCompleter, NestedCompleter
from prompt_toolkit.validation import Validator


def cli():
    print_formatted_text(
        ANSI(
            """

                         _  _    _            ____  
              __      __(_)| |_ | |__ __   __|___ \ 
              \ \ /\ / /| || __|| '_ \\ \ / /  __) |
               \ V  V / | || |_ | | | |\ V /  / __/ 
                \_/\_/  |_| \__||_| |_| \_/  |_____|


            """
        )
    )
    

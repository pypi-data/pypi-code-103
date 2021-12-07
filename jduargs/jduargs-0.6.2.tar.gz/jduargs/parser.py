from typing import Any, Type
import builtins
import json
import yaml
import copy
import sys

from .result import Result


class ArgumentParser:
    """A simple argument parser.
    It allows you to specify the type of each expected argument.

        The key-shorts and their values have to be given together.
    For example: if an integer \"offset\" with short being \"o\" has to take the value 100, in the command-line you would type \"-o100\".
    """

    def __init__(
        self,
        description: str = "",
        epilog: str = "",
        add_help: bool = True,
    ):
        """
        Initialization of the class.

        Parameters
        ----------
        description: string
            description of the program purpose (default is "")
        epilog: string
            last text displayed by help (default is "")
        add_help: bool
            flag to allow help to be provided (default is True)
        """
        self.arguments: dict = {}
        self.__results: dict = {}
        self.description = description
        self.epilog = epilog
        self.add_help = add_help
        self.version_number = "1.0"
        self.name = ""
        self.mail = ""

    def owner(self, name: str, version: str):
        self.name = name
        self.version_number = version

    def from_dict(self, data: dict):

        meta = data["metadata"]
        self.description = meta["description"]
        self.epilog = meta["epilog"]
        self.name = meta["owner"]
        self.version_number = meta["version"]

        args = data["arguments"]
        for key, value in args.items():
            short = value["short"]
            type = getattr(builtins, value["type"]) if "type" in value.keys() else str
            required = value["required"] if "required" in value.keys() else True
            help = value["help"] if "help" in value.keys() else ""
            choices = value["choices"] if "choices" in value.keys() else []
            multiple = value["multiple"] if "multiple" in value.keys() else False
            self.add(key, short, type, required, help, choices, multiple)

    def from_file(self, path: str):
        ext = path.split(".")[-1]

        if ext == "json":
            with open(path, "r") as f:
                data = json.load(f)
        elif ext == "yaml":
            with open(path, "r") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
        else:
            print(
                "Not a valid file extension. Option file must be a json or yaml file."
            )
            exit()

        self.from_dict(data)

    def add(
        self,
        key: str,
        short: str,
        type: type = str,
        required: bool = True,
        help: str = "",
        choices: list = [],
        multiple: bool = False,
    ) -> None:
        """Add an argument to parse.

        Parameters
        ----------
        key: string
            key of the new argument. It has to be new.
        short: string
            short representation of the key, without dash.
        type: type
            type of the argument. (default is str)
        required: boolean
            flag that specify if a key is mandatory. (default is True)
        help: str
            description of the argument. (default is "")
        choices: list
            allowed values for the argument. (default is [])
        multiple: boolean
            flag that specify if a list might be given as value (default value is False)
        """
        assert key not in self.arguments.keys(), "Key already used."
        assert isinstance(key, str), "Key must be a string."
        assert isinstance(short, str), "Short must be a string."
        assert isinstance(type, Type), "Type must be a class type."
        assert isinstance(required, bool), "Required must be a boolean."
        assert isinstance(help, str), "Description must be a string."
        assert isinstance(choices, list), "Choices must be a list."
        assert isinstance(multiple, bool), "Multiple must be a boolean."
        assert len(short) == 1, "Short must be a single character."

        self.arguments[key] = {
            "short": f"-{short}",
            "required": required,
            "type": type,
            "help": help,
            "choices": [str(c) for c in choices],
            "multiple": multiple,
        }

    def compile(self, args: list[str]) -> dict:
        """Parse the input arguments with the keys previously specified.

        Parameters
        ----------
        args: list of string
            Arguments to parse

        Returns
        -------
        dict
            dictionnary of compiled arguments keys and values
        """
        keys = [key for key, _ in self.arguments.items()]
        shorts = [value["short"] for _, value in self.arguments.items()]

        if self.add_help:
            if (
                len(args) == 0
                and len([key for key, arg in self.arguments.items() if arg["required"]])
                != 0
            ):
                print("To get help, use -h or --help command line options.")
                exit()

            if len(args) == 1 and args[0] in ["--help", "-h"]:
                self.help()
                exit()

            if len(args) == 2 and args[1] in ["--help", "-h"]:
                key = keys[shorts.index(args[0])]
                value = self.arguments[key]
                self.argument_help(key, value, 10)
                exit()

        if len(args) == 1 and args[0] in ["--version", "-v"]:
            self.version()
            exit()

        idx = 0
        while idx < len(args):
            short = args[idx]
            idx += 1

            if short in shorts:
                key = keys[shorts.index(short)]
                if self.arguments[key]["type"] == bool:
                    self.__results[key] = "True"
                    continue

                if idx == len(args):
                    print(f"Key '{short}' requires a value")
                    exit()

                self.__results[key] = args[idx]
                idx += 1

            else:
                print(f"Key '{short}' not found")
                exit()

        for key in keys:
            if self.arguments[key]["required"] and key not in self.__results.keys():
                print(
                    f"{__class__.__name__} error: '{key}' argument is required. Add it using '{self.arguments[key]['short']} <{key}>'"
                )
                exit()

        result = Result()

        for key in self.arguments:
            result.__dict__[key] = self.__getitem__(key)

        return result

    def version(self):
        """Displays the current version of the program."""
        program_name = sys.argv[0].split("\\")[-1]

        if self.name != "":
            print(f"'{program_name}' version {self.version_number} by {self.name}")
        else:
            print(f"'{program_name}' version {self.version_number}")
            print("Version number can be changed with parser.owner() method")

    def help(self):
        """Displays help for the argument to pass on the command-line."""
        if len(self.arguments) != 0:
            length_str = max([len(arg) for arg in self.arguments.keys()])
            script_name = sys.argv[0]

            arg_strs: list[str] = []
            for key, value in self.arguments.items():
                value_str = f" <{key}>" if value["type"] != bool else ""

                if value["required"]:
                    arg_strs.append(f"{value['short']}{value_str}")
                else:
                    arg_strs.append(f"[{value['short']}{value_str}]")

            print(f"usage: {script_name} {' '.join(arg_strs)}\n")
            if self.description:
                print(f"{self.description}\n")

            print(f"positional arguments:")
            for key, value in self.arguments.items():
                if value["required"]:
                    self.argument_help(key, value, length_str)

            print("")
            print(f"optional arguments:")
            for key, value in self.arguments.items():
                if not value["required"]:
                    self.argument_help(key, value, length_str)

            print("-v, --version\n\tshows the version number and exit")
            print("-h, --help\n\tshows this help message and exit")

            if self.epilog:
                print(f"\n{self.epilog}")

    def argument_help(self, key: str, value: dict, length_str: int):
        """Displays the help for a given key and value.

        Parameters
        ----------
        key: string
            key of the argument
        value: dictionnary
            dictionnary of all values related to key.
        """

        print(f"{value['short']}: {key:{length_str+10}s} {value['type']}", end="")

        if value["multiple"]:
            print(f" (list of values accepted)")
        else:
            print("")
        if value["help"]:
            print(f"\t{value['help']}")
        if value["choices"]:
            print(f"\tPossible values are {value['choices']}")

    def to_file(self, path: str):
        """Export the arguments dictionnary to file. THe file extension must be .json or .yaml.

        Parameters
        ----------
        path: string
            name of the json or yaml file to send dictionnary values to.
        """

        # arguments
        args = copy.deepcopy(self.arguments)

        for key in args.keys():
            args[key]["type"] = args[key]["type"].__name__
            args[key]["short"] = args[key]["short"][1]

        # meta
        meta = {
            "description": self.description,
            "epilog": self.epilog,
            "owner": self.name,
            "version": self.version_number,
        }

        output = {"metadata": meta, "arguments": args}

        ext = path.split(".")[-1]

        if ext == "json":
            with open(path, "w") as f:
                json.dump(output, f)
        elif ext == "yaml":
            with open(path, "w") as f:
                yaml.dump(output, f)
        else:
            print(
                "Not a valid file extension. Option file must be a json or yaml file."
            )
            exit()

    def __getitem__(self, key: str) -> Any:
        """Returns the value (with the right type) associated with a given key. If the key correspond to an optional argument that has not been given, the method returns None.

        Parameters
        ----------
        key: string
            key to retrieve the value for.

        Returns
        -------
        Any
            The value related to the given key, with the right type.

        """
        assert key in self.arguments, f'Key "{key}" not found.'

        value_type = self.arguments[key]["type"]
        multiple = self.arguments[key]["multiple"]

        if key not in self.__results:
            return value_type()

        result = self.__results[key]
        try:
            if value_type == bool:
                return value_type(eval(result))

            if multiple:
                if result[0] == "[" and result[-1] == "]":
                    values = result[1:-1].split(",")
                    return_list = []
                    for v in values:
                        if self.in_choices(key, v, value_type):
                            return_list.append(value_type(v))
                        else:
                            print(f"Provided {key} not allowed.")
                            exit()
                    return return_list
                else:
                    if self.in_choices(key, result, value_type):
                        return [value_type(result)]
                    else:
                        print(f"Provided {key} not allowed.")
                        exit()
            else:
                if self.in_choices(key, result, value_type):
                    return value_type(result)
                else:
                    print(f"Provided {key} not allowed.")
                    exit()

        except ValueError as e:
            print(
                f"{__class__.__name__} error with '{key}': {e}. Using default constructor value."
            )
            return value_type()

    def in_choices(self, key: str, value: Any, value_type: type) -> bool:
        choices = [value_type(c) for c in self.arguments[key]["choices"]]

        return not (choices and value_type(value) not in choices)

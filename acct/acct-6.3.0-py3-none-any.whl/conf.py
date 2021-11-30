CLI_CONFIG = {
    "input_file": {"positional": True, "subcommands": ["encrypt", "decrypt"],},
    "acct_key": {"os": "ACCT_KEY", "subcommands": ["encrypt", "decrypt"]},
    "crypto_plugin": {"subcommands": ["encrypt", "decrypt"]},
    "output": {"source": "rend", "subcommands": ["decrypt"]},
    "output_file": {"subcommands": ["encrypt"]},
}
CONFIG = {
    "acct_file": {"default": None, "help": "An encrypted acct file",},
    "acct_key": {
        "default": None,
        "help": "The key to encrypt the file with, if no key is passed a key will be generated and displayed on after the encrypted file is created",
    },
    "crypto_plugin": {
        "default": "fernet",
        "help": "The crypto plugin to use with acct",
    },
    "output_file": {"default": None, "help": "The output file name when encrypting"},
}
SUBCOMMANDS = {
    "encrypt": {x: "Use the acct command to encrypt data" for x in ("desc", "help")},
    "decrypt": {x: "Use the acct command to decrypt data" for x in ("desc", "help")},
}
DYNE = {
    "acct": ["acct"],
    "crypto": ["crypto"],
}

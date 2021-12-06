from pathlib import Path

from jaepeto.utils import post


def describe_file_architecture(file_path: Path) -> str:
    with open(file_path, "r") as f:
        full_contents = f.read()

    for arch_notifier in ("requests.", "boto3.resource", "MongoClient"):
        if arch_notifier in full_contents:
            with open(file_path, "r") as f:
                contents = f.readlines()

            contents = [c.strip().strip("\n") for c in contents]
            return post("arch", contents)

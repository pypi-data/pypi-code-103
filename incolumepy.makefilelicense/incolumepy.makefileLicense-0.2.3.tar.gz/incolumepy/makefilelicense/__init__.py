import toml
from pathlib import Path

__root__ = Path(__file__).parents[0]

with __root__.joinpath("version.txt").open("w") as f:
    f.write(
        toml.load(Path(__file__).parents[2].joinpath("pyproject.toml"))["tool"][
            "poetry"
        ]["version"]
    )

with __root__.joinpath("version.txt").open() as f:
    __version__ = f.readline().strip()

if __name__ == "__main__":
    ...

import requests
from pathlib import Path


def config_file() -> Path:
    return Path.home() / ".pennywise" / "pennywise.toml"


def tool_list_exists() -> bool:
    return config_file().exists()


def load_tools(user: str, branch: str) -> None:
    config_file().parent.mkdir(parents=True, exist_ok=True)

    url = f"https://raw.githubusercontent.com/{user}/pennywise/{branch}/pennywise.toml"
    response = requests.get(url)

    if response.status_code == 404:
        print(f"{user}/pennywise not found!")

    elif response.status_code == 200:
        print(f"Loading tool list from {user}/pennywise")
        config_file().write_text(response.text)

    else:
        print(f"Failed to load source from {user}")

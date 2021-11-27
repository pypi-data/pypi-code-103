from everett.manager import ConfigManager, ListOf

CONFIG = ConfigManager.basic_config()
CONFIG_SHORTCUTS = CONFIG("shortcuts", parser=ListOf(str, delimiter=", "))


def _is_shortcut(pstr: str, raise_on_missing: bool = False) -> bool:
    # https://github.com/pgierz/dots
    if pstr == "https" or pstr == "http":
        return False
    # as argument: gh:pgierz/dots
    # as config: gh=https://githubcom
    check_list = [shortcut.split("=")[0] for shortcut in CONFIG_SHORTCUTS]
    if pstr.split(":")[0] in check_list:
        return True
    if raise_on_missing:
        raise ValueError(f"Did not understand {pstr} in {check_list}!")
    return False


def _dealias_shortcut(pstr: str) -> str:
    config_shortcuts_split = [item.split("=") for item in CONFIG_SHORTCUTS]
    shortcuts: dict[str, str] = {scut: url for scut, url in config_shortcuts_split}
    shortcut, path_stub = pstr.split(":")
    dealiased_url = shortcuts.get(shortcut)
    if dealiased_url:
        return f"{dealiased_url}/{path_stub}"
    raise ValueError(f"Did not understand the shortcut {pstr} in {shortcuts}!")

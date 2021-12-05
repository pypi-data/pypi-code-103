import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.request import urlopen, urlretrieve

from appdirs import user_cache_dir

ASSETS_SEARCH_URL = "https://api.github.com/repos/kilroybot/assets/git/trees/main?recursive=1"
ENCODING = "utf-8"
FORMAT = ".ttf"
CACHE_DIR = Path(user_cache_dir("kilroy")) / "fonts"


@dataclass
class AssetData:
    path: str
    mode: str
    type: str
    sha: str
    url: str
    size: Optional[str] = None

    @property
    def filename(self) -> str:
        return Path(self.path).name

    @property
    def basename(self) -> str:
        return Path(self.path).stem


@dataclass
class FileData:
    path: str
    sha: str

    @property
    def filename(self) -> str:
        return Path(self.path).name

    @property
    def basename(self) -> str:
        return Path(self.path).stem


def search_assets(
        search_url: str = ASSETS_SEARCH_URL,
        encoding: str = ENCODING
) -> Dict[str, Any]:
    with urlopen(search_url) as url:
        return json.loads(url.read().decode(encoding=encoding))


def get_assets_data(
        *args,
        **kwargs
) -> List[AssetData]:
    data = search_assets(*args, *kwargs)
    return [AssetData(**asset) for asset in data["tree"]]


def get_available_fonts(
        *args,
        format: str = FORMAT,
        **kwargs
) -> List[AssetData]:
    assets = get_assets_data(*args, **kwargs)
    return [
        asset
        for asset in assets
        if asset.path.startswith("fonts/") and asset.path.endswith(format)
    ]


def sha256_file(
        path: Union[str, Path]
) -> str:
    sha = hashlib.sha256()
    with open(path, 'rb') as file:
        while chunk := file.read(sha.block_size):
            sha.update(chunk)
    return sha.hexdigest()


def get_cached_files(
        cache_dir: Union[str, Path]
) -> List[FileData]:
    files = [p for p in Path(str(cache_dir)).iterdir() if p.is_file()]
    return [
        FileData(
            path=str(file),
            sha=sha256_file(file)
        )
        for file in files
    ]


def download_file(
        url: str,
        to: Union[str, Path]
) -> str:
    return urlretrieve(url, str(to))[0]


def download_fonts(
        *args,
        cache_dir: Union[str, Path] = CACHE_DIR,
        **kwargs
) -> List[str]:
    cache_dir = Path(str(cache_dir))
    cache_dir.mkdir(parents=True, exist_ok=True)
    fonts = get_available_fonts(*args, **kwargs)
    cached_fonts = get_cached_files(cache_dir)
    cached_shas = set(font.sha for font in get_cached_files(cache_dir))
    new_fonts = [font for font in fonts if font.sha not in cached_shas]
    new_fonts = [
        FileData(
            path=download_file(font.url, cache_dir / font.filename),
            sha=font.sha
        )
        for font in new_fonts
    ]
    return [font.path for font in cached_fonts + new_fonts]


paths = download_fonts()

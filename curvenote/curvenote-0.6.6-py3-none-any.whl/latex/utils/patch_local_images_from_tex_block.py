import re
from itertools import chain
from typing import List

from .localize_images import ImageSummary
from .run_regex_matchers import run_regex_matchers


def patch_local_images_from_tex_block(
    regex_matchers: List[str], content: str
) -> ImageSummary:
    """
    Take a piece of tex content that we expect to contain only one includegraphics directive
    get the remote path, assign a new local path and retrun a structure that can be parsed
    """
    updated_content = content
    matches = run_regex_matchers(regex_matchers, content)

    remote_paths: List[str] = []
    local_paths: List[str] = []
    for match in matches:
        remote_path = match[1]
        hash_segment = remote_path[6:]
        local_segment = hash_segment.replace("/", "_")
        local_path = (
            remote_path.replace("block:", "images/")
            .replace("oxa:", "images/")
            .replace(hash_segment, local_segment)
        )
        updated_content = updated_content.replace(remote_path, local_path)
        remote_paths.append(remote_path)
        local_paths.append(local_path)

    return ImageSummary(
        content=updated_content,
        remote_paths=remote_paths,
        local_paths=local_paths,
    )

import re


def find_groups_in_content(regex_matcher: str, content: str):
    """
    Take a piece of tex content that we expect to contain one or more commands,
    find all instances based on the regex given and return the first groups

    Typically this is used to extract block_paths for different latex commands from
    TeX content
    """
    block_paths = []
    matches = re.finditer(regex_matcher, content)
    for match in matches:
        block_path = match[1]
        block_paths.append(block_path)

    return block_paths

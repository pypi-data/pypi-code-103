from .links import oxa_path_to_api_url
from .regex import HREF_COMMAND_OXA_REGEX
from .run_regex_matchers import run_regex_matchers


def localize_hrefs_in_content(site_url: str, content: str):
    matches = run_regex_matchers([HREF_COMMAND_OXA_REGEX], content)
    for match in matches:
        url = oxa_path_to_api_url(site_url, match[1])
        content = content.replace(match[0], f"\\href{{{url}}}")
    return content

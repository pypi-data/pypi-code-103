import unicodedata
from typing import Dict, Pattern


def remove_tags_from_string(tags: Pattern[str], text: str):
    return tags.sub('', text)


def replace_html_entities(replace_dict: Dict[str, str], text: str):
    for key in replace_dict:
        text = text.replace(key, replace_dict[key])
        text = text.strip()
    return text


def remove_emoji(text: str):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf8')

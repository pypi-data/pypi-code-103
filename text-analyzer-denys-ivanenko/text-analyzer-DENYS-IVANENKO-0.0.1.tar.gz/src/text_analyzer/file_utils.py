import os
import urllib.request

from text_analyzer.constants import HTTP, HTTPS, HEADERS


def is_link(text: str) -> bool:
    return text.startswith(HTTP) or text.startswith(HTTPS)


def clean_file_lead(file_lead: str):
    is_web_link = is_link(file_lead)
    filename = get_filename_from_file_lead(file_lead, is_web_link)
    return filename, is_web_link


def get_filename_from_file_lead(file_lead: str, is_web_link: bool) -> str:
    filename = file_lead.split("/")[-1] if is_web_link else file_lead
    return filename


def read_input_text_local(filename: str) -> str:
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} not found.")
    try:
        with open(filename) as fp:
            text = "".join(fp.readlines())
    except Exception as ex:
        print(str(ex.args[0]))
        raise ex
    text = text.replace("\n", " ")
    return text


def clean_text(raw_text: str) -> str:
    return raw_text.replace("\n", " ")


def read_input_text_web(file_link: str):
    try:
        request = urllib.request.Request(file_link, None, HEADERS)
        text = urllib.request.urlopen(request).read().decode("utf-8")
        text = clean_text(text)
    except Exception as ex:
        print(str(ex.args[0]))
        raise ex
    return text

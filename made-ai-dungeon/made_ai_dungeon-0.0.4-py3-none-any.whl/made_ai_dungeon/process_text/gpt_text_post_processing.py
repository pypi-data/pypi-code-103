import re


def gpt_text_post_processing(text: str) -> str:
    new_text_lst = text.split(">")
    new_text = text if len(new_text_lst[0]) < 10 else new_text_lst[0]
    rev_text = new_text[::-1]
    proc_text = rev_text[re.search(r"[!.?]", rev_text).end() - 1:][::-1]
    return proc_text

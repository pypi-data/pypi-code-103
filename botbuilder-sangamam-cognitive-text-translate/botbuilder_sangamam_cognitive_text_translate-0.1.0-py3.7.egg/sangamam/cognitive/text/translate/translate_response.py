from typing import List


class Translate:
    def __init__(self) -> None:
        self.lang = ''
        self.text = ''


class TranslateResponse:
    def __init__(self) -> None:
        self.from_lang = Translate()
        self.output = List[Translate]
        self.status_code = 0
        self.status_message = ''

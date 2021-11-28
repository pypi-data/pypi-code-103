class KabutobashiBaseError(Exception):
    pass


class KabutobashiPageError(KabutobashiBaseError):
    """
    Crawlが失敗したときに返すエラー
    """

    def __init__(self, url: str = ""):
        self.url = url

    def __str__(self):
        return f"error occurred when crawling [{self.url}]"


class TagNotFoundError(KabutobashiPageError):
    """
    crawlしたいページに対象のtagがない場合に返すエラー
    """

    def __init__(self, tag):
        super().__init__(url="")
        self.tag = tag

    def __str__(self):
        return f"tag [{self.tag}] not found"


class KabutobashiMethodError(KabutobashiBaseError):
    pass


class KabutobashiVisualizeError(KabutobashiBaseError):
    pass


class KabutobashiEntityError(KabutobashiBaseError):
    pass

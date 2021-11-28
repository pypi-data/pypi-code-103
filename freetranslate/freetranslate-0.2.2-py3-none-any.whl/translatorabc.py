from abc import ABC, abstractmethod 

class TranslatorABC(ABC):
    """
    Abstract class for translators, you probably don't want to use this unless you're planning to implement a translator API.
    """
    @abstractmethod
    def __init__(self, endpoint_url: str = None, endpoint_urls: list() = None):
        pass

    @abstractmethod
    def _parse_result(self, result: dict):
        pass

    @abstractmethod
    async def translate(self, text: str, target_language: str, source_language: str = "auto"):
        """
        Translate text.
        """
        pass

    @abstractmethod
    async def detect(self, text: str):
        """
        Detect language of text.
        """
        pass
    
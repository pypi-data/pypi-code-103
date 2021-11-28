from typing import Text


class BaseNASAWarning(Warning):
    CODE: Text = "NASA-WARN-001"

    def __init__(self, message: Text) -> None:
        coded_message: Text = f"{self.CODE} - {message}"
        super().__init__(coded_message)


class InvalidInputWarning(BaseNASAWarning):
    CODE: Text = "NASA-WARN-002"


class AttributesCollussionWarning(BaseNASAWarning):
    CODE: Text = "NASA-WARN-003"


class UnsupportedInputWarning(BaseNASAWarning):
    CODE: Text = "NASA-WARN-004"

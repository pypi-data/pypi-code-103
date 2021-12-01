import attr

from ..modules import Module


@attr.s(slots=True, repr=False)
class SsrfmapModule(Module):
    """
    Module that implements lifecycle methods for the SSRFmap module.
    """

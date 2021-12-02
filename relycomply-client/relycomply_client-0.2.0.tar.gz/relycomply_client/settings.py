from dryenv import DryEnv, populate_globals


class RELYCOMPLY(DryEnv):
    URL = "https://app.relycomply.com"
    TOKEN: str = None
    IMPERSONATE = ""


populate_globals()

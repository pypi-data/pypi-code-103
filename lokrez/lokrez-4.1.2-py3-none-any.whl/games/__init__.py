# =============================================================================
# -----------------------------------------------------------------------------
class Character:
    """Infos needed about a Smash character"""
    def __init__(
            self,
            name,
            codenames,
            smashggid = None,
            res_urls = {},
            ):
        self.res_urls = res_urls
        self.smashggid = smashggid
        self.name = name
        self.codenames = codenames

    def __str__(self):
        return self.name

# -----------------------------------------------------------------------------
class Game:
    def __init__(
            self,
            name,
            fullname,
            aliases,
            smashggid = None,
            ):

        self.name = name
        self.fullname = fullname
        self.aliases = aliases
        self.smashggid = smashggid

    def list_names(self):
        return [self.name] + [self.fullname] + self.aliases
    
    def __str__(self):
        return self.name

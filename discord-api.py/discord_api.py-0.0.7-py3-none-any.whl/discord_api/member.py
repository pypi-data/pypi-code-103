class Member:
    def __init__(self, client, guild, user:dict):
        self.guild = guild
        self.name = user["username"]
        self.id = user["id"]
        self.discriminator = user["discriminator"]
        self.avatar = user["avatar"]

    @classmethod
    def from_dict(cls, client, guild, data):
        return cls(client, guild, data)
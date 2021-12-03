class Member:
    def __init__(self, user:dict):
        self.name = user["username"]
        self.id = user["id"]
        self.discriminator = user["discriminator"]
        self.avatar = user["avatar"]

    @classmethod
    def from_dict(cls, data):
        return cls(data)

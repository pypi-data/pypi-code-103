from .channels import TextChannel
from .role import Role

class Guild:
    def __init__(self, client, data):
        self.name = data["name"]
        self.id = data["id"]
        self.description = data["description"]
        self.roles = [Role.from_dict(role) for role in data["roles"]]
        self.text_channels = [TextChannel.from_dict(client, i) for i in data["channels"] if i["type"] == 0]

    def get_role(self, id:int):
        role = None
        for role in self.roles:
            if role.id == id:
                break
        return role
        
    @classmethod
    def from_dict(cls, client, data):
        self = cls(client, data)
        return self

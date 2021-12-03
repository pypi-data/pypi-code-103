from .channels import TextChannel

class Guild:
    def __init__(self, client, data):
        self.name = data["name"]
        self.id = data["id"]
        self.description = data["description"]
        self.text_channels = [TextChannel.from_dict(client, i) for i in data["channels"] if i["type"] == 0]
        
    @classmethod
    def from_dict(cls, client, data):
        self = cls(client, data)
        return self
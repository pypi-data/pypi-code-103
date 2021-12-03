from digitalguide.whatsapp.WhatsAppUpdate import WhatsAppUpdate
import yaml

import time

def read_action_yaml(filename, action_functions={}):
    with open(filename) as file:
        yaml_dict = yaml.load(file, Loader=yaml.FullLoader)

    actions_dict = {}

    for key, value in yaml_dict.items():
        actions_dict[key] = Action(value, action_functions=action_functions)

    return actions_dict


class Action():
    def __init__(self, actions, action_functions={}):
        self.actions = actions
        self.action_functions = action_functions

    def __call__(self, client, update: WhatsAppUpdate, context):
        for item in self.actions:
            time.sleep(.2)
            if item["type"] == "message":
                client.messages.create(
                    body=item["text"].format(
                        **{"profileName": update.ProfileName, "echo": update.Body, **context}),
                    from_=update.To,
                    to=update.From
                )
            elif item["type"] == "venue":
                client.messages.create(
                    body=item["title"],
                    persistent_action=['geo:{},{}|{}'.format(
                        item["latitude"], item["longitude"], item["address"])],
                    from_=update.To,
                    to=update.From
                )
            elif item["type"] == "photo":
                client.messages.create(
                    media_url=item["url"],
                    from_=update.To,
                    to=update.From
                )
            elif item["type"] == "video":
                client.messages.create(
                    media_url=item["url"],
                    from_=update.To,
                    to=update.From
                )
            elif item["type"] == "media_group":
                client.messages.create(
                    media_url=item["urls"],
                    from_=update.To,
                    to=update.From
                )
            elif item["type"] == "audio" or item["type"] == "voice":
                client.messages.create(
                    media_url=[item["url"]],
                    from_=update.To,
                    to=update.From
                )
            elif item["type"] == "poll":
                message = item["question"] + "\n"
                for option in item["options"]:
                    message += option + "\n"
                client.messages.create(
                    body=message,
                    from_=update.To,
                    to=update.From
                )

            elif item["type"] == "function":
                arguments = {i: item[i]
                             for i in item if i != 'type' and i != 'func'}
                self.action_functions[item["func"]](
                    client, update, context, **arguments)

            elif item["type"] == "return":
                return item["state"]

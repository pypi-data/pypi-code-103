from typing import List
import yaml
from digitalguide.whatsapp.WhatsAppUpdate import WhatsAppUpdate
import re

from digitalguide.pattern import EMOJI_PATTERN, WEITER_PATTERN, WOHIN_PATTERN, JA_PATTERN, NEIN_PATTERN

def read_state_yml(filename, actions={}, prechecks:List=[]):
    with open(filename) as file:
        yaml_dict = yaml.load(file, Loader=yaml.FullLoader)

    states_dict = {}

    for state, handlers in yaml_dict.items():
        handler_list = prechecks[:]
        for handler in handlers:
            if handler["handler"] == "PollAnswerHandler":
                newHandler = MessageHandler(RegexFilter("^(.)+"), actions[handler["action"]])
            elif handler["handler"] == "MessageHandler":
                if handler["filter"] == "regex":
                    if handler["regex"] == "EMOJI_PATTERN":
                        newHandler = MessageHandler(RegexFilter(
                            EMOJI_PATTERN), actions[handler["action"]])
                    elif handler["regex"] == "WEITER_PATTERN":
                        newHandler = MessageHandler(RegexFilter(
                            WEITER_PATTERN), actions[handler["action"]])
                    elif handler["regex"] == "WOHIN_PATTERN":
                        newHandler = MessageHandler(RegexFilter(
                            WOHIN_PATTERN), actions[handler["action"]])
                    elif handler["regex"] == "JA_PATTERN":
                        newHandler = MessageHandler(RegexFilter(
                            JA_PATTERN), actions[handler["action"]])
                    elif handler["regex"] == "NEIN_PATTERN":
                        newHandler = MessageHandler(RegexFilter(
                            NEIN_PATTERN), actions[handler["action"]])
                    else:
                        newHandler = MessageHandler(RegexFilter(handler["regex"]), actions[handler["action"]])
                elif handler["filter"] == "text":
                    newHandler = MessageHandler(TextFilter(), actions[handler["action"]])
                elif handler["filter"] == "photo":
                    newHandler = MessageHandler(PhotoFilter(), actions[handler["action"]])
                elif handler["filter"] == "voice":
                    newHandler = MessageHandler(VoiceFilter(), actions[handler["action"]])
            elif handler["handler"] == "CommandHandler":
                newHandler = CommandHandler(handler["command"], actions[handler["action"]])
            elif handler["handler"] == "TypeHandler":
                if handler["type"] == "Update":
                    type_ = WhatsAppUpdate
                newHandler = TypeHandler(type_, actions[handler["action"]])
                
            handler_list.append(newHandler)

        states_dict[state]= handler_list

    return states_dict

class MessageHandler:
    def __init__(self, filters, callback):
        self.filters = filters
        self.callback = callback

    def check_update(self, update: WhatsAppUpdate):
        return self.filters(update)

class CommandHandler:
    def __init__(self, command, callback):
        self.command = command
        self.callback = callback

    def check_update(self, update: WhatsAppUpdate):
        if update.Body.strip("/").lower() == self.command.lower():
            return True

class TypeHandler:
    def __init__(self, type_, callback):
        self.type_ = type_
        self.callback = callback

    def check_update(self, update: WhatsAppUpdate):
        return type(update) is self.type_

class RegexFilter:
    def __init__(self, regex) -> None:
        self.regex = regex

    def __call__(self, update: WhatsAppUpdate) -> bool:
        return re.match(self.regex, update.Body)

class TextFilter:
    def __call__(self, update: WhatsAppUpdate) -> bool:
        return update.Body != ""

class PhotoFilter:
    def __call__(self, update: WhatsAppUpdate) -> bool:
        return update.MediaContentType0 and update.MediaContentType0.startswith("image")

class VoiceFilter:
    def __call__(self, update: WhatsAppUpdate) -> bool:
        return update.MediaContentType0 and update.MediaContentType0.startswith("audio")
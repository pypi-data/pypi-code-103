import yaml
from telegram import Update
from telegram.ext import (CommandHandler, Filters, MessageHandler,
                          PollAnswerHandler, TypeHandler)

from digitalguide import rasa_filter, uhrzeit_filter
from digitalguide.pattern import (EMOJI_PATTERN, JA_PATTERN, NEIN_PATTERN,
                                  WEITER_PATTERN, WOHIN_PATTERN)


def read_state_yml(filename, actions=None, prechecks: list = None):
    if actions is None:
        actions = {}
    if prechecks is None:
        prechecks = []
    with open(filename) as file:
        yaml_dict = yaml.load(file, Loader=yaml.FullLoader)

    states_dict = {}

    for state, handlers in yaml_dict.items():
        handler_list = prechecks[:]
        for handler in handlers:
            if handler["handler"] == "MessageHandler":
                if handler["filter"] == "regex":
                    if handler["regex"] == "EMOJI_PATTERN":
                        newHandler = MessageHandler(Filters.regex(
                            EMOJI_PATTERN), actions[handler["action"]])
                    elif handler["regex"] == "WEITER_PATTERN":
                        newHandler = MessageHandler(Filters.regex(
                            WEITER_PATTERN), actions[handler["action"]])
                    elif handler["regex"] == "WOHIN_PATTERN":
                        newHandler = MessageHandler(Filters.regex(
                            WOHIN_PATTERN), actions[handler["action"]])
                    elif handler["regex"] == "JA_PATTERN":
                        newHandler = MessageHandler(Filters.regex(
                            JA_PATTERN), actions[handler["action"]])
                    elif handler["regex"] == "NEIN_PATTERN":
                        newHandler = MessageHandler(Filters.regex(
                            NEIN_PATTERN), actions[handler["action"]])
                    else:
                        newHandler = MessageHandler(Filters.regex(
                            handler["regex"]), actions[handler["action"]])
                elif handler["filter"] == "text":
                    newHandler = MessageHandler(
                        Filters.text, actions[handler["action"]])
                elif handler["filter"] == "photo":
                    newHandler = MessageHandler(
                        Filters.photo, actions[handler["action"]])
                elif handler["filter"] == "voice":
                    newHandler = MessageHandler(
                        Filters.voice, actions[handler["action"]])
                elif handler["filter"] == "rasa":
                    newHandler = MessageHandler(
                        rasa_filter.FilterRasa(handler["intent"]), actions[handler["action"]])
                elif handler["filter"] == "uhrzeit":
                    newHandler = MessageHandler(
                        uhrzeit_filter.FilterUhrzeit(), actions[handler["action"]])
                else:
                    raise NotImplementedError(
                        "This filter is not implemented: {}".format(handler["filter"]))
            elif handler["handler"] == "CommandHandler":
                newHandler = CommandHandler(
                    handler["command"], actions[handler["action"]])
            elif handler["handler"] == "PollAnswerHandler":
                newHandler = PollAnswerHandler(actions[handler["action"]])
            elif handler["handler"] == "TypeHandler":
                if handler["type"] == "Update":
                    type_ = Update
                newHandler = TypeHandler(type_, actions[handler["action"]])
            else:
                raise NotImplementedError(
                    "This Handler is not implemented: {}".format(handler["handler"]))

            handler_list.append(newHandler)

        states_dict[state] = handler_list

    return states_dict

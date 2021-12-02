from .base import Action, Item


class ActionEnum:
    action_695 = Action(695, "礼品码", example='"p": {"code": "AUC"}')
    action_11016 = Action(11016, "队列的设置", example='')

    def __init__(self):
        pass


class ItemEnum:
    item_600001 = Item(600001, item_name="大体力瓶")
    item_600002 = Item(600002, item_name="大体力瓶")
    item_910005 = Item(910005, item_name='玉米')

    def __init__(self):
        pass

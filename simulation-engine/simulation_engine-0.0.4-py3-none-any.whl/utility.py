def get_set_name(item_name):
    if "Kavasa" not in item_name:
        return item_name.split("Prime", 1)[0] + "Prime"
    else:
        return "Kavasa Prime Kubrow Collar"


def get_set_price(item_name, set_data):
    if item_name != "Forma Blueprint":
        return set_data[get_set_name(item_name)]['plat']
    else:
        return 0


def get_price(item_name, set_data):
    if item_name != "Forma Blueprint":
        return set_data[get_set_name(item_name)]['parts'][item_name]['plat']
    else:
        return 0


def get_ducats(item_name, set_data):
    if item_name != "Forma Blueprint":
        return set_data[get_set_name(item_name)]['parts'][item_name]['ducats']
    else:
        return 0

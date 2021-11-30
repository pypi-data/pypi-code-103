from browser import window, document, aio, bind
from invitation import InvitationManager
from javascript import JSON
from aio_bridge import Bridge, BridgeException
import dialog


bridge = Bridge()
lists_ns = window.lists_ns
pubsub_service = window.pubsub_service
pubsub_node = window.pubsub_node
list_type = window.list_type
try:
    affiliations = window.affiliations.to_dict()
except AttributeError:
    pass

@bind("#button_manage", "click")
def manage_click(evt):
    evt.stopPropagation()
    evt.preventDefault()
    pubsub_data = {
        "namespace": lists_ns,
        "service": pubsub_service,
        "node": pubsub_node
    }
    try:
        name = pubsub_node.split('_', 1)[1]
    except IndexError:
        pass
    else:
        name = name.strip()
        if name:
            pubsub_data['name'] = name
    manager = InvitationManager("pubsub", pubsub_data)
    manager.attach(affiliations=affiliations)


async def on_delete(evt):
    item_elt = evt.target.closest(".item")
    if item_elt is None:
        dialog.notification.show(
            "Can't find parent item element",
            level="error"
        )
        return
    item_elt.classList.add("selected_for_deletion")
    item = JSON.parse(item_elt.dataset.item)
    confirmed = await dialog.Confirm(
        f"{item['name']!r} will be deleted, are you sure?",
        ok_label="delete",
        ok_color="danger",
    ).ashow()
    item_elt.classList.remove("selected_for_deletion")
    if confirmed:
        try:
            await bridge.psItemRetract(pubsub_service, pubsub_node, item["id"], True)
        except Exception as e:
            dialog.notification.show(
                f"Can't delete list item: {e}",
                level="error"
            )
        else:
            dialog.notification.show("list item deleted successfuly")
            item_elt.remove()


async def on_next_state(evt):
    """Update item with next state

    Only used with grocery list at the moment
    """
    evt.stopPropagation()
    evt.preventDefault()
    # FIXME: states are currently hardcoded, it would be better to use schema
    item_elt = evt.target.closest(".item")
    if item_elt is None:
        dialog.notification.show(
            "Can't find parent item element",
            level="error"
        )
        return
    item = JSON.parse(item_elt.dataset.item)
    try:
        status = item["status"]
    except (KeyError, IndexError) as e:
        dialog.notification.show(
            f"Can't get item status: {e}",
            level="error"
        )
        status = "to_buy"
    if status == "to_buy":
        item["status"] = "bought"
        class_update_method = item_elt.classList.add
        checked = True
    elif status == "bought":
        item["status"] = "to_buy"
        checked = False
        class_update_method = item_elt.classList.remove
    else:
        dialog.notification.show(
            f"unexpected item status: {status!r}",
            level="error"
        )
        return
    item_elt.dataset.item = JSON.stringify(item)
    try:
        await bridge.listSet(
            pubsub_service,
            pubsub_node,
            # FIXME: value type should be consistent, or we should serialise
            {k: (v if isinstance(v, list) else [v]) for k,v in item.items()},
            "",
            item["id"],
            ""
        )
    except BridgeException as e:
        dialog.notification.show(
            f"Can't udate list item: {e.message}",
            level="error"
        )
    else:
        evt.target.checked = checked
        class_update_method("list-item-closed")


if list_type == "grocery":
    for elt in document.select('.click_to_delete'):
        elt.bind("click", lambda evt: aio.run(on_delete(evt)))

    for elt in document.select('.click_to_next_state'):
        elt.bind("click", lambda evt: aio.run(on_next_state(evt)))


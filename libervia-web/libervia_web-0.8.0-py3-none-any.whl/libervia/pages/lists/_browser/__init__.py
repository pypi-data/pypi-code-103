from browser import DOMNode, document, aio
from javascript import JSON
from aio_bridge import Bridge, BridgeException
import dialog

bridge = Bridge()


async def on_delete(evt):
    evt.stopPropagation()
    evt.preventDefault()
    target = evt.currentTarget
    item_elt = DOMNode(target.closest('.item'))
    item_elt.classList.add("selected_for_deletion")
    item = JSON.parse(item_elt.dataset.item)
    confirmed = await dialog.Confirm(
        f"List {item['name']!r} will be deleted, are you sure?",
        ok_label="delete",
    ).ashow()

    if not confirmed:
        item_elt.classList.remove("selected_for_deletion")
        return

    try:
        await bridge.interestRetract("", item['id'])
    except BridgeException as e:
        dialog.notification.show(
            f"Can't remove list {item['name']!r} from personal interests: {e}",
            "error"
        )
    else:
        print(f"{item['name']!r} removed successfuly from list of interests")
        item_elt.classList.add("state_deleted")
        item_elt.bind("transitionend", lambda evt: item_elt.remove())
        if item.get("creator", False):
            try:
                await bridge.psNodeDelete(
                    item['service'],
                    item['node'],
                )
            except BridgeException as e:
                dialog.notification.show(
                    f"Error while deleting {item['name']!r}: {e}",
                    "error"
                )
            else:
                dialog.notification.show(f"{item['name']!r} has been deleted")


for elt in document.select('.action_delete'):
    elt.bind("click", lambda evt: aio.run(on_delete(evt)))

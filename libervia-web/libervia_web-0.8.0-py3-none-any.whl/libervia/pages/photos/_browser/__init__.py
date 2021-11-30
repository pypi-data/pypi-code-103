from browser import window, bind, DOMNode
from javascript import JSON
from bridge import Bridge
import dialog

bridge = Bridge()


def album_delete_cb(item_elt, item):
    print(f"deleted {item['name']}")


def album_delete_eb(failure, item_elt, item):
    # TODO: cleaner error notification
    window.alert(f"error while deleting {item['name']}: failure")


def interest_retract_cb(item_elt, item):
    print(f"{item['name']} removed successfuly from list of interests")
    item_elt.classList.add("state_deleted")
    item_elt.bind("transitionend", lambda evt: item_elt.remove())
    bridge.fileSharingDelete(
        item['service'],
        item.get('path', ''),
        item.get('files_namespace', ''),
        callback=lambda __: album_delete_cb(item_elt, item),
        errback=lambda failure: album_delete_eb(failure, item_elt, item),
    )


def interest_retract_eb(failure_, item_elt, item):
    # TODO: cleaner error notification
    window.alert(f"Can't delete album {item['name']}: {failure_['message']}")


def delete_ok(evt, notif_elt, item_elt, item):
    bridge.interestRetract(
        "", item['id'],
        callback=lambda: interest_retract_cb(item_elt, item),
        errback=lambda failure:interest_retract_eb(failure, item_elt, item))


def delete_cancel(evt, notif_elt, item_elt, item):
    notif_elt.remove()
    item_elt.classList.remove("selected_for_deletion")


@bind(".action_delete", "click")
def on_delete(evt):
    evt.stopPropagation()
    target = evt.currentTarget
    item_elt = DOMNode(target.closest('.item'))
    item_elt.classList.add("selected_for_deletion")
    item = JSON.parse(item_elt.dataset.item)
    dialog.Confirm(
        f"album {item['name']!r} will be deleted (inluding all its photos), "
        f"are you sure?",
        ok_label="delete",
    ).show(
        ok_cb=lambda evt, notif_elt: delete_ok(evt, notif_elt, item_elt, item),
        cancel_cb=lambda evt, notif_elt: delete_cancel(evt, notif_elt, item_elt, item),
    )

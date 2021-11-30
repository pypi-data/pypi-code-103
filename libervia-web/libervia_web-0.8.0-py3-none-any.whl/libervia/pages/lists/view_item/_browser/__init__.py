from browser import document, window, aio
from aio_bridge import Bridge
import dialog

try:
    pubsub_service = window.pubsub_service
    pubsub_node = window.pubsub_node
    pubsub_item = window.pubsub_item
except AttributeError:
    can_delete = False
else:
    bridge = Bridge()
    can_delete = True


async def on_delete(evt):
    evt.stopPropagation()
    confirmed = await dialog.Confirm(
        "This item will be deleted, are you sure?",
        ok_label="delete",
        ok_color="danger",
    ).ashow()
    if confirmed:
        try:
            comments_service = window.comments_service
            comments_node = window.comments_node
        except AttributeError:
            pass
        else:
            print(f"deleting comment node at [{comments_service}] {comments_node!r}")
            try:
                await bridge.psNodeDelete(comments_service, comments_node)
            except Exception as e:
                dialog.notification.show(
                    f"Can't delete comment node: {e}",
                    level="error"
                )

        print(f"deleting list item {pubsub_item!r} at [{pubsub_service}] {pubsub_node!r}")
        try:
            await bridge.psItemRetract(pubsub_service, pubsub_node, pubsub_item, True)
        except Exception as e:
            dialog.notification.show(
                f"Can't delete list item: {e}",
                level="error"
            )
        else:
            # FIXME: Q&D way to get list view URL, need to have a proper method (would
            #   be nice to have a way to reference pages by name from browser)
            list_url = '/'.join(window.location.pathname.split('/')[:-1]).replace(
                'view_item', 'view')
            window.location.replace(list_url)


if can_delete:
    for elt in document.select('.action_delete'):
        elt.bind("click", lambda evt: aio.run(on_delete(evt)))

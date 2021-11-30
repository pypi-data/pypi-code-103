from browser import document, window, bind, html, DOMNode, aio
from javascript import JSON
from bridge import Bridge
from aio_bridge import Bridge as AIOBridge
from template import Template
import dialog
from slideshow import SlideShow
from invitation import InvitationManager
import alt_media_player
# we use tmp_aio because `blob` is not handled in Brython's aio
import tmp_aio
import loading


cache_path = window.cache_path
files_service = window.files_service
files_path = window.files_path
try:
    affiliations = window.affiliations.to_dict()
except AttributeError:
    pass
bridge = Bridge()
aio_bridge = AIOBridge()

alt_media_player.install_if_needed()

photo_tpl = Template('photo/item.html')
player_tpl = Template('components/media_player.html')

# file upload

def on_progress(ev, photo_elt):
    if ev.lengthComputable:
        percent = int(ev.loaded/ev.total*100)
        update_progress(photo_elt, percent)


def on_load(file_, photo_elt):
    update_progress(photo_elt, 100)
    photo_elt.classList.add("progress_finished")
    photo_elt.classList.remove("progress_started")
    photo_elt.select_one('.action_delete').bind("click", on_delete)
    print(f"file {file_.name} uploaded correctly")


def on_error(failure, file_, photo_elt):
    dialog.notification.show(
        f"can't upload {file_.name}: {failure}",
        level="error"
    )


def update_progress(photo_elt, new_value):
    progress_elt = photo_elt.select_one("progress")
    progress_elt.value = new_value
    progress_elt.text = f"{new_value}%"


def on_slot_cb(file_, upload_slot, photo_elt):
    put_url, get_url, headers = upload_slot
    xhr = window.XMLHttpRequest.new()
    xhr.open("PUT", put_url, True)
    xhr.upload.bind('progress', lambda ev: on_progress(ev, photo_elt))
    xhr.upload.bind('load', lambda ev: on_load(file_, photo_elt))
    xhr.upload.bind('error', lambda ev: on_error(xhr.response, file_, photo_elt))
    xhr.setRequestHeader('Xmpp-File-Path', window.encodeURIComponent(files_path))
    xhr.setRequestHeader('Xmpp-File-No-Http', "true")
    xhr.send(file_)


def on_slot_eb(file_, failure, photo_elt):
    dialog.notification.show(
        f"Can't get upload slot: {failure['message']}",
        level="error"
    )
    photo_elt.remove()


def upload_files(files):
    print(f"uploading {len(files)} files")
    album_items = document['album_items']
    for file_ in files:
        url = window.URL.createObjectURL(file_)
        photo_elt = photo_tpl.get_elt({
            "file": {
                "name": file_.name,
                # we don't want to open the file on click, it's not yet the
                # uploaded URL
                "url": url,
                # we have no thumb yet, so we use the whole image
                # TODO: reduce image for preview
                "thumb_url": url,
            },
            "uploading": True,
        })
        photo_elt.classList.add("progress_started")
        album_items <= photo_elt

        bridge.fileHTTPUploadGetSlot(
            file_.name,
            file_.size,
            file_.type or '',
            files_service,
            callback=lambda upload_slot, file_=file_, photo_elt=photo_elt:
                on_slot_cb(file_, upload_slot, photo_elt),
            errback=lambda failure, file_=file_, photo_elt=photo_elt:
                on_slot_eb(file_, failure, photo_elt),
        )


@bind("#file_drop", "drop")
def on_file_select(evt):
    evt.stopPropagation()
    evt.preventDefault()
    files = evt.dataTransfer.files
    upload_files(files)


@bind("#file_drop", "dragover")
def on_drag_over(evt):
    evt.stopPropagation()
    evt.preventDefault()
    evt.dataTransfer.dropEffect = 'copy'


@bind("#file_input", "change")
def on_file_input_change(evt):
    files = evt.currentTarget.files
    upload_files(files)

# delete

def file_delete_cb(item_elt, item):
    item_elt.classList.add("state_deleted")
    item_elt.bind("transitionend", lambda evt: item_elt.remove())
    print(f"deleted {item['name']}")


def file_delete_eb(failure, item_elt, item):
    dialog.notification.show(
        f"error while deleting {item['name']}: failure",
        level="error"
    )


def delete_ok(evt, notif_elt, item_elt, item):
    file_path = f"{files_path.rstrip('/')}/{item['name']}"
    bridge.fileSharingDelete(
        files_service,
        file_path,
        "",
        callback=lambda : file_delete_cb(item_elt, item),
        errback=lambda failure: file_delete_eb(failure, item_elt, item),
    )


def delete_cancel(evt, notif_elt, item_elt, item):
    notif_elt.remove()
    item_elt.classList.remove("selected_for_deletion")


def on_delete(evt):
    evt.stopPropagation()
    target = evt.currentTarget
    item_elt = DOMNode(target.closest('.item'))
    item_elt.classList.add("selected_for_deletion")
    item = JSON.parse(item_elt.dataset.item)
    dialog.Confirm(
        f"{item['name']!r} will be deleted, are you sure?",
        ok_label="delete",
        ok_color="danger",
    ).show(
        ok_cb=lambda evt, notif_elt: delete_ok(evt, notif_elt, item_elt, item),
        cancel_cb=lambda evt, notif_elt: delete_cancel(evt, notif_elt, item_elt, item),
    )

# cover

async def cover_ok(evt, notif_elt, item_elt, item):
    # we first need to get a blob of the image
    img_elt = item_elt.select_one("img")
    # the simplest way is to download it
    r = await tmp_aio.ajax("GET", img_elt.src, "blob")
    if r.status != 200:
        dialog.notification.show(
            f"can't retrieve cover: {r.status}: {r.statusText}",
            level="error"
        )
        return
    img_blob = r.response
    # now we'll upload it via HTTP Upload, we need a slow
    img_name = img_elt.src.rsplit('/', 1)[-1]
    img_size = img_blob.size

    slot = await aio_bridge.fileHTTPUploadGetSlot(
        img_name,
        img_size,
        '',
        files_service
    )
    get_url, put_url, headers = slot
    # we have the slot, we can upload image
    r = await tmp_aio.ajax("PUT", put_url, "", img_blob)
    if r.status != 201:
        dialog.notification.show(
            f"can't upload cover: {r.status}: {r.statusText}",
            level="error"
        )
        return
    extra = {"thumb_url": get_url}
    album_name = files_path.rsplit('/', 1)[-1]
    await aio_bridge.interestsRegisterFileSharing(
        files_service,
        "photos",
        "",
        files_path,
        album_name,
        JSON.stringify(extra),
    )
    dialog.notification.show("Album cover has been changed")


def cover_cancel(evt, notif_elt, item_elt, item):
    notif_elt.remove()
    item_elt.classList.remove("selected_for_action")


def on_cover(evt):
    evt.stopPropagation()
    target = evt.currentTarget
    item_elt = DOMNode(target.closest('.item'))
    item_elt.classList.add("selected_for_action")
    item = JSON.parse(item_elt.dataset.item)
    dialog.Confirm(
        f"use {item['name']!r} for this album cover?",
        ok_label="use as cover",
    ).show(
        ok_cb=lambda evt, notif_elt: aio.run(cover_ok(evt, notif_elt, item_elt, item)),
        cancel_cb=lambda evt, notif_elt: cover_cancel(evt, notif_elt, item_elt, item),
    )


# slideshow

@bind(".photo_thumb_click", "click")
def photo_click(evt):
    evt.stopPropagation()
    evt.preventDefault()
    slideshow = SlideShow()
    target = evt.currentTarget
    clicked_item_elt = DOMNode(target.closest('.item'))

    slideshow.attach()
    for idx, item_elt in enumerate(document.select('.item')):
        item = JSON.parse(item_elt.dataset.item)
        try:
            biggest_thumb = item['extra']['thumbnails'][-1]
            thumb_url = f"{cache_path}{biggest_thumb['filename']}"
        except (KeyError, IndexError) as e:
            print(f"Can't get full screen thumbnail URL: {e}")
            thumb_url = None
        if item.get("mime_type", "")[:5] == "video":
            player = alt_media_player.MediaPlayer(
                [item['url']],
                poster = thumb_url,
                reduce_click_area =  True
            )
            elt = player.elt
            elt.classList.add("slide_video", "no_fullscreen")
            slideshow.add_slide(
                elt,
                item,
                options={
                    "flags": (alt_media_player.NO_PAGINATION, alt_media_player.NO_SCROLLBAR),
                    "exit_callback": player.reset,
                }
            )
        else:
            slideshow.add_slide(html.IMG(src=thumb_url or item['url'], Class="slide_img"), item)
        if item_elt == clicked_item_elt:
            slideshow.index = idx


for elt in document.select('.action_delete'):
    elt.bind("click", on_delete)
for elt in document.select('.action_cover'):
    elt.bind("click", on_cover)

# manage


@bind("#button_manage", "click")
def manage_click(evt):
    evt.stopPropagation()
    evt.preventDefault()
    manager = InvitationManager("photos", {"service": files_service, "path": files_path})
    manager.attach(affiliations=affiliations)


# hint
@bind("#hint .click_to_delete", "click")
def remove_hint(evt):
    document['hint'].remove()


loading.remove_loading_screen()

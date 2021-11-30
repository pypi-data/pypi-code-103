"""text edition management"""

from browser import document, window, aio, bind, timer
from browser.local_storage import storage
from browser.object_storage import ObjectStorage
from javascript import JSON
from aio_bridge import Bridge, BridgeException
from template import Template
import dialog

bridge = Bridge()
object_storage = ObjectStorage(storage)
profile = window.profile

# how often we save forms, in seconds
AUTOSAVE_FREQUENCY = 20


def serialise_form(form_elt):
    ret = {}
    for elt in form_elt.elements:
        if elt.tagName == "INPUT":
            if elt.type in ("hidden", "submit"):
                continue
            elif elt.type == "text":
                ret[elt.name] = elt.value
            else:
                print(f"elt.type not managet yet: {elt.type}")
                continue
        elif elt.tagName == "TEXTAREA":
            ret[elt.name] = elt.value
        elif elt.tagName in ("BUTTON",):
            continue
        else:
            print(f"tag not managet yet: {elt.tagName}")
            continue
    return ret


def restore_form(form_elt, data):
    for elt in form_elt.elements:
        if elt.tagName not in ("INPUT", "TEXTAREA"):
            continue
        try:
            value = data[elt.name]
        except KeyError:
            continue
        else:
            elt.value = value


def set_form_autosave(form_id):
    """Save locally form data regularly and restore it until it's submitted

    form is saved every AUTOSAVE_FREQUENCY seconds and when visibility is lost.
    Saved data is restored when the method is called.
    Saved data is cleared when the form is submitted.
    """
    if profile is None:
        print(f"No session started, won't save and restore form {form_id}")
        return

    form_elt = document[form_id]
    submitted = False

    key = {"profile": profile, "type": "form_autosave", "form": form_id}
    try:
        form_saved_data = object_storage[key]
    except KeyError:
        last_serialised = None
    else:
        print(f"restoring content of form {form_id!r}")
        last_serialised = form_saved_data
        restore_form(form_elt, form_saved_data)

    def save_form():
        if not submitted:
            nonlocal last_serialised
            serialised = serialise_form(form_elt)
            if serialised != last_serialised:
                last_serialised = serialised
                print(f"saving content of form {form_id!r}")
                object_storage[key] = serialised

    @bind(form_elt, "submit")
    def on_submit(evt):
        nonlocal submitted
        submitted = True
        print(f"clearing stored content of form {form_id!r}")
        try:
            del object_storage[key]
        except KeyError:
            print("key error")
            pass

    @bind(document, "visibilitychange")
    def on_visibiliy_change(evt):
        print("visibility change")
        if document.visibilityState != "visible":
            save_form()

    timer.set_interval(save_form, AUTOSAVE_FREQUENCY * 1000)


class TagsEditor:

    def __init__(self, input_selector):
        print("installing Tags Editor")
        self.input_elt = document.select_one(input_selector)
        self.input_elt.style.display = "none"
        tags_editor_tpl = Template('editor/tags_editor.html')
        self.tag_tpl = Template('editor/tag.html')

        editor_elt = tags_editor_tpl.get_elt()
        self.input_elt.parent <= editor_elt
        self.tag_input_elt = editor_elt.select_one(".tag_input")
        self.tag_input_elt.bind("keydown", self.on_key_down)
        self._current_tags = None
        self.tags_map = {}
        for tag in self.current_tags:
            self.add_tag(tag, force=True)

    @property
    def current_tags(self):
        if self._current_tags is None:
            self._current_tags = {
                t.strip() for t in self.input_elt.value.split(',') if t.strip()
            }
        return self._current_tags

    @current_tags.setter
    def current_tags(self, tags):
        self._current_tags = tags

    def add_tag(self, tag, force=False):
        tag = tag.strip()
        if not force and (not tag or tag in self.current_tags):
            return
        self.current_tags = self.current_tags | {tag}
        self.input_elt.value = ','.join(self.current_tags)
        tag_elt = self.tag_tpl.get_elt({"label": tag})
        self.tags_map[tag] = tag_elt
        self.tag_input_elt.parent.insertBefore(tag_elt, self.tag_input_elt)
        tag_elt.select_one(".click_to_delete").bind(
            "click", lambda evt: self.on_tag_click(evt, tag)
        )

    def remove_tag(self, tag):
        try:
            tag_elt = self.tags_map[tag]
        except KeyError:
            print(f"trying to remove an inexistant tag: {tag}")
        else:
            self.current_tags = self.current_tags - {tag}
            self.input_elt.value = ','.join(self.current_tags)
            tag_elt.remove()

    def on_tag_click(self, evt, tag):
        evt.stopPropagation()
        self.remove_tag(tag)

    def on_key_down(self, evt):
        if evt.key in (",", "Enter"):
            evt.stopPropagation()
            evt.preventDefault()
            self.add_tag(self.tag_input_elt.value)
            self.tag_input_elt.value = ""


class BlogEditor:
    """Editor class, handling tabs, preview, and submit loading button

    It's using and HTML form as source
    The form must have:
        - a "title" text input
        - a "body" textarea
        - an optional "tags" text input with comma separated tags (may be using Tags
          Editor)
        - a "tab_preview" tab element
    """

    def __init__(self, form_id="blog_post_edit"):
        self.tab_select = window.tab_select
        self.item_tpl = Template('blog/item.html')
        self.form = document[form_id]
        for elt in document.select(".click_to_edit"):
            elt.bind("click", self.on_edit)
        for elt in document.select('.click_to_preview'):
            elt.bind("click", lambda evt: aio.run(self.on_preview(evt)))
        self.form.bind("submit", self.on_submit)


    def on_edit(self, evt):
        self.tab_select(evt.target, "tab_edit", "is-active")

    async def on_preview(self, evt):
        """Generate a blog preview from HTML form

        """
        print("on preview OK")
        elt = evt.target
        tab_preview = document["tab_preview"]
        tab_preview.clear()
        data = {
            "content_rich": self.form.select_one('textarea[name="body"]').value.strip()
        }
        title = self.form.select_one('input[name="title"]').value.strip()
        if title:
            data["title_rich"] = title
        tags_input_elt = self.form.select_one('input[name="tags"]')
        if tags_input_elt is not None:
            tags = tags_input_elt.value.strip()
            if tags:
                data['tags'] = [t.strip() for t in tags.split(',') if t.strip()]
        try:
            preview_data = JSON.parse(
                await bridge.mbPreview("", "", JSON.stringify(data))
            )
        except BridgeException as e:
            dialog.notification.show(
                f"Can't generate item preview: {e.message}",
                level="error"
            )
        else:
            self.tab_select(elt, "tab_preview", "is-active")
            item_elt = self.item_tpl.get_elt({
                "item": preview_data,
                "dates_format": "short",
            })
            tab_preview <= item_elt

    def on_submit(self, evt):
        submit_btn = document.select_one("button[type='submit']")
        submit_btn.classList.add("is-loading")

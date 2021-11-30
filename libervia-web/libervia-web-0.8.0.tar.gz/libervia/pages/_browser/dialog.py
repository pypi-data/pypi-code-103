"""manage common dialogs"""

from browser import document, window, timer
from template import Template


class Confirm:

    def __init__(self, message, ok_label="", cancel_label="", ok_color="success"):
        self._tpl = Template("dialogs/confirm.html")
        self.message = message
        self.ok_label = ok_label
        assert ok_color in ("success", "danger")
        self.ok_color = ok_color
        self.cancel_label = cancel_label

    def cancel_cb(self, evt, notif_elt):
        notif_elt.remove()

    def show(self, ok_cb, cancel_cb=None):
        if cancel_cb is None:
            cancel_cb = self.cancel_cb
        notif_elt = self._tpl.get_elt({
            "message": self.message,
            "ok_label": self.ok_label,
            "ok_color": self.ok_color,
            "cancel_label": self.cancel_label,
        })

        document['notifs_area'] <= notif_elt
        timer.set_timeout(lambda: notif_elt.classList.add('state_appended'), 0)
        for cancel_elt in notif_elt.select(".click_to_cancel"):
            cancel_elt.bind("click", lambda evt: cancel_cb(evt, notif_elt))
        for cancel_elt in notif_elt.select(".click_to_ok"):
            cancel_elt.bind("click", lambda evt: ok_cb(evt, notif_elt))

    def _ashow_cb(self, evt, notif_elt, resolve_cb, confirmed):
        evt.stopPropagation()
        notif_elt.remove()
        resolve_cb(confirmed)

    async def ashow(self):
        return window.Promise.new(
            lambda resolve_cb, reject_cb:
            self.show(
                lambda evt, notif_elt: self._ashow_cb(evt, notif_elt, resolve_cb, True),
                lambda evt, notif_elt: self._ashow_cb(evt, notif_elt, resolve_cb, False)
            )
        )


class Notification:

    def __init__(self):
        self._tpl = Template("dialogs/notification.html")

    def close(self, notif_elt):
        notif_elt.classList.remove('state_appended')
        notif_elt.bind("transitionend", lambda __: notif_elt.remove())

    def show(
        self,
        message: str,
        level: str = "info",
        delay: int = 5
    ) -> None:
        # we log in console error messages, may be useful
        if level in ("warning", "error"):
            print(f"[{level}] {message}")
        notif_elt = self._tpl.get_elt({
            "message": message,
            "level": level,
        })
        document["notifs_area"] <= notif_elt
        timer.set_timeout(lambda: notif_elt.classList.add('state_appended'), 0)
        timer.set_timeout(lambda: self.close(notif_elt), delay * 1000)
        for elt in notif_elt.select('.click_to_close'):
            elt.bind('click', lambda __: self.close(notif_elt))


notification = Notification()

from browser import document, window, html, timer, DOMNode
from js_modules.swiper import Swiper
from template import Template


class SlideShow:

    def __init__(self):
        self.swiper = None
        slideshow_tpl = Template('photo/slideshow.html')
        self.slideshow_elt = slideshow_tpl.get_elt()
        self.comments_count_elt = self.slideshow_elt.select_one('.comments__count')
        self.wrapper = self.slideshow_elt.select_one(".swiper-wrapper")
        self.hidden_elts = {}
        self.control_hidden = False
        self.click_timer = None
        self._class_to_remove = set()
        self._exit_callback = None

    @property
    def current_slide(self):
        if self.swiper is None:
            return None
        try:
            return DOMNode(self.swiper.slides[self.swiper.realIndex])
        # getting missing item in JS arrays returns KeyError
        except KeyError:
            return None

    @property
    def current_item(self):
        """item attached to the current slide, if any"""
        current = self.current_slide
        if current is None:
            return None
        try:
            return current._item
        except AttributeError:
            return None

    @property
    def current_options(self):
        """options attached to the current slide, if any"""
        current = self.current_slide
        if current is None:
            return None
        try:
            return current._options
        except AttributeError:
            return None

    @property
    def index(self):
        if self.swiper is None:
            return None
        return self.swiper.realIndex

    @index.setter
    def index(self, idx):
        if self.swiper is not None:
            self.swiper.slideTo(idx, 0)

    def attach(self):
        # we hide other elts to avoid scrolling issues
        for elt in document.body.children:
            try:
                self.hidden_elts[elt] = elt.style.display
            except AttributeError:
                pass
                # FIXME: this is a workaround needed because Brython's children method
                #   is returning all nodes,
                #   cf. https://github.com/brython-dev/brython/issues/1657
                #   to be removed when Brython is fixed.
            else:
                elt.style.display = "none"
        document.body <= self.slideshow_elt
        self.swiper = Swiper.new(
            ".swiper-container",
            {
                # default 0 value results in lot of accidental swipes, notably when media
                # player is used
                "threshold": 10,
                "pagination": {
                    "el": ".swiper-pagination",
                },
                "navigation": {
                    "nextEl": ".swiper-button-next",
                    "prevEl": ".swiper-button-prev",
                },
                "scrollbar": {
                    "el": ".swiper-scrollbar",
                },
                "grabCursor": True,
                "keyboard": {
                    "enabled": True,
                    "onlyInViewport": False,
                },
                "mousewheel": True,
                "zoom": {
                    "maxRatio": 15,
                    "toggle": False,
                },
            }
        )
        window.addEventListener("keydown", self.on_key_down, True)
        self.slideshow_elt.select_one(".click_to_close").bind("click", self.on_close)
        self.slideshow_elt.select_one(".click_to_comment").bind("click", self.on_comment)

        # we don't use swiper.on for "click" and "dblclick" (or "doubleTap" in swiper
        # terms) because it breaks event propagation management, which cause trouble with
        # media player
        self.slideshow_elt.bind("click", self.on_click)
        self.slideshow_elt.bind("dblclick", self.on_dblclick)
        self.swiper.on("slideChange", self.on_slide_change)
        self.on_slide_change(self.swiper)
        self.fullscreen(True)

    def add_slide(self, elt, item_data=None, options=None):
        slide_elt = html.DIV(Class="swiper-slide")
        zoom_cont_elt = html.DIV(Class="swiper-zoom-container")
        slide_elt <= zoom_cont_elt
        zoom_cont_elt <= elt
        slide_elt._item = item_data
        if options is not None:
            slide_elt._options = options
        self.swiper.appendSlide([slide_elt])
        self.swiper.update()

    def quit(self):
        # we unhide
        for elt, display in self.hidden_elts.items():
            elt.style.display = display
        self.hidden_elts.clear()
        self.slideshow_elt.remove()
        self.slideshow_elt = None
        self.swiper.destroy(True, True)
        self.swiper = None

    def fullscreen(self, active=None):
        """Activate/desactivate fullscreen

        @param acvite: can be:
            - True to activate
            - False to desactivate
            - Auto to switch fullscreen mode
        """
        try:
            fullscreen_elt = document.fullscreenElement
            request_fullscreen = self.slideshow_elt.requestFullscreen
        except AttributeError:
            print("fullscreen is not available on this browser")
        else:
            if active is None:
                active = fullscreen_elt == None
            if active:
                request_fullscreen()
            else:
                try:
                    document.exitFullscreen()
                except AttributeError:
                    print("exitFullscreen not available on this browser")

    def on_key_down(self, evt):
        if evt.key == 'Escape':
            self.quit()
        else:
            return
        evt.preventDefault()

    def on_slide_change(self, swiper):
        if self._exit_callback is not None:
            self._exit_callback()
            self._exit_callback = None
        item = self.current_item
        if item is not None:
            comments_count = item.get('comments_count')
            self.comments_count_elt.text = comments_count or ''

        for cls in self._class_to_remove:
            self.slideshow_elt.classList.remove(cls)

        self._class_to_remove.clear()

        options = self.current_options
        if options is not None:
            for flag in options.get('flags', []):
                cls = f"flag_{flag.lower()}"
                self.slideshow_elt.classList.add(cls)
                self._class_to_remove.add(cls)
            self._exit_callback = options.get("exit_callback", None)

    def toggle_hide_controls(self, evt):
        self.click_timer = None
        # we don't want to hide controls when a control is clicked
        # so we check all ancestors if we are not in a control
        current = evt.target
        while current and current != self.slideshow_elt:
            print(f"current: {current}")
            if 'slideshow_control' in current.classList:
                return
            current = current.parent
        for elt in self.slideshow_elt.select('.slideshow_control'):
            elt.style.display = '' if self.control_hidden else 'none'
        self.control_hidden = not self.control_hidden

    def on_click(self, evt):
        evt.stopPropagation()
        evt.preventDefault()
        # we use a timer so double tap can cancel the click
        # this avoid double tap side effect
        if self.click_timer is None:
            self.click_timer = timer.set_timeout(
                lambda: self.toggle_hide_controls(evt), 300)

    def on_dblclick(self, evt):
        evt.stopPropagation()
        evt.preventDefault()
        if self.click_timer is not None:
            timer.clear_timeout(self.click_timer)
            self.click_timer = None
        if self.swiper.zoom.scale != 1:
            self.swiper.zoom.toggle()
        else:
            # "in" is reserved in Python, so we call it using dict syntax
            self.swiper.zoom["in"]()

    def on_close(self, evt):
        evt.stopPropagation()
        evt.preventDefault()
        self.quit()

    def on_comment_close(self, evt):
        evt.stopPropagation()
        side_panel = self.comments_panel_elt.select_one('.comments_side_panel')
        side_panel.classList.remove('open')
        side_panel.bind("transitionend", lambda evt: self.comments_panel_elt.remove())

    def on_comments_panel_click(self, evt):
        # we stop stop propagation to avoid the closing of the panel
        evt.stopPropagation()

    def on_comment(self, evt):
        item = self.current_item
        if item is None:
            return
        comments_panel_tpl = Template('blog/comments_panel.html')
        try:
            comments = item['comments']['items']
        except KeyError:
            comments = []
        self.comments_panel_elt = comments_panel_tpl.get_elt({
            "comments": comments,
            "comments_service": item['comments_service'],
            "comments_node": item['comments_node'],

        })
        self.slideshow_elt <= self.comments_panel_elt
        side_panel = self.comments_panel_elt.select_one('.comments_side_panel')
        timer.set_timeout(lambda: side_panel.classList.add("open"), 0)
        for close_elt in self.comments_panel_elt.select('.click_to_close'):
            close_elt.bind("click", self.on_comment_close)
        side_panel.bind("click", self.on_comments_panel_click)

#!/usr/bin/env python3

"""This module implement an alternative media player

If browser can't play natively some libre video/audio formats, ogv.js will be used,
otherwise the native player will be used.

This player uses its own controls, this allow better tuning/event handling notably with
slideshow.
"""

from browser import document, timer, html


NO_PAGINATION = "NO_PAGINATION"
NO_SCROLLBAR = "NO_SCROLLBAR"


class MediaPlayer:
    TIMER_MODES = ("timer", "remaining")
    # will be set to False if browser can't play natively webm or ogv
    native = True
    # will be set to True when template and modules will be imported
    imports_done = False

    def __init__(
            self,
            sources,
            to_rpl_vid_elt=None,
            poster=None,
            reduce_click_area=False
    ):
        """
        @param sources: list of paths to media
            only the first one is used at the moment
        @param to_rpl_vid_elt: video element to replace
            if None, nothing is replaced and element must be inserted manually
        @param reduce_click_area: when True, only center of the element will react to
            click. Useful when used in slideshow, as click on border is used to
            show/hide slide controls
        """
        self.do_imports()

        self.reduce_click_area = reduce_click_area

        self.media_player_elt = media_player_elt = media_player_tpl.get_elt()
        self.player = player = self._create_player(sources, poster)
        if to_rpl_vid_elt is not None:
            to_rpl_vid_elt.parentNode.replaceChild(media_player_elt, to_rpl_vid_elt)
        overlay_play_elt = self.media_player_elt.select_one(".media_overlay_play")
        overlay_play_elt.bind("click", self.on_play_click)
        self.progress_elt = media_player_elt.select_one("progress")
        self.progress_elt.bind("click", self.on_progress_click)
        self.timer_elt = media_player_elt.select_one(".timer")
        self.timer_mode = "timer"

        self.controls_elt = media_player_elt.select_one(".media_controls")
        # we devnull 2 following events to avoid accidental side effect
        # this is notably useful in slideshow to avoid changing the slide when
        # the user misses slightly a button
        self.controls_elt.bind("mousedown", self._devnull)
        self.controls_elt.bind("click", self._devnull)

        player_wrapper_elt = media_player_elt.select_one(".media_elt")
        player.preload = "none"
        player.src = sources[0]
        player_wrapper_elt <= player
        self.hide_controls_timer = None

        # we capture mousedown to avoid side effect on slideshow
        player_wrapper_elt.addEventListener("mousedown", self._devnull)
        player_wrapper_elt.addEventListener("click", self.on_player_click)

        # buttons
        for handler in ("play", "change_timer_mode", "change_volume", "fullscreen"):
            for elt in media_player_elt.select(f".click_to_{handler}"):
                elt.bind("click", getattr(self, f"on_{handler}_click"))
        # events
        # FIXME: progress is not implemented in OGV.js, update when available
        for event in ("play", "pause", "timeupdate", "ended", "volumechange"):
            player.bind(event, getattr(self, f"on_{event}"))

    @property
    def elt(self):
        return self.media_player_elt

    def _create_player(self, sources, poster):
        """Create player element, using native one when possible"""
        player = None
        if not self.native:
            source = sources[0]
            ext = self.get_source_ext(source)
            if ext is None:
                print(
                    f"no extension found for {source}, using native player"
                )
            elif ext in self.cant_play_ext_list:
                print(f"OGV player user for {source}")
                player = self.ogv.OGVPlayer.new()
                # OGCPlayer has non standard "poster" property
                player.poster = poster
        if player is None:
            player = html.VIDEO(poster=poster)
        return player

    def reset(self):
        """Put back media player in intial state

        media will be stopped, time will be set to beginning, overlay will be put back
        """
        print("resetting media player")
        self.player.pause()
        self.player.currentTime = 0
        self.media_player_elt.classList.remove("in_use")

    def _devnull(self, evt):
        # stop an event
        evt.preventDefault()
        evt.stopPropagation()

    def on_player_click(self, evt):
        if self.reduce_click_area:
            bounding_rect = self.media_player_elt.getBoundingClientRect()
            margin_x = margin_y = 200
            if ((evt.clientX - bounding_rect.left < margin_x
                 or bounding_rect.right - evt.clientX < margin_x
                 or evt.clientY - bounding_rect.top < margin_y
                 or bounding_rect.bottom - evt.clientY < margin_y
               )):
                # click is not in the center, we don't handle it and let the event
                # propagate
                return
        self.on_play_click(evt)

    def on_play_click(self, evt):
        evt.preventDefault()
        evt.stopPropagation()
        self.media_player_elt.classList.add("in_use")
        if self.player.paused:
            print("playing")
            self.player.play()
        else:
            self.player.pause()
            print("paused")

    def on_change_timer_mode_click(self, evt):
        evt.preventDefault()
        evt.stopPropagation()
        self.timer_mode = self.TIMER_MODES[
            (self.TIMER_MODES.index(self.timer_mode) + 1) % len(self.TIMER_MODES)
        ]

    def on_change_volume_click(self, evt):
        evt.stopPropagation()
        self.player.muted = not self.player.muted

    def on_fullscreen_click(self, evt):
        evt.stopPropagation()
        try:
            fullscreen_elt = document.fullscreenElement
            request_fullscreen = self.media_player_elt.requestFullscreen
        except AttributeError:
            print("fullscreen is not available on this browser")
        else:
            if fullscreen_elt == None:
                print("requesting fullscreen")
                request_fullscreen()
            else:
                print(f"leaving fullscreen: {fullscreen_elt}")
                try:
                    document.exitFullscreen()
                except AttributeError:
                    print("exitFullscreen not available on this browser")

    def on_progress_click(self, evt):
        evt.stopPropagation()
        position = evt.offsetX / evt.target.width
        new_time = self.player.duration * position
        self.player.currentTime = new_time

    def on_play(self, evt):
        self.media_player_elt.classList.add("playing")
        self.show_controls()
        self.media_player_elt.bind("mousemove", self.on_mouse_move)

    def on_pause(self, evt):
        self.media_player_elt.classList.remove("playing")
        self.show_controls()
        self.media_player_elt.unbind("mousemove")

    def on_timeupdate(self, evt):
        self.update_progress()

    def on_ended(self, evt):
        self.update_progress()

    def on_volumechange(self, evt):
        evt.stopPropagation()
        if self.player.muted:
            self.media_player_elt.classList.add("muted")
        else:
            self.media_player_elt.classList.remove("muted")

    def on_mouse_move(self, evt):
        self.show_controls()

    def update_progress(self):
        duration = self.player.duration
        current_time = duration if self.player.ended else self.player.currentTime
        self.progress_elt.max = duration
        self.progress_elt.value = current_time
        self.progress_elt.text = f"{current_time/duration*100:.02f}"
        current_time, duration = int(current_time), int(duration)
        if self.timer_mode == "timer":
            cur_min, cur_sec = divmod(current_time, 60)
            tot_min, tot_sec = divmod(duration, 60)
            self.timer_elt.text = f"{cur_min}:{cur_sec:02d}/{tot_min}:{tot_sec:02d}"
        elif self.timer_mode == "remaining":
            rem_min, rem_sec = divmod(duration - current_time, 60)
            self.timer_elt.text = f"{rem_min}:{rem_sec:02d}"
        else:
            print(f"ERROR: unknown timer mode: {self.timer_mode}")

    def hide_controls(self):
        self.controls_elt.classList.add("hidden")
        self.media_player_elt.style.cursor = "none"
        if self.hide_controls_timer is not None:
            timer.clear_timeout(self.hide_controls_timer)
            self.hide_controls_timer = None

    def show_controls(self):
        self.controls_elt.classList.remove("hidden")
        self.media_player_elt.style.cursor = ""
        if self.hide_controls_timer is not None:
            timer.clear_timeout(self.hide_controls_timer)
        if self.player.paused:
            self.hide_controls_timer = None
        else:
            self.hide_controls_timer = timer.set_timeout(self.hide_controls, 3000)

    @classmethod
    def do_imports(cls):
        # we do imports (notably for ogv.js) only if they are necessary
        if cls.imports_done:
            return
        if not cls.native:
            from js_modules import ogv
            cls.ogv = ogv
            if not ogv.OGVCompat.supported('OGVPlayer'):
                print("Can't use OGVPlayer with this browser")
                raise NotImplementedError
        import template
        global media_player_tpl
        media_player_tpl = template.Template("components/media_player.html")
        cls.imports_done = True

    @staticmethod
    def get_source_ext(source):
        try:
            ext = f".{source.rsplit('.', 1)[1].strip()}"
        except IndexError:
            return None
        return ext or None

    @classmethod
    def install(cls, cant_play):
        cls.native = False
        ext_list = set()
        for data in cant_play.values():
            ext_list.update(data['ext'])
        cls.cant_play_ext_list = ext_list
        for to_rpl_vid_elt in document.body.select('video'):
            sources = []
            src = (to_rpl_vid_elt.src or '').strip()
            if src:
                sources.append(src)

            for source_elt in to_rpl_vid_elt.select('source'):
                src = (source_elt.src or '').strip()
                if src:
                    sources.append(src)

            # FIXME: we only use first found source
            try:
                source = sources[0]
            except IndexError:
                print(f"Can't find any source for following elt:\n{to_rpl_vid_elt.html}")
                continue

            ext = cls.get_source_ext(source)

            ext = f".{source.rsplit('.', 1)[1]}"
            if ext is None:
                print(
                    "No extension found for source of following elt:\n"
                    f"{to_rpl_vid_elt.html}"
                )
                continue
            if ext in ext_list:
                print(f"alternative player will be used for {source!r}")
                cls(sources, to_rpl_vid_elt)


def install_if_needed():
    CONTENT_TYPES = {
        "ogg_theora": {"type": 'video/ogg; codecs="theora"', "ext": [".ogv", ".ogg"]},
        "webm_vp8": {"type": 'video/webm; codecs="vp8, vorbis"', "ext": [".webm"]},
        "webm_vp9": {"type": 'video/webm; codecs="vp9"', "ext": [".webm"]},
        # FIXME: handle audio
        # "ogg_vorbis": {"type": 'audio/ogg; codecs="vorbis"', "ext": ".ogg"},
    }
    test_media_elt = html.VIDEO()
    cant_play = {k:d for k,d in CONTENT_TYPES.items()
                 if test_media_elt.canPlayType(d['type']) != "probably"}

    if cant_play:
        cant_play_list = '\n'.join(f"- {k} ({d['type']})" for k, d in cant_play.items())
        print(
            "This browser is incompatible with following content types, using "
            f"alternative:\n{cant_play_list}"
        )
        try:
            MediaPlayer.install(cant_play)
        except NotImplementedError:
            pass
    else:
        print("This browser can play natively all requested open video/audio formats")

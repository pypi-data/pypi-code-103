from tkinter import Canvas, PhotoImage
import tkinter as tk
from typing import overload
import cv2
from PIL import Image, ImageTk
import time

ITEM_TYPE_NONE = 0
# simple items
ITEM_TYPE_IMAGE = 1
ITEM_TYPE_STATUS = 2
ITEM_TYPE_ANIMATIONGIF = 3
ITEM_TYPE_VIDEO = 4
# complex items
ITEM_TYPE_ITEMSGROUP = 101

# region OOCanvas


class OOCanvas(Canvas):
    def __init__(self, master=None, image=None, command=None, **kw):
        super(OOCanvas, self).__init__(
            master=master, image=image, command=command, **kw)
        self.items_list = list()

    def create_ooImage(self, x=0, y=0):
        img = OOCanvasImage(self, int(x), int(y))
        self.items_list.append(img)
        return img

    def create_ooStatus(self, x=0, y=0):
        st = OOCanvasMultiStatus(self, int(x), int(y))
        self.items_list.append(st)
        return st

    def create_ooVideo(self, x=0, y=0, video_source=0):
        st = OOCanvasVideo(self, int(x), int(y), video_source)
        self.items_list.append(st)
        return st

    def create_ooItemsGroup(self):
        return OOCanvasItemsGroup(self)

# endregion

# region CanvasItem abstract classes


class OOCanvasItem:
    """Abstract class"""

    def __init__(self, canvas, x, y):
        self.canv = canvas
        self.objectType = ITEM_TYPE_NONE
        self.isVisible = True
        self.x = x
        self.y = y
        self.anchor = tk.CENTER

    def make_visible(self):
        self.isVisible = True

    def make_hidden(self):
        self.isVisible = False

    def set_location(self, x, y):
        self.x = x
        self.y = y

    def move(self, xmovement, ymovement):
        self.x += xmovement
        self.y += ymovement

    def set_anchor(self, anchor):
        self.anchor = anchor

    def raise_to_top(self):
        raise NotImplementedError("Please Implement this method")

    def dispose(self):
        raise NotImplementedError("Please Implement this method")

    # region events
    def add_left_mouse_button_down(self, callback):
        raise NotImplementedError("Please Implement this method")

    def add_left_mouse_button_up(self, callback):
        raise NotImplementedError("Please Implement this method")

    def add_mouse_double_click(self, callback):
        raise NotImplementedError("Please Implement this method")

    def add_right_mouse_button_down(self, callback):
        raise NotImplementedError("Please Implement this method")

    def add_right_mouse_button_up(self, callback):
        raise NotImplementedError("Please Implement this method")

    def remove_left_mouse_button_down(self, callback):
        raise NotImplementedError("Please Implement this method")

    def remove_left_mouse_button_up(self, callback):
        raise NotImplementedError("Please Implement this method")

    def remove_mouse_double_click(self, callback):
        raise NotImplementedError("Please Implement this method")

    def remove_right_mouse_button_down(self, callback):
        raise NotImplementedError("Please Implement this method")

    def remove_right_mouse_button_up(self, callback):
        raise NotImplementedError("Please Implement this method")
    # endregion


class OOCanvasSimpleItem(OOCanvasItem):
    """Abstract class"""

    def __init__(self, canvas, x, y):
        super(OOCanvasSimpleItem, self).__init__(canvas, x=x, y=y)
        self.id = None

    def make_visible(self):
        self.canv.itemconfigure(self.id, state=tk.NORMAL)
        OOCanvasItem.make_visible(self)
        return self

    def make_hidden(self):
        self.canv.itemconfigure(self.id, state=tk.HIDDEN)
        OOCanvasItem.make_hidden(self)
        return self

    def set_location(self, x, y):
        self.canv.coords(self.id, x, y)
        OOCanvasItem.set_location(self, x, y)
        return self

    def move(self, xmovement, ymovement):
        self.canv.move(self.id, xmovement, ymovement)
        OOCanvasItem.move(self, xmovement, ymovement)
        return self

    def set_anchor(self, anchor):
        self.canv.itemconfigure(self.id, anchor=anchor)
        OOCanvasItem.set_anchor(self, anchor)
        return self

    def raise_to_top(self):
        self.canv.tag_raise(self.id)
        return self

    def dispose(self):
        self.canv.delete(self.id)
        return self

    # region events
    def add_left_mouse_button_down(self, callback):
        """A method with an arguments (event)"""
        self.canv.tag_bind(self.id,
                           '<Button-1>', callback)
        return self

    def add_left_mouse_button_up(self, callback):
        """A method with an arguments (event)"""
        self.canv.tag_bind(self.id,
                           '<ButtonRelease-1>', callback)
        return self

    def add_mouse_double_click(self, callback):
        """A method with an arguments (event)"""
        self.canv.tag_bind(self.id,
                           '<Double-Button-1>', callback)
        return self

    def add_right_mouse_button_down(self, callback):
        """A method with an arguments (event)"""
        self.canv.tag_bind(self.id,
                           '<Button-3>', callback)
        return self

    def add_right_mouse_button_up(self, callback):
        """A method with an arguments (event)"""
        self.canv.tag_bind(self.id,
                           '<ButtonRelease-3>', callback)
        return self

    def remove_left_mouse_button_down(self, callback):
        """A method with an arguments (event)"""
        self.canv.tag_unbind(self.id,
                             '<Button-1>', callback)
        return self

    def remove_left_mouse_button_up(self, callback):
        """A method with an arguments (event)"""
        self.canv.tag_unbind(self.id,
                             '<ButtonRelease-1>', callback)
        return self

    def remove_mouse_double_click(self, callback):
        """A method with an arguments (event)"""
        self.canv.tag_unbind(self.id,
                             '<Double-Button-1>', callback)
        return self

    def remove_right_mouse_button_down(self, callback):
        """A method with an arguments (event)"""
        self.canv.tag_unbind(self.id,
                             '<Button-3>', callback)
        return self

    def remove_right_mouse_button_up(self, callback):
        """A method with an arguments (event)"""
        self.canv.tag_unbind(self.id,
                             '<ButtonRelease-3>', callback)
        return self
    # endregion


class OOCanvasComplexItem(OOCanvasItem):
    """Abstract class"""

    def __init__(self, canvas, x, y):
        super(OOCanvasComplexItem, self).__init__(canvas, x=x, y=y)
        self.__items = list()

    def _add_item(self, item):
        self.__items.append(item)
        return self

    def make_visible(self):
        for item in self.__items:
            item.make_visible()
        super.make_visible()
        return self

    def make_hidden(self):
        for item in self.__items:
            item.make_hidden()
        super.make_hidden()
        return self

    def set_location(self, x, y):
        for item in self.__items:
            item.set_location(x, y)
        super.set_location(x, y)
        return self

    def move(self, xmovement, ymovement):
        for item in self.__items:
            item.move(xmovement, ymovement)
        super.move(xmovement, ymovement)
        return self

    def set_anchor(self):
        raise NotImplementedError("Please Implement this method")

    def raise_to_top(self):
        for item in self.__items:
            item.raise_to_top()
        return self

    # region events
    def add_left_mouse_button_down(self, callback):
        """A method with an arguments (event)"""
        for item in self.__items:
            item.add_left_mouse_button_down(callback)
        return self

    def add_left_mouse_button_up(self, callback):
        """A method with an arguments (event)"""
        for item in self.__items:
            item.add_left_mouse_button_up(callback)
        return self

    def add_mouse_double_click(self, callback):
        """A method with an arguments (event)"""
        for item in self.__items:
            item.add_mouse_double_click(callback)
        return self

    def add_right_mouse_button_down(self, callback):
        """A method with an arguments (event)"""
        for item in self.__items:
            item.add_right_mouse_button_down(callback)
        return self

    def add_right_mouse_button_up(self, callback):
        """A method with an arguments (event)"""
        for item in self.__items:
            item.add_right_mouse_button_up(callback)
        return self

    def remove_left_mouse_button_down(self, callback):
        """A method with an arguments (event)"""
        for item in self.__items:
            item.remove_left_mouse_button_down(callback)
        return self

    def remove_left_mouse_button_up(self, callback):
        """A method with an arguments (event)"""
        for item in self.__items:
            item.remove_left_mouse_button_up(callback)
        return self

    def remove_mouse_double_click(self, callback):
        """A method with an arguments (event)"""
        for item in self.__items:
            item.remove_mouse_double_click(callback)
        return self

    def remove_right_mouse_button_down(self, callback):
        """A method with an arguments (event)"""
        for item in self.__items:
            item.remove_right_mouse_button_down(callback)
        return self

    def remove_right_mouse_button_up(self, callback):
        """A method with an arguments (event)"""
        for item in self.__items:
            item.remove_right_mouse_button_up(callback)
        return self
    # endregion
# endregion

# region complex items


class OOCanvasItemsGroup(OOCanvasComplexItem):
    """Group of canvas items to manage group situations"""

    def __init__(self, canvas):
        super(OOCanvasItemsGroup, self).__init__(canvas, x=0, y=0)
        self.objectType = ITEM_TYPE_ITEMSGROUP

    def add_item(self, item):
        self._add_item(item)
        return self

# endregion

# region simple items


class OOCanvasImage(OOCanvasSimpleItem):
    """OOImage for OOCanvas"""

    def __init__(self, canvas, x, y, imageId=None):
        super(OOCanvasImage, self).__init__(canvas, x=x, y=y)
        self.objectType = ITEM_TYPE_IMAGE
        self.__image = None
        if imageId == None:
            self.id = self.canv.create_image(x, y)
        else:
            self.id = imageId
            self.set_location(x, y)

    def set_image(self, image):
        self.canv.itemconfig(self.id, image=image)
        self.__image = image
        return self

    def refresh(self):
        self.canv.itemconfig(self.id, image=self.__image)
        return self


class OOCanvasMultiStatus(OOCanvasSimpleItem):
    """OOStatus for OOCanvas"""

    def __init__(self, canvas, x, y):
        super(OOCanvasMultiStatus, self).__init__(canvas, x=x, y=y)
        self.objectType = ITEM_TYPE_STATUS
        self.id = self.canv.create_image(x, y)
        self.__statuses = dict()
        self.__selected_statusKey = None
        self.__selected_status = None

    def add_status_image(self, statusKey, image):
        item = OOCanvasImage(self.canv, self.x, self.y, self.id)\
            .set_image(image)
        self.__statuses[statusKey] = item
        return self

    def add_status_gif(self, statusKey, image, gifFramesArray, nextFrameAfter_ms=100):
        item = OOCanvasAnimationGif(self.canv, self.x, self.y, self.id)\
            .set_image(image, gifFramesArray, nextFrameAfter_ms)
        self.__statuses[statusKey] = item
        return self

    def add_status_gif_file(self, statusKey, imageAddress, nextFrameAfter_ms=100):
        item = OOCanvasAnimationGif(self.canv, self.x, self.y, self.id)\
            .set_image(imageAddress, nextFrameAfter_ms)
        self.__statuses[statusKey] = item
        return self

    def add_status_video(self, statusKey, videoSource):
        item = OOCanvasVideo(self.canv, self.x, self.y, self.id)\
            .set_video_source(videoSource)
        self.__statuses[statusKey] = item
        return self

    def select_status(self, statusKey):
        if type(self.__selected_status) is OOCanvasAnimationGif or self.__selected_status is OOCanvasVideo:
            self.__selected_status.stop()
        self.__selected_statusKey = statusKey
        st = self.__statuses.get(statusKey)
        if st == None:
            self.canv.itemconfig(self.id, image=None)
        else:
            if type(st) is OOCanvasImage:
                st.refresh()
            elif type(st) is OOCanvasAnimationGif:
                st.refresh()
                st.start()
            elif type(st) is OOCanvasVideo:
                st.start()
            self.__selected_status = st
        self.set_location(self.x, self.y)
        return self

    def get_selected_statusKey(self):
        return self.__selected_statusKey


class OOCanvasAnimationGif(OOCanvasSimpleItem):
    """OOAnimationGif for OOCanvas"""

    def __init__(self, canvas, x, y, imageId=None):
        super(OOCanvasAnimationGif, self).__init__(canvas, x=x, y=y)
        self.objectType = ITEM_TYPE_ANIMATIONGIF
        if imageId == None:
            self.id = self.canv.create_image(x, y)
        else:
            self.id = imageId
            self.set_location(x, y)

        self.__first_image = None
        self.__loop_active = False
        self.__loop = None
        self.__frames = None
        self.__frames_len = 0
        self.__current_frame_index = 0
        self.__nextFrameAfter_ms = 1

    def set_image(self, image, framesArray, nextFrameAfter_ms=100):
        self.canv.itemconfig(self.id, image=image)
        self.__first_image = image
        self.__frames = framesArray
        self.__frames_len = len(framesArray)
        self.__nextFrameAfter_ms = nextFrameAfter_ms
        return self

    def set_image_address(self, imageAddress, nextFrameAfter_ms=100):
        self.__first_image = PhotoImage(imageAddress)
        self.canv.itemconfig(self.id, image=self.__first_image)
        self.__frames_len = self.__find_frames_count(Image.open(imageAddress))
        self.__frames = [PhotoImage(
            file=imageAddress, format='gif -index %i' % (i)) for i in range(self.__frames_len)]
        self.__nextFrameAfter_ms = nextFrameAfter_ms
        return self

    def refresh(self):
        self.canv.itemconfig(self.id, image=self.__first_image)
        return self

    def start(self):
        if not self.__loop_active:
            self.__loop_active = True
            self.__loop = self.canv.master.after(
                self.__nextFrameAfter_ms, self.__frame_manager)
        return self

    def start_from_beginning(self):
        self.__current_frame_index = 0
        self.start()
        return self

    def stop(self):
        if self.__loop_active:
            self.__loop_active = False
            self.canv.master.after_cancel(self.__loop)
        return self

    def __frame_manager(self):
        self.canv.itemconfig(
            self.id, image=self.__frames[self.__current_frame_index])
        if self.__current_frame_index >= self.__frames_len-1:
            self.__current_frame_index = 0
        else:
            self.__current_frame_index += 1
        self.__loop = self.canv.master.after(
            self.__nextFrameAfter_ms, self.__frame_manager)

    def __find_frames_count(gif_obj):
        gif_obj.seek(0)  # move to the start of the gif, frame 0
        count = 0
        # run a while loop to loop through the frames
        while True:
            try:
                count += 1
                # now move to the next frame of the gif
                # image.tell() => current frame
                gif_obj.seek(gif_obj.tell() + 1)
            except EOFError:
                return count


class OOCanvasVideo(OOCanvasSimpleItem):
    """OOVideo for OOCanvas"""

    def __init__(self, canvas, x, y, imageId=None):
        super(OOCanvasVideo, self).__init__(canvas, x=x, y=y)
        self.objectType = ITEM_TYPE_VIDEO
        if imageId == None:
            self.id = self.canv.create_image(x, y)
        else:
            self.id = imageId
            self.set_location(x, y)

        self.__delay = 40
        self.__speed = 1
        self.__repeat = False
        self.__loop_active = False
        self.__loop = None

    def set_video_source(self, video_source=0):
        # open video source (by default 0 will try to open the computer webcam)
        self.__video = _VideoCapture(video_source)
        self.__delay = 1000 / self.__video.get_frame_rate()
        return self

    def set_speed(self, speed):
        """a float bigger than zero - one for no change in speed"""
        if float(speed) > 0:
            self.__speed = float(speed)
        return self

    def refresh(self):
        self.start()
        return self

    def start(self):
        if not self.__loop_active:
            self.__loop_active = True
            self.__loop = self.canv.master.after(
                self.__nextFrameAfter_ms, self.__update)
        return self

    def start_from_beginning(self):
        self.stop()
        self.__video.reset()
        self.start()
        return self

    def stop(self):
        if self.__loop_active:
            self.__loop_active = False
            self.canv.master.after_cancel(self.__loop)
        return self

    def forward(self, framesCount=1):
        self.__video.forward(framesCount)
        return self

    def backward(self, framesCount=1):
        self.__video.backward(framesCount)
        return self

    def repeat_video(self, repeat=True):
        self.__repeat = bool(repeat)
        return self

    def save_snapshot(self):
        # Get a frame from the video source
        ret, frame = self.__video.get_frame()

        if ret:
            cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") +
                        ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        return self

    def __update(self):
        # Get a frame from the video source
        ret, frame = self.__video.get_frame()

        if ret:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canv.itemconfig(self.id, image=self.photo)

        if self.__video.end_of_video and self.__repeat:
            self.__video.reset()
        if not self.__video.end_of_video:
            self.__loop = self.canv.master.after(
                self.__delay*self.__speed, self.__update)
# endregion

# region private helper classes


class _VideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        self.__current_frame_index = 0
        self.__frames_count = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)
        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.end_of_video = False

    def reset(self):
        self.__current_frame_index = 0
        self.end_of_video = False

    def forward(self, frameCount):
        self.__current_frame_index += int(frameCount)
        if self.__current_frame_index >= self.__frames_count:
            self.__current_frame_index = self.__frames_count
            self.end_of_video = True

    def backward(self, frameCount):
        self.__current_frame_index -= int(frameCount)
        if self.__current_frame_index < 0:
            self.__current_frame_index = 0
            self.end_of_video = False

    def get_frame(self):
        if self.vid.isOpened():
            # set next frame index
            self.vid.set(cv2.CV_CAP_PROP_POS_FRAMES,
                         self.__current_frame_index)
            ret, frame = self.vid.read()
            self.__current_frame_index += 1
            if self.__current_frame_index >= self.__frames_count:
                self.end_of_video = True
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (False, None)

    def get_frame_rate(self):
        """frames per second"""
        return self.vid.get(cv2.CAP_PROP_FPS)

     # Release the video source when the object is destroyed
    def dispose(self):
        if self.vid.isOpened():
            self.vid.release()


class CanvasEventHandler(object):
    def __init__(self):
        self.__registeredMethods = []

    def __iadd__(self, Ehandler):
        self.__registeredMethods.append(Ehandler)
        return self

    def __isub__(self, Ehandler):
        self.__registeredMethods.remove(Ehandler)
        return self

    def __call__(self, *args, **keywargs):
        for method in self.__registeredMethods:
            method(*args, **keywargs)
# endregion


# region potential
    # def addtag_above(self, newtag):
    #     """Add tag NEWTAG to all items above TAGORID."""
    #     self.canvas.addtag_above(newtag, self.canvasItemId)

    # def addtag_all(self, newtag):
    #     """Add tag NEWTAG to all items."""
    #     self.canvas.addtag_all(newtag, self.canvasItemId)

    # def addtag_below(self, newtag):
    #     """Add tag NEWTAG to all items below TAGORID."""
    #     self.canvas.addtag_below(newtag, self.canvasItemId)

    # def addtag_closest(self, newtag, x, y, halo=None, start=None):
    #     """Add tag NEWTAG to item which is closest to pixel at X, Y.
    #     If several match take the top-most.
    #     All items closer than HALO are considered overlapping (all are
    #     closests). If START is specified the next below this tag is taken."""
    #     self.canvas.addtag_closest(self, newtag, x, y, halo=halo, start=start)

    # def addtag_enclosed(self, newtag, x1, y1, x2, y2):
    #     """Add tag NEWTAG to all items in the rectangle defined
    #     by X1,Y1,X2,Y2."""
    #     self.addtag(newtag, 'enclosed', x1, y1, x2, y2)

    # def addtag_overlapping(self, newtag, x1, y1, x2, y2):
    #     """Add tag NEWTAG to all items which overlap the rectangle
    #     defined by X1,Y1,X2,Y2."""
    #     self.addtag(newtag, 'overlapping', x1, y1, x2, y2)

    # def addtag_withtag(self, newtag, tagOrId):
    #     """Add tag NEWTAG to all items with TAGORID."""
    #     self.addtag(newtag, 'withtag', tagOrId)

    # def bbox(self, *args):
    #     """Return a tuple of X1,Y1,X2,Y2 coordinates for a rectangle
    #     which encloses all items with tags specified as arguments."""
    #     return self._getints(
    #         self.tk.call((self._w, 'bbox') + args)) or None

    # def tag_unbind(self, tagOrId, sequence, funcid=None):
    #     """Unbind for all items with TAGORID for event SEQUENCE  the
    #     function identified with FUNCID."""
    #     self.tk.call(self._w, 'bind', tagOrId, sequence, '')
    #     if funcid:
    #         self.deletecommand(funcid)

    # def tag_bind(self, tagOrId, sequence=None, func=None, add=None):
    #     """Bind to all items with TAGORID at event SEQUENCE a call to function FUNC.

    #     An additional boolean parameter ADD specifies whether FUNC will be
    #     called additionally to the other bound function or whether it will
    #     replace the previous function. See bind for the return value."""
    #     return self._bind((self._w, 'bind', tagOrId),
    #                       sequence, func, add)

    # def canvasx(self, screenx, gridspacing=None):
    #     """Return the canvas x coordinate of pixel position SCREENX rounded
    #     to nearest multiple of GRIDSPACING units."""
    #     return self.tk.getdouble(self.tk.call(
    #         self._w, 'canvasx', screenx, gridspacing))

    # def canvasy(self, screeny, gridspacing=None):
    #     """Return the canvas y coordinate of pixel position SCREENY rounded
    #     to nearest multiple of GRIDSPACING units."""
    #     return self.tk.getdouble(self.tk.call(
    #         self._w, 'canvasy', screeny, gridspacing))

    # def coords(self, *args):
    #     """Return a list of coordinates for the item given in ARGS."""
    #     # XXX Should use _flatten on args
    #     return [self.tk.getdouble(x) for x in
    #             self.tk.splitlist(
    #         self.tk.call((self._w, 'coords') + args))]

    # def dchars(self, *args):
    #     """Delete characters of text items identified by tag or id in ARGS (possibly
    #     several times) from FIRST to LAST character (including)."""
    #     self.tk.call((self._w, 'dchars') + args)

    # def delete(self, *args):
    #     """Delete items identified by all tag or ids contained in ARGS."""
    #     self.tk.call((self._w, 'delete') + args)

    # def dtag(self, *args):
    #     """Delete tag or id given as last arguments in ARGS from items
    #     identified by first argument in ARGS."""
    #     self.tk.call((self._w, 'dtag') + args)

    # def find(self, *args):
    #     """Internal function."""
    #     return self._getints(
    #         self.tk.call((self._w, 'find') + args)) or ()

    # def find_above(self, tagOrId):
    #     """Return items above TAGORID."""
    #     return self.find('above', tagOrId)

    # def find_all(self):
    #     """Return all items."""
    #     return self.find('all')

    # def find_below(self, tagOrId):
    #     """Return all items below TAGORID."""
    #     return self.find('below', tagOrId)

    # def find_closest(self, x, y, halo=None, start=None):
    #     """Return item which is closest to pixel at X, Y.
    #     If several match take the top-most.
    #     All items closer than HALO are considered overlapping (all are
    #     closest). If START is specified the next below this tag is taken."""
    #     return self.find('closest', x, y, halo, start)

    # def find_enclosed(self, x1, y1, x2, y2):
    #     """Return all items in rectangle defined
    #     by X1,Y1,X2,Y2."""
    #     return self.find('enclosed', x1, y1, x2, y2)

    # def find_overlapping(self, x1, y1, x2, y2):
    #     """Return all items which overlap the rectangle
    #     defined by X1,Y1,X2,Y2."""
    #     return self.find('overlapping', x1, y1, x2, y2)

    # def find_withtag(self, tagOrId):
    #     """Return all items with TAGORID."""
    #     return self.find('withtag', tagOrId)

    # def focus(self, *args):
    #     """Set focus to the first item specified in ARGS."""
    #     return self.tk.call((self._w, 'focus') + args)

    # def gettags(self, *args):
    #     """Return tags associated with the first item specified in ARGS."""
    #     return self.tk.splitlist(
    #         self.tk.call((self._w, 'gettags') + args))

    # def icursor(self, *args):
    #     """Set cursor at position POS in the item identified by TAGORID.
    #     In ARGS TAGORID must be first."""
    #     self.tk.call((self._w, 'icursor') + args)

    # def index(self, *args):
    #     """Return position of cursor as integer in item specified in ARGS."""
    #     return self.tk.getint(self.tk.call((self._w, 'index') + args))

    # def insert(self, *args):
    #     """Insert TEXT in item TAGORID at position POS. ARGS must
    #     be TAGORID POS TEXT."""
    #     self.tk.call((self._w, 'insert') + args)

    # def itemcget(self, tagOrId, option):
    #     """Return the resource value for an OPTION for item TAGORID."""
    #     return self.tk.call(
    #         (self._w, 'itemcget') + (tagOrId, '-'+option))

    # def itemconfigure(self, tagOrId, cnf=None, **kw):
    #     """Configure resources of an item TAGORID.

    #     The values for resources are specified as keyword
    #     arguments. To get an overview about
    #     the allowed keyword arguments call the method without arguments.
    #     """
    #     return self._configure(('itemconfigure', tagOrId), cnf, kw)

    # itemconfig = itemconfigure

    # # lower, tkraise/lift hide Misc.lower, Misc.tkraise/lift,
    # # so the preferred name for them is tag_lower, tag_raise
    # # (similar to tag_bind, and similar to the Text widget);
    # # unfortunately can't delete the old ones yet (maybe in 1.6)
    # def tag_lower(self, *args):
    #     """Lower an item TAGORID given in ARGS
    #     (optional below another item)."""
    #     self.tk.call((self._w, 'lower') + args)

    # lower = tag_lower

    # def postscript(self, cnf={}, **kw):
    #     """Print the contents of the canvas to a postscript
    #     file. Valid options: colormap, colormode, file, fontmap,
    #     height, pageanchor, pageheight, pagewidth, pagex, pagey,
    #     rotate, width, x, y."""
    #     return self.tk.call((self._w, 'postscript') +
    #                         self._options(cnf, kw))

    # def tag_raise(self, *args):
    #     """Raise an item TAGORID given in ARGS
    #     (optional above another item)."""
    #     self.tk.call((self._w, 'raise') + args)

    # lift = tkraise = tag_raise

    # def scale(self, *args):
    #     """Scale item TAGORID with XORIGIN, YORIGIN, XSCALE, YSCALE."""
    #     self.tk.call((self._w, 'scale') + args)

    # def scan_mark(self, x, y):
    #     """Remember the current X, Y coordinates."""
    #     self.tk.call(self._w, 'scan', 'mark', x, y)

    # def scan_dragto(self, x, y, gain=10):
    #     """Adjust the view of the canvas to GAIN times the
    #     difference between X and Y and the coordinates given in
    #     scan_mark."""
    #     self.tk.call(self._w, 'scan', 'dragto', x, y, gain)

    # def select_adjust(self, tagOrId, index):
    #     """Adjust the end of the selection near the cursor of an item TAGORID to index."""
    #     self.tk.call(self._w, 'select', 'adjust', tagOrId, index)

    # def select_clear(self):
    #     """Clear the selection if it is in this widget."""
    #     self.tk.call(self._w, 'select', 'clear')

    # def select_from(self, tagOrId, index):
    #     """Set the fixed end of a selection in item TAGORID to INDEX."""
    #     self.tk.call(self._w, 'select', 'from', tagOrId, index)

    # def select_item(self):
    #     """Return the item which has the selection."""
    #     return self.tk.call(self._w, 'select', 'item') or None

    # def select_to(self, tagOrId, index):
    #     """Set the variable end of a selection in item TAGORID to INDEX."""
    #     self.tk.call(self._w, 'select', 'to', tagOrId, index)

    # def type(self, tagOrId):
    #     """Return the type of the item TAGORID."""
    #     return self.tk.call(self._w, 'type', tagOrId) or None
# endregion

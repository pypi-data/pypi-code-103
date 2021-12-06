"""A widget for setting values by rotating a knob.

**Imperative:**

    >>> import tkinter as tk
    >>> import tkinter.ttk as ttk
    >>> import witkets as wtk
    >>> def test():
    ...     label['text'] = gauge['number']
    ...     root.after(50, test)
    ...
    >>> root = tk.Tk()
    >>> label = ttk.Label(root)
    >>> label.pack()
    >>> gauge = wtk.Gauge(root)
    >>> gauge['width'] = gauge['height'] = 200
    >>> gauge.pack(expand=1, fill=tk.BOTH)
    >>> gauge.enable_mouse()
    >>> root.after(50, test)
    'after#0'
    >>> root.mainloop()

**Declarative:**

.. code-block:: xml

    <root>
        <gauge wid='gauge1' minvalue='0' maxvalue='100' tickcount='8'
               width='96' height='96' startang='30' endang='330'
               knobcolor='red' />
        <geometry>
            <pack for='gauge1' />
        </geometry>
    </root>

"""

import tkinter as tk
from math import sqrt, sin, cos, pi, atan2


class Gauge(tk.Canvas):
    """A widget for setting values by rotating a knob.
    
       This widget is an alternative way of inputting numbers in a range.

    Parameters:
        master (object): Parent widget

    **Events:**
        * <<FilePathChanged>> : fired whenever the user changes the filepath

    The following options can be used in several ways:
     - upon construction (e.g.: :code:`widget = Widget(parent, option=value)`)
     - by *tkinter* standard :code:`config()` method 
       (e.g. :code:`widget.config(option=value)`) or
     - in a dict-like access (e.g.: widget['option'] = value)
    
    Keyword Arguments:
        number (number): The current value
        numvariable (object): Numeric variable to store the current value
        maxvalue (number): Maximum value (proportional to maximum angle)
        minvalue (number): Minimum value (proportional to minimum angle)
        tickcount (int): Number of ticks along the scale
        startang (float): Starting angle
        endang (float): Ending angle (must be greater than *startang*)
        knobrelradius (float): Knob radius relative to the total radius [0..1]
        knobcolor (color): Knob color (inner radius)
        scalecolor (color): Scale color (outer radius)
        tickcolor (color): Ticks color
        cursorcolor (color): Cursor color
        cursorwidth (int): Cursor line width
        kw (dict): Other keywords arguments (:class:`Canvas` widget options)

    """

    def __init__(self, master=None, number=0, numvariable=None,
                 maxvalue=100, minvalue=0, tickcount=20, startang=-60,
                 endang=240, knobrelradius=0.75, knobcolor='#CCCCCC',
                 scalecolor='#EEEEEE', tickcolor='#333333',
                 cursorcolor='#333333', cursorwidth=2, **kw):

        # Canvas init
        if 'width' in kw:
            kw['height'] = kw['width']
        elif 'height' in kw:
            kw['width'] = kw['height']
        else:
            kw['width'] = kw['height'] = 120
        if 'background' not in kw:
            kw['background'] = '#FFF'
        tk.Canvas.__init__(self, master, **kw)

        # Widget-specific Properties
        if not numvariable:
            self._var = tk.DoubleVar()
        else:
            self._var = numvariable
        self._minvalue = minvalue
        self._maxvalue = maxvalue
        self._tickcount = tickcount
        self._knobrelradius = knobrelradius
        self._knobcolor = knobcolor
        self._scalecolor = scalecolor
        self._tickcolor = tickcolor
        self._cursorcolor = cursorcolor
        self._cursorwidth = cursorwidth
        self._startang = startang
        self._endang = endang
        self._var.set(number)
        self._var.trace_add('write', self._redraw)

        # Mouse related
        self._motion = False

        # First draw
        self._reconfigure()

    # =====================================================================            
    # Introspection
    # =====================================================================
    
    widget_keys = {
        'number': float,
        'numvariable': tk.DoubleVar, 
        'maxvalue': float, 
        'minvalue': float,
        'tickcount': int,
        'startang': float, 
        'endang': float, 
        'knobrelradius': float, 
        'knobcolor': str,
        'scalecolor': str,
        'tickcolor': str,
        'cursorcolor': str,
        'cursorwidth': int
    }

    # =====================================================================
    # Helper methods
    # =====================================================================

    def _reconfigure(self):
        """Reconfigures internal state and redraws everything"""
        self._height = int(self['height'])
        self._width = int(self['width'])
        self._xc, self._yc = self._width >> 1, self._height >> 1
        self.delete(tk.ALL)
        self._draw_structure()
        self._draw_knob()

    @staticmethod
    def _radius_at(radians, a, b):
        """Evaluates the radius for a given angle"""
        return a * b / sqrt((a * cos(radians)) ** 2 + (b * sin(radians)) ** 2)

    def _get_limit_radians(self):
        """Corrects the angle interval.

            This function adds 360 degrees to the angle limits until 
            both are positive.

            The lower and upper limits are returned in radians.
        """
        angle1 = self._startang
        angle2 = self._endang
        while angle1 < 0:
            angle1 += 360
            angle2 += 360
        return angle1 * pi / 180, angle2 * pi / 180

    # =====================================================================
    # Drawing Functions
    # =====================================================================

    def _draw_structure(self):

        # Scale
        c = (1, 1, self._width - 1, self._height - 1)
        self.create_oval(fill=self._scalecolor, *c)

        # Center coords
        xc, yc = self._xc, self._yc  # shortcut

        # Ticks
        angle, last_angle = self._get_limit_radians()
        step = (last_angle - angle) / (self._tickcount - 1)
        tick = 0
        while tick < self._tickcount:
            radius = self._radius_at(angle, a=xc, b=yc)
            x, y = int(radius * cos(angle)), int(radius * sin(angle))
            self.create_line(xc, yc, xc + x, yc - y, fill=self._tickcolor)
            angle += step
            tick += 1

    def _draw_knob(self):
        xc, yc = self._xc, self._yc

        # Knob
        topleft = 1 - self._knobrelradius  # default: 0.25
        bottomright = 1 + self._knobrelradius  # default: 1.75
        # xc and yc are also a and b (major and minor radius)
        c = (xc * topleft, yc * topleft, xc * bottomright, yc * bottomright)
        self._knob = self.create_oval(fill=self._knobcolor, *c)

        # Cursor
        num = self._var.get()
        percent = (num - self._minvalue) / (self._maxvalue - self._minvalue)
        percent = 1 - percent  # number raises counterclockwise direction

        start_angle, last_angle = self._get_limit_radians()
        angle = start_angle + percent * (last_angle - start_angle)
        radius = self._radius_at(angle,
                                 a=xc * self._knobrelradius,
                                 b=yc * self._knobrelradius
                                 )
        x, y = int(radius * cos(angle)), int(radius * sin(angle))
        self._cursor = self.create_line(xc, yc, xc + x, yc - y,
                                        fill=self._cursorcolor, width=self._cursorwidth)

    def _redraw(self, *args):
        self.delete(self._knob)
        self.delete(self._cursor)
        self._draw_knob()

    # =====================================================================
    # Mouse Events
    # =====================================================================

    def enable_mouse(self):
        """Enable mouse events"""
        self.bind('<ButtonPress>', self._on_clicked)
        self.bind('<Motion>', self._on_motion)
        self.bind('<ButtonRelease>', self._on_release)

    def disable_mouse(self):
        """Disables mouse events"""
        self.unbind('<ButtonPress>')
        self.unbind('<Motion>')
        self.unbind('<ButtonRelease>')

    def _mouse_update_value(self, event):
        """Mouse clicked callback"""
        xc, yc = self._xc, self._yc
        xrel = event.x_root - event.widget.winfo_rootx()
        yrel = event.y_root - event.widget.winfo_rooty()
        # Getting angle
        angle = - (atan2(yrel - yc, xrel - xc))
        # Normalizing interval
        min_angle, max_angle = self._get_limit_radians()
        while angle < min_angle:
            angle += 2 * pi
        if angle > max_angle:
            return  # invalid region
        # Getting corresponding Var value
        percent = (angle - min_angle) / (max_angle - min_angle)
        percent = 1 - percent  # counterclockwise
        amplitude = self._maxvalue - self._minvalue
        self._var.set(self._minvalue + percent * amplitude)

    def _on_clicked(self, event):
        """Mouse clicked callback"""
        self._mouse_update_value(event)
        self._motion = True

    def _on_release(self, event):
        """Mouse button release callback"""
        self._motion = False

    def _on_motion(self, event):
        """Mouse motion callback"""
        if not self._motion:
            return
        self._mouse_update_value(event)

    # =====================================================================
    # Inherited Methods
    # =====================================================================

    def __setitem__(self, key, val):
        if key in Gauge.widget_keys:
            if key == 'number':
                self._var.set(val)
            elif key == 'numvariable':
                self._var = val
                self._var.trace_add('write', self._redraw)
            else:
                self.__setattr__('_' + key, val)
        else:
            tk.Canvas.__setitem__(self, key, val)
        self._reconfigure()

    def __getitem__(self, key):
        if key in Gauge.widget_keys:
            if key == 'number':
                return self._var.get()
            elif key == 'numvariable':
                return self._var
            else:
                return self.__getattribute__('_' + key)
        else:
            return tk.Canvas.__getitem__(self, key)

    def config(self, **kw):
        """Standard Tk config method"""
        if 'number' in kw:
            self._var.set(kw['number'])
        if 'numvariable' in kw:
            self._var = kw['variable']
            self._var.trace_add('write', self._redraw)
        for key in Gauge.widget_keys:
            if key in kw:
                self[key] = kw[key]
                kw.pop(key, False)
        tk.Canvas.config(self, **kw)
        self._reconfigure()

# =====================================================================
# Module DocTest
# =====================================================================

if __name__ == '__main__':
    import doctest
    doctest.testmod()

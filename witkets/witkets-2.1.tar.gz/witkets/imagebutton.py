"""A convenience widget for setting a button with an image.

**Imperative:**

      >>> import tkinter as tk
      >>> import tkinter.ttk as ttk
      >>> import witkets as wtk
      >>> root = tk.Tk()
      >>> btn = ImageButton(root, imgfile='myicon.gif', compound='top')
      >>> btn['text'] = 'Click me!'
      >>> root.mainloop()

**Declarative:**

.. code-block:: xml

    <root>
        <imagebutton wid='imgbutton1' imgfile='test.png' text='Test' />
        <geometry>
            <pack for='imgbutton1' />
        </geometry>
    </root>

"""


import tkinter as tk
import tkinter.ttk as ttk

class ImageButton(ttk.Button):
    """A button with an image.

    Parameters:
        master (object): Parent widget

    The following option can be used in several ways:
     - upon construction (e.g.: :code:`widget = Widget(parent, option=value)`)
     - by *tkinter* standard :code:`config()` method 
       (e.g. :code:`widget.config(option=value)`) or
     - in a dict-like access (e.g.: widget['option'] = value)
    
    Keyword Arguments:
        imgfile (str): Path to the button icon.
        kw (dict): Other keywords arguments (:class:`ttk.Button` widget options)

"""

    def __init__(self, master, imgfile=None, **kw):
        if 'compound' not in kw:
            kw['compound'] = 'top'
        self._imgfile = imgfile
        self._image = None
        if imgfile:
            self._image = tk.PhotoImage(file=imgfile)
            kw['image'] = self._image
        ttk.Button.__init__(self, master, **kw)

    # =====================================================================
    # Inherited Methods
    # =====================================================================

    def __setitem__(self, key, val):
        if key == 'imgfile':
            self._imgfile = val
            self._image = tk.PhotoImage(file=val)
            ttk.Button.__setitem__(self, 'image', self._image)
        else:
            ttk.Button.__setitem__(self, key, val)

    def __getitem__(self, key):
        if key == 'imgfile':
            return self._imgfile
        return ttk.Button.__getitem__(self, key)

    def config(self, **kw):
        """Standard Tk config method"""
        if 'imgfile' in kw:
            self.__setitem__('imgfile', kw['imgfile'])
            kw.pop('imgfile', False)
        ttk.Button.config(self, **kw)

# =====================================================================
# Module DocTest
# =====================================================================

if __name__ == '__main__':
    import doctest
    doctest.testmod()
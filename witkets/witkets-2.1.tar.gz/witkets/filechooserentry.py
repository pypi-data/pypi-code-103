"""File chooser for open, "save as" and "folder select" operations.

**Imperative:**

    >>> import tkinter as tk
    >>> import tkinter.ttk as ttk
    >>> import witkets as wtk
    >>> root = tk.Tk()
    >>> ttk.Label(root, text='Open, save as and select folder: ').pack()
    >>> chooser = wtk.FileChooserEntry(root)
    >>> chooser['filetypes'] = [('Bitmap', '*.bmp'), ('PDF', '*.pdf')]
    >>> chooser2 = wtk.FileChooserEntry(root, buttontext='Escolher')
    >>> chooser2['action'] = wtk.FileChooserAction.SAVE
    >>> chooser2['dialogtitle'] = 'Salvar como...'
    >>> chooser3 = wtk.FileChooserEntry(root, 
    ...     action=wtk.FileChooserAction.SELECT_FOLDER)
    >>> chooser3.config(buttontext='Choisir...', 
    ...     dialogtitle='Je veux un dossier')
    >>> chooser4 = wtk.FileChooserEntry(root, 
    ...     action=FileChooserAction.OPEN_MULTIPLE)
    >>> chooser4['buttontext'] = 'Open Multiple...'
    >>> chooser.pack(fill='both')
    >>> chooser2.pack(fill='both')
    >>> chooser3.pack(fill='both')
    >>> chooser4.pack(fill='both')
    >>> root.mainloop()

**Declarative:**

.. code-block:: xml

    <root>
        <filechooserentry wid='filechooser1' buttontext="Choisir"
                          dialogtitle="Nom du nouveau fichier..."
                          action="save">
            <filetypes>
                <filetype name="PNG Images" pattern="*.png" />
            </filetypes>
        </filechooserentry>>
        <geometry>
            <pack for='filechooser1' />
        </geometry>
    </root>

For the declarative approach, the action attribute accepts the following values:

 * open
 * open-multiple
 * save
 * select-folder

"""

import sys
from enum import Enum
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename, askdirectory, asksaveasfilename
from tkinter.filedialog import askopenfilenames


class FileChooserAction(Enum):
    """File chooser actions (OPEN, OPEN_MULTIPLE, SAVE or SELECT_FOLDER)"""
    OPEN = 'open'
    OPEN_MULTIPLE = 'open-multiple'
    SAVE = 'save'
    SELECT_FOLDER = 'select-folder'


class FileChooserEntry(ttk.Frame):
    """File chooser for open, save as and path select operations.
    
       The chosen path can be accessed either through the :code:`get` method or
       by a Tk StringVar via the *textvariable* option.

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
        action (FileChooserAction): OPEN, SAVE, SELECT_FOLDER or OPEN_MULTIPLE
        buttontext (str): Text for the "Choose" button
        dialogtitle (str): Dialog window title
        textvariable (object): Tk :class:`StringVar` used to store the filepath
        filetypes (list): File types (applies only to OPEN, OPEN_MULTIPLE or 
            SAVE actions). If omitted, defaults to [('All files', '*.*')]
        kw (dict): Other keywords arguments (:class:`Frame` widget options)

    """

    def __init__(self, master=None, textvariable=None, buttontext='Choose...',
                 dialogtitle='Choose...', action=FileChooserAction.OPEN, **kw):
        if 'filetypes' in kw:
            self._filetypes = kw['filetypes']
            kw.pop('filetypes', False)
        else:
            self._filetypes = [('All files', '*.*')]
        ttk.Frame.__init__(self, master, **kw)
        # Variables
        self._var_entry = tk.StringVar()
        self._entrycbname = self._var_entry.trace_add('write', 
            self._update_from_entry_edit)
        self._var = textvariable if textvariable else tk.StringVar(value='')
        self._dialogtitle = dialogtitle
        self._action = action
        # Widgets
        self._entry = ttk.Entry(self)
        self._entry['textvariable'] = self._var_entry
        self._entry['width'] = 30
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self._button = ttk.Button(self, text=buttontext)
        self._button['command'] = self._choose
        self._button.pack(side=tk.LEFT)
        self._maincbname = self._var.trace_add('write', self._update)

    # =====================================================================            
    # Introspection
    # =====================================================================

    widget_keys = {
        'action': FileChooserAction,
        'buttontext': str, 
        'dialogtitle': str, 
        'filetypes': list,
        'textvariable': tk.StringVar
    }


    # =====================================================================            
    # Protected Methods
    # =====================================================================

    def _update(self, event=None, *args):
        """Update label (and scroll to the end)"""
        text = self._var.get()
        if sys.platform == 'win32':
            text = text.replace('/', '\\')
        # Preventing callback
        self._var_entry.trace_remove('write', self._entrycbname)
        self._var_entry.set(text)
        # Restoring callback
        self._entrycbname = self._var_entry.trace_add('write', 
            self._update_from_entry_edit)
        self._entry.xview('end')
        self._entry.update()

    def _update_from_entry_edit(self, *args):
        self._var.set(self._var_entry.get())

    def _choose(self):
        """Choose button callback."""
        enum_ = FileChooserAction
        if self._action in (enum_.OPEN, enum_.OPEN.value):
            path = askopenfilename(parent=self, filetypes=self._filetypes,
                                   title=self._dialogtitle)
        elif self._action in (enum_.SAVE, enum_.SAVE.value):
            path = asksaveasfilename(parent=self, filetypes=self._filetypes,
                                     title=self._dialogtitle)
        elif self._action in (enum_.OPEN_MULTIPLE, enum_.OPEN_MULTIPLE.value):
            paths = askopenfilenames(parent=self, filetypes=self._filetypes,
                                     title=self._dialogtitle)
            path = ':'.join(paths)
        else:
            path = askdirectory(parent=self, title=self._dialogtitle)
        self._var.set(path)
        self._update()
        self.event_generate('<<FilePathChanged>>')

    def _change_variable(self, new_value):
        self._var.trace_remove('write', self._maincbname)
        self._var = new_value
        self._maincbname = self._var.trace_add('write', self._update)
        self._update()

    # =====================================================================            
    # Properties
    # =====================================================================

    @property
    def button(self):
        """The Choose button."""
        return self._button

    @property
    def entry(self):
        """The entry displaying the selected filename."""
        return self._entry

    def get(self):
        """Gets the current selected file path."""
        return self._var.get()

    # =====================================================================
    # Inherited Methods
    # =====================================================================

    def __setitem__(self, key, val):
        if key == 'textvariable':
            self._change_variable(val)
        elif key == 'buttontext':
            self._button['text'] = val
        elif key in ('filetypes', 'dialogtitle', 'action'):
            self.__setattr__('_' + key, val)
        else:
            ttk.Frame.__setitem__(self, key, val)

    def __getitem__(self, key):
        if key == 'textvariable':
            return self._var
        elif key == 'buttontext':
            return self._button['text']
        elif key in ('filetypes', 'dialogtitle', 'action'):
            return self.__getattr__('_' + key)
        else:
            return ttk.Frame.__getitem__(self, key)

    def config(self, **kw):
        """Tk standard config method"""
        if 'textvariable' in kw:
            self._change_variable(kw['textvariable'])
            kw.pop('textvariable', False)
        if 'buttontext' in kw:
            self._button['text'] = kw['buttontext']
            kw.pop('buttontext', False)
        base_kw = {}
        for key in kw:
            if key in ('filetypes', 'dialogtitle', 'action'):
                self.__setattr__('_' + key, kw[key])
            else:
                base_kw[key] = kw[key]
        ttk.Frame.config(self, **base_kw)


# =====================================================================            
# Module DocTest
# =====================================================================

if __name__ == '__main__':
    import doctest
    doctest.testmod()

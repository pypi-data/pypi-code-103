"""TkBuilder GUI Application with a window title and the default witkets style.

One typical usage is to inherit the Application class and implement 
solution-specific methods.

A minimalist example without inheritance is given below:

    >>> import witkets as wtk
    >>> app = wtk.Application(ui_filename='demo.xml', title='Demo')
    >>> mainwindow = app.root # tk.Tk instance
    >>> builder = app.builder # TkBuilder instance
    >>> app.run()             # call app.root.mainloop()

"""

import tkinter as tk
import witkets as wtk

class Application:
    """A GUI Application.

    Parameters:
        ui_filename (str): path to the XML used by TkBuilder

    Keyword Arguments:
        title (str): window title
        theme (str): theme name
        kw (dict): Any of the :class:`tk.Tk` keyword arguments
    """
    def __init__(self, ui_filename=None, title=None, theme=None, **kw):

        self.root = tk.Tk()
        if title:
            self.root.title(title)
        style = wtk.Style()
        style.set_default_fonts()
        if theme:
            style.theme_use(theme)
        self.builder = wtk.TkBuilder(self.root)
        self.builder.build_from_file(ui_filename)
        style.apply_default()

    def run(self):
        """Enter the application event loop."""
        self.root.mainloop()
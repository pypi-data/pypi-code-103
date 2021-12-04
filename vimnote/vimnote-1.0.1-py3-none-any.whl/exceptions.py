# everything here mostly exists for communication between main.py tableview instances

class ExitException(Exception):
    pass

class OpenBookException(Exception):
    def __init__(self, title):
        super().__init__(self)
        self.title = title

class CloseBookException(Exception):
    pass

class EditNoteException(Exception):
    def __init__(self, book, title):
        super().__init__(self)
        self.book = book
        self.title = title

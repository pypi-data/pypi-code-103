from . import errors


class Element:
    '''
    Base of all OpenTraining artifacts (Topic, Exercise, Task, Person, ...)

    '''
    def __init__(self, title, path, docname, userdata):
        ''':param title: string that is sometimes (?) displayed somewhere (?)

        :param docname: leaks out from sphinx/docutils. Sometimes (?)
        used to display error messages. Should be removed in favor of
        ``userdata``

        :param userdata: during sphinx/docutils processing, we try to
        create OpenTraining elements as early as possible while
        keeping reference to the original docutils elements. For
        debugging and error messages only.

        :param path: the requested path across the hierarchy that this
        element should be placed under. Note that the hierarchy is not
        yet in place when an Element is create - this is just a
        request for a later step: when the soup is committed, Group
        elements are created, and is that point where the ``path``
        argument is used to add this Element to a *parent* group.

        '''

        verify_is_path(path, userdata)

        self.title = title
        self.docname = docname
        self.userdata = userdata
        if path:
            self._requested_path = path
        else:   # root group; no parent
            self.parent = None

        # derived classes call super().resolve() which sets this
        self._resolve_called = False

    def __str__(self):
        c = self.resolved and 'resolved' or 'unresolved'
        return f'{str(type(self))}({self.path},{c})'

    @property
    def path(self):
        if hasattr(self, '_requested_path'):
            return self._requested_path
        if self.parent:
            return self.parent.path + [self.parent.element_name(self)]
        else:
            return []  # root

    @property
    def resolved(self):
        if hasattr(self, '_requested_path'):
            return False
        return self._resolve_called

    def resolve(self, soup):
        assert not self._resolve_called
        self._resolve_called = True


def is_path(path):
    if type(path) not in (list, tuple):
        return False
    for elem in path:
        if type(elem) is not str:
            return False
        if not elem.isidentifier():
            return False
    return True

def verify_is_path(path, userdata):
    if not is_path(path):
        raise errors.BadPath(f'Not a valid path: {repr(path)}', userdata=userdata)
